import os
import uuid
import html
import re
import csv
import io
from datetime import datetime, timezone, timedelta
from typing import Optional, List
from contextlib import asynccontextmanager
from collections import defaultdict

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException, Depends, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field, field_validator
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from jose import jwt, JWTError

MONGO_URL = os.environ.get("MONGO_URL")
DB_NAME = os.environ.get("DB_NAME")
JWT_SECRET = os.environ.get("JWT_SECRET")
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
rate_limits = {}

client = None
db = None


async def seed_admin():
    existing = await db.admin_users.find_one({"email": ADMIN_EMAIL})
    if not existing:
        await db.admin_users.insert_one({
            "user_id": str(uuid.uuid4()),
            "email": ADMIN_EMAIL,
            "password_hash": pwd_context.hash(ADMIN_PASSWORD),
            "role": "admin",
            "created_at": datetime.now(timezone.utc).isoformat()
        })
        await db.admin_users.insert_one({
            "user_id": str(uuid.uuid4()),
            "email": "viewer@unchainedcoffee.com",
            "password_hash": pwd_context.hash("viewer2025"),
            "role": "viewer",
            "created_at": datetime.now(timezone.utc).isoformat()
        })


@asynccontextmanager
async def lifespan(app: FastAPI):
    global client, db
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    await db.events.create_index([("session_id", 1)])
    await db.events.create_index([("product_id", 1), ("event_time", 1)])
    await db.events.create_index([("event_name", 1), ("event_time", 1)])
    await db.consumer_taste_profiles.create_index("session_id", unique=True, sparse=True)
    await db.consumer_taste_profiles.create_index("consumer_id", sparse=True)
    await db.consumer_taste_profiles.create_index("updated_at")
    await db.product_affective_responses.create_index([("product_id", 1), ("created_at", 1)])
    await db.product_affective_responses.create_index([("session_id", 1), ("created_at", 1)])
    await db.product_affective_responses.create_index([("consumer_id", 1), ("created_at", 1)])
    await seed_admin()
    yield
    client.close()


app = FastAPI(title="Unchained Coffee Taste Fit API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Pydantic Models ---

class ProfileBody(BaseModel):
    session_id: str
    consumer_id: Optional[str] = None
    aroma_pref_1to9: int = Field(ge=1, le=9)
    flavor_pref_1to9: int = Field(ge=1, le=9)
    aftertaste_pref_1to9: int = Field(ge=1, le=9)
    acidity_pref_1to9: int = Field(ge=1, le=9)
    sweetness_pref_1to9: int = Field(ge=1, le=9)
    mouthfeel_pref_1to9: int = Field(ge=1, le=9)
    consent_analytics: bool = True
    consent_marketing: bool = False


class ResponseBody(BaseModel):
    session_id: str
    consumer_id: Optional[str] = None
    product_id: str
    variant_id: Optional[str] = None
    mode: str
    aroma_1to9: Optional[int] = Field(None, ge=1, le=9)
    flavor_1to9: Optional[int] = Field(None, ge=1, le=9)
    aftertaste_1to9: Optional[int] = Field(None, ge=1, le=9)
    acidity_1to9: Optional[int] = Field(None, ge=1, le=9)
    sweetness_1to9: Optional[int] = Field(None, ge=1, le=9)
    mouthfeel_1to9: Optional[int] = Field(None, ge=1, le=9)
    overall_liking_1to9: Optional[int] = Field(None, ge=1, le=9)
    notes: Optional[str] = None
    standout_tags: Optional[List[str]] = None
    standout_tags_source: Optional[str] = None
    fit_tags: Optional[List[str]] = None
    consent_analytics: bool = True
    consent_marketing: bool = False

    @field_validator("mode")
    @classmethod
    def validate_mode(cls, v):
        if v not in ("preference_only", "tasted"):
            raise ValueError("mode must be preference_only or tasted")
        return v

    @field_validator("notes")
    @classmethod
    def sanitize_notes(cls, v):
        if v:
            v = re.sub(r'<[^>]+>', '', v)
            v = html.escape(v.strip())[:280]
        return v

    @field_validator("standout_tags")
    @classmethod
    def limit_tags(cls, v):
        if v and len(v) > 5:
            raise ValueError("Max 5 standout tags")
        return v


class EventBody(BaseModel):
    event_name: str
    session_id: str
    product_id: Optional[str] = None
    variant_id: Optional[str] = None
    metadata: Optional[dict] = None


class LoginBody(BaseModel):
    email: str
    password: str


class TasteFitScoreBody(BaseModel):
    session_id: str
    product_sensory: dict


class TasteFitBatchBody(BaseModel):
    session_id: str
    products: List[dict]


# --- Helpers ---

def check_rate_limit(key: str, max_per_day: int = 10) -> bool:
    now = datetime.now(timezone.utc)
    if key not in rate_limits:
        rate_limits[key] = {"count": 1, "reset": now}
        return True
    entry = rate_limits[key]
    if (now - entry["reset"]).total_seconds() > 86400:
        rate_limits[key] = {"count": 1, "reset": now}
        return True
    if entry["count"] >= max_per_day:
        return False
    entry["count"] += 1
    return True


async def verify_admin_token(request: Request):
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(401, "Missing auth token")
    try:
        payload = jwt.decode(auth[7:], JWT_SECRET, algorithms=["HS256"])
        user = await db.admin_users.find_one({"user_id": payload["user_id"]}, {"_id": 0})
        if not user:
            raise HTTPException(401, "User not found")
        return user
    except JWTError:
        raise HTTPException(401, "Invalid token")


async def require_admin_role(request: Request):
    user = await verify_admin_token(request)
    if user["role"] != "admin":
        raise HTTPException(403, "Admin role required")
    return user


async def emit_event(name, session_id, product_id=None, variant_id=None, consumer_id=None, metadata=None):
    await db.events.insert_one({
        "event_id": str(uuid.uuid4()),
        "event_name": name,
        "event_time": datetime.now(timezone.utc).isoformat(),
        "actor_type": "consumer",
        "session_id": session_id,
        "consumer_id": consumer_id,
        "source": "web",
        "product_id": product_id,
        "variant_id": variant_id,
        "metadata": metadata or {}
    })


# --- Health ---

@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "taste-fit-api"}


# --- Auth ---

@app.post("/api/auth/login")
async def login(body: LoginBody):
    user = await db.admin_users.find_one({"email": body.email}, {"_id": 0})
    if not user or not pwd_context.verify(body.password, user["password_hash"]):
        raise HTTPException(401, "Invalid credentials")
    token = jwt.encode({
        "user_id": user["user_id"],
        "email": user["email"],
        "role": user["role"],
        "exp": datetime.now(timezone.utc) + timedelta(hours=24)
    }, JWT_SECRET, algorithm="HS256")
    return {"token": token, "email": user["email"], "role": user["role"]}


# --- Public: Taste Profile ---

@app.post("/api/affective/profile")
async def upsert_profile(body: ProfileBody):
    if not check_rate_limit(f"profile:{body.session_id}"):
        raise HTTPException(429, "Rate limit exceeded")

    now = datetime.now(timezone.utc).isoformat()
    existing = await db.consumer_taste_profiles.find_one(
        {"session_id": body.session_id}, {"_id": 0}
    )

    profile_data = {
        "session_id": body.session_id,
        "consumer_id": body.consumer_id,
        "aroma_pref_1to9": body.aroma_pref_1to9,
        "flavor_pref_1to9": body.flavor_pref_1to9,
        "aftertaste_pref_1to9": body.aftertaste_pref_1to9,
        "acidity_pref_1to9": body.acidity_pref_1to9,
        "sweetness_pref_1to9": body.sweetness_pref_1to9,
        "mouthfeel_pref_1to9": body.mouthfeel_pref_1to9,
        "consent_analytics": body.consent_analytics,
        "consent_marketing": body.consent_marketing,
        "updated_at": now
    }

    profile_id = existing.get("profile_id") if existing else str(uuid.uuid4())

    result = await db.consumer_taste_profiles.update_one(
        {"session_id": body.session_id},
        {"$set": profile_data, "$setOnInsert": {"profile_id": profile_id}},
        upsert=True
    )

    if existing:
        pref_fields = ["aroma_pref_1to9", "flavor_pref_1to9", "aftertaste_pref_1to9",
                       "acidity_pref_1to9", "sweetness_pref_1to9", "mouthfeel_pref_1to9"]
        fields_changed = [f for f in pref_fields if existing.get(f) != profile_data[f]]
        consent_changed = (existing.get("consent_analytics") != body.consent_analytics or
                          existing.get("consent_marketing") != body.consent_marketing)
        if fields_changed:
            await emit_event("taste_profile_updated", body.session_id,
                           consumer_id=body.consumer_id,
                           metadata={"fields_changed": fields_changed})
        if consent_changed:
            await emit_event("consent_updated", body.session_id,
                           consumer_id=body.consumer_id,
                           metadata={"consent_analytics": body.consent_analytics,
                                    "consent_marketing": body.consent_marketing})
    else:
        await emit_event("taste_profile_updated", body.session_id,
                       consumer_id=body.consumer_id,
                       metadata={"fields_changed": ["all"], "is_new": True})

    return {"status": "ok", "profile_id": profile_id}


@app.get("/api/affective/profile")
async def get_profile(session_id: str = Query(...)):
    profile = await db.consumer_taste_profiles.find_one(
        {"session_id": session_id}, {"_id": 0}
    )
    if not profile:
        return {"profile": None}
    return {"profile": profile}


# --- Public: Affective Response ---

@app.post("/api/affective/response")
async def create_response(body: ResponseBody):
    if not check_rate_limit(f"response:{body.session_id}"):
        raise HTTPException(429, "Rate limit exceeded")

    if body.mode == "tasted":
        required = ["aroma_1to9", "flavor_1to9", "aftertaste_1to9",
                     "acidity_1to9", "sweetness_1to9", "mouthfeel_1to9", "overall_liking_1to9"]
        for field in required:
            if getattr(body, field) is None:
                raise HTTPException(422, f"Field {field} required in tasted mode")

    now = datetime.now(timezone.utc).isoformat()
    response_data = {
        "response_id": str(uuid.uuid4()),
        "session_id": body.session_id,
        "consumer_id": body.consumer_id,
        "product_id": body.product_id,
        "variant_id": body.variant_id,
        "mode": body.mode,
        "aroma_1to9": body.aroma_1to9,
        "flavor_1to9": body.flavor_1to9,
        "aftertaste_1to9": body.aftertaste_1to9,
        "acidity_1to9": body.acidity_1to9,
        "sweetness_1to9": body.sweetness_1to9,
        "mouthfeel_1to9": body.mouthfeel_1to9,
        "overall_liking_1to9": body.overall_liking_1to9,
        "notes": body.notes,
        "standout_tags": body.standout_tags,
        "standout_tags_source": body.standout_tags_source,
        "fit_tags": body.fit_tags,
        "consent_analytics": body.consent_analytics,
        "consent_marketing": body.consent_marketing,
        "created_at": now
    }

    await db.product_affective_responses.insert_one(response_data)

    await emit_event("affective_form_submitted", body.session_id,
                    product_id=body.product_id,
                    variant_id=body.variant_id,
                    consumer_id=body.consumer_id,
                    metadata={
                        "mode": body.mode,
                        "has_notes": bool(body.notes),
                        "overall_liking_1to9": body.overall_liking_1to9,
                        "response_id": response_data["response_id"]
                    })

    return {"status": "ok", "response_id": response_data["response_id"]}


# --- Public: Events ---

@app.post("/api/events")
async def create_event(body: EventBody):
    if not check_rate_limit(f"event:{body.session_id}", max_per_day=50):
        raise HTTPException(429, "Rate limit exceeded")
    await emit_event(body.event_name, body.session_id,
                    product_id=body.product_id,
                    variant_id=body.variant_id,
                    metadata=body.metadata)
    return {"status": "ok"}


# --- Public: Taste-Fit Score ---

def compute_fit_score(profile, product_sensory):
    """Compute taste-fit score: how well a product matches user preferences."""
    attr_map = [
        ("aroma", "aroma_pref_1to9"),
        ("flavor", "flavor_pref_1to9"),
        ("aftertaste", "aftertaste_pref_1to9"),
        ("acidity", "acidity_pref_1to9"),
        ("sweetness", "sweetness_pref_1to9"),
        ("mouthfeel", "mouthfeel_pref_1to9"),
    ]
    breakdown = {}
    total = 0
    count = 0
    for sensory_key, pref_key in attr_map:
        pref = profile.get(pref_key)
        sensory = product_sensory.get(sensory_key)
        if pref is not None and sensory is not None:
            match = max(0, 1 - abs(pref - sensory) / 8)
            breakdown[sensory_key] = {
                "match": round(match * 100),
                "pref": pref,
                "product": sensory,
                "delta": sensory - pref,
            }
            total += match
            count += 1
    overall = round((total / max(count, 1)) * 100)
    # Apply slight curve to make scores more meaningful (avoid clustering at 75-90)
    curved = round(min(99, max(0, overall * 1.1 - 5)))
    label = "Perfect Match" if curved >= 90 else "Great Match" if curved >= 75 else "Good Fit" if curved >= 60 else "Decent Fit" if curved >= 45 else "Different Vibe"
    return {
        "score": curved,
        "raw_score": overall,
        "label": label,
        "breakdown": breakdown,
    }


@app.post("/api/affective/taste-fit")
async def taste_fit_score(body: TasteFitScoreBody):
    profile = await db.consumer_taste_profiles.find_one(
        {"session_id": body.session_id}, {"_id": 0}
    )
    if not profile:
        return {"profile_exists": False, "score": None}
    result = compute_fit_score(profile, body.product_sensory)
    return {**result, "profile_exists": True}


@app.post("/api/affective/taste-fit/batch")
async def taste_fit_batch(body: TasteFitBatchBody):
    profile = await db.consumer_taste_profiles.find_one(
        {"session_id": body.session_id}, {"_id": 0}
    )
    if not profile:
        return {"profile_exists": False, "scores": []}
    scores = []
    for product in body.products:
        pid = product.get("product_id", "")
        sensory = product.get("sensory", {})
        result = compute_fit_score(profile, sensory)
        scores.append({"product_id": pid, **result})
    return {"profile_exists": True, "scores": scores}


# --- Admin: List Products ---

@app.get("/api/admin/products")
async def admin_list_products(
    request: Request,
    search: Optional[str] = None,
    user=Depends(verify_admin_token)
):
    pipeline = [
        {"$group": {
            "_id": "$product_id",
            "count": {"$sum": 1},
            "last_response": {"$max": "$created_at"},
            "modes": {"$addToSet": "$mode"}
        }},
        {"$sort": {"last_response": -1}}
    ]
    products = await db.product_affective_responses.aggregate(pipeline).to_list(1000)
    result = []
    for p in products:
        pid = p["_id"] or ""
        if search and search.lower() not in pid.lower():
            continue
        result.append({
            "product_id": pid,
            "response_count": p["count"],
            "last_response": p["last_response"],
            "modes": p["modes"]
        })
    return {"products": result}


# --- Admin: Product Summary ---

@app.get("/api/admin/products/summary")
async def admin_product_summary(
    request: Request,
    product_id: Optional[str] = None,
    date_from: Optional[str] = Query(None, alias="from"),
    date_to: Optional[str] = Query(None, alias="to"),
    user=Depends(verify_admin_token)
):
    query = {}
    if product_id:
        query["product_id"] = product_id
    if date_from or date_to:
        date_q = {}
        if date_from:
            date_q["$gte"] = date_from
        if date_to:
            date_q["$lte"] = date_to
        query["created_at"] = date_q

    responses = await db.product_affective_responses.find(query, {"_id": 0}).to_list(10000)

    if not responses:
        return {"count": 0, "averages": {}, "distributions": {}, "standout_tags": {}, "fit_tags": {}, "notes_count": 0, "mode_breakdown": {}}

    attrs = ["aroma_1to9", "flavor_1to9", "aftertaste_1to9",
             "acidity_1to9", "sweetness_1to9", "mouthfeel_1to9", "overall_liking_1to9"]

    averages = {}
    distributions = {}
    for attr in attrs:
        values = [r[attr] for r in responses if r.get(attr) is not None]
        if values:
            averages[attr] = round(sum(values) / len(values), 2)
            dist = {str(i): 0 for i in range(1, 10)}
            for v in values:
                dist[str(v)] += 1
            distributions[attr] = dist

    tag_counts = defaultdict(int)
    fit_tag_counts = defaultdict(int)
    for r in responses:
        for t in (r.get("standout_tags") or []):
            tag_counts[t] += 1
        for t in (r.get("fit_tags") or []):
            fit_tag_counts[t] += 1

    notes_count = sum(1 for r in responses if r.get("notes"))
    mode_counts = defaultdict(int)
    for r in responses:
        mode_counts[r.get("mode", "unknown")] += 1

    return {
        "count": len(responses),
        "averages": averages,
        "distributions": distributions,
        "standout_tags": dict(tag_counts),
        "fit_tags": dict(fit_tag_counts),
        "notes_count": notes_count,
        "mode_breakdown": dict(mode_counts)
    }


# --- Admin: Segments ---

@app.get("/api/admin/segments")
async def admin_segments(
    request: Request,
    date_from: Optional[str] = Query(None, alias="from"),
    date_to: Optional[str] = Query(None, alias="to"),
    user=Depends(verify_admin_token)
):
    query = {}
    if date_from or date_to:
        date_q = {}
        if date_from:
            date_q["$gte"] = date_from
        if date_to:
            date_q["$lte"] = date_to
        query["updated_at"] = date_q

    profiles = await db.consumer_taste_profiles.find(query, {"_id": 0}).to_list(10000)
    attrs = ["aroma_pref_1to9", "flavor_pref_1to9", "aftertaste_pref_1to9",
             "acidity_pref_1to9", "sweetness_pref_1to9", "mouthfeel_pref_1to9"]

    segments = {}
    for attr in attrs:
        bands = {"low_1_3": 0, "mid_4_6": 0, "high_7_9": 0}
        for p in profiles:
            v = p.get(attr)
            if v is not None:
                if 1 <= v <= 3:
                    bands["low_1_3"] += 1
                elif 4 <= v <= 6:
                    bands["mid_4_6"] += 1
                elif 7 <= v <= 9:
                    bands["high_7_9"] += 1
        segments[attr] = bands

    return {"total_profiles": len(profiles), "segments": segments}


# --- Admin: Funnel ---

@app.get("/api/admin/funnel")
async def admin_funnel(
    request: Request,
    date_from: Optional[str] = Query(None, alias="from"),
    date_to: Optional[str] = Query(None, alias="to"),
    user=Depends(verify_admin_token)
):
    query = {}
    if date_from or date_to:
        date_q = {}
        if date_from:
            date_q["$gte"] = date_from
        if date_to:
            date_q["$lte"] = date_to
        query["event_time"] = date_q

    funnel_events = ["product_viewed", "affective_form_viewed", "affective_form_opened", "affective_form_submitted"]
    counts = {}
    for event_name in funnel_events:
        q = {**query, "event_name": event_name}
        count = await db.events.count_documents(q)
        counts[event_name] = count
    return {"funnel": counts}


# --- Admin: CSV Export ---

@app.get("/api/admin/export.csv")
async def admin_export_csv(
    request: Request,
    product_id: Optional[str] = None,
    date_from: Optional[str] = Query(None, alias="from"),
    date_to: Optional[str] = Query(None, alias="to"),
    user=Depends(require_admin_role)
):
    query = {}
    if product_id:
        query["product_id"] = product_id
    if date_from or date_to:
        date_q = {}
        if date_from:
            date_q["$gte"] = date_from
        if date_to:
            date_q["$lte"] = date_to
        query["created_at"] = date_q

    responses = await db.product_affective_responses.find(query, {"_id": 0}).to_list(50000)

    output = io.StringIO()
    fieldnames = ["response_id", "session_id", "consumer_id", "product_id", "variant_id",
                  "mode", "aroma_1to9", "flavor_1to9", "aftertaste_1to9", "acidity_1to9",
                  "sweetness_1to9", "mouthfeel_1to9", "overall_liking_1to9", "notes",
                  "standout_tags", "fit_tags", "consent_analytics", "consent_marketing", "created_at"]
    writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction='ignore')
    writer.writeheader()
    for r in responses:
        row = {**r}
        if row.get("standout_tags"):
            row["standout_tags"] = "|".join(row["standout_tags"])
        if row.get("fit_tags"):
            row["fit_tags"] = "|".join(row["fit_tags"])
        writer.writerow(row)

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=affective_responses.csv"}
    )


# --- Admin: Privacy Delete ---

@app.delete("/api/admin/data")
async def admin_delete_data(
    request: Request,
    session_id: Optional[str] = None,
    consumer_id: Optional[str] = None,
    user=Depends(require_admin_role)
):
    if not session_id and not consumer_id:
        raise HTTPException(400, "Provide session_id or consumer_id")

    query = {}
    if session_id:
        query["session_id"] = session_id
    if consumer_id:
        query["consumer_id"] = consumer_id

    profile_result = await db.consumer_taste_profiles.delete_many(query)
    response_result = await db.product_affective_responses.delete_many(query)
    event_result = await db.events.delete_many(query)

    await db.events.insert_one({
        "event_id": str(uuid.uuid4()),
        "event_name": "data_deleted",
        "event_time": datetime.now(timezone.utc).isoformat(),
        "actor_type": "internal_ops",
        "session_id": session_id or "",
        "consumer_id": consumer_id,
        "source": "web",
        "metadata": {
            "deleted_by": user["email"],
            "profiles_deleted": profile_result.deleted_count,
            "responses_deleted": response_result.deleted_count,
            "events_deleted": event_result.deleted_count
        }
    })

    return {
        "status": "ok",
        "deleted": {
            "profiles": profile_result.deleted_count,
            "responses": response_result.deleted_count,
            "events": event_result.deleted_count
        }
    }
