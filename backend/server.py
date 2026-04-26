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

from recommendation_engine import (
    lot_flavor_vector_compute, taste_vector_from_quiz,
    score_lot_for_consumer, editors_picks_sort_key
)

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


SEED_LOTS = [
    {
        "lot_id": "papayo-natural-8001", "handle": "papayo-natural",
        "title": "Papayo Natural Process", "producer": "Maria del Pilar Naranjo Giron",
        "farm": "Los Pinos", "region": "Tolima, Colombia",
        "process": "natural", "variety": "bourbon", "altitude_m": 1600,
        "roast_rec": "medium", "price": 30.00,
        "expected_flavor_tags": ["tropical", "berry", "caramel"],
        "tasting_notes": ["Golden Berry", "Cantaloupe", "Peach"],
        "image": "https://unchainedcoffee.com/cdn/shop/files/Papayo_Natural_Process_Maria_del_Pilar_Naranjo.png?v=1770848927&width=800",
        "quantity_available": 50, "is_published": True,
        "metadata_completeness": 90, "farmer_payout_recorded": True,
        "reorder_definite_count": 3, "quantity_pct_remaining": 80,
        "reviews": [{"rating": 4.5}, {"rating": 4.0}, {"rating": 5.0}],
        "ideal_for": "Pour Over",
        "sensory": {"aroma": 7, "flavor": 8, "aftertaste": 7, "acidity": 6, "sweetness": 8, "mouthfeel": 7},
    },
    {
        "lot_id": "geisha-honey-8002", "handle": "geisha-honey",
        "title": "Geisha Honey Process", "producer": "Maria del Pilar Naranjo Giron",
        "farm": "Los Pinos", "region": "Tolima, Colombia",
        "process": "honey", "variety": "geisha", "altitude_m": 1600,
        "roast_rec": "light-medium", "price": 35.00,
        "expected_flavor_tags": ["floral", "tropical", "citrus", "tea-like"],
        "tasting_notes": ["Lemongrass", "Pineapple", "Starfruit"],
        "image": "https://unchainedcoffee.com/cdn/shop/files/Geisha_Honey_Process_Maria_del_Pilar_Naranjo.png?v=1770849019&width=800",
        "quantity_available": 30, "is_published": True,
        "metadata_completeness": 95, "farmer_payout_recorded": True,
        "reorder_definite_count": 5, "quantity_pct_remaining": 60,
        "reviews": [{"rating": 5.0}, {"rating": 4.8}, {"rating": 4.5}, {"rating": 5.0}],
        "ideal_for": "Pour Over",
        "sensory": {"aroma": 8, "flavor": 9, "aftertaste": 8, "acidity": 7, "sweetness": 8, "mouthfeel": 6},
    },
    {
        "lot_id": "red-bourbon-8003", "handle": "red-bourbon-semi-washed",
        "title": "Red Bourbon Semi-Washed", "producer": "Maria del Pilar Naranjo Giron",
        "farm": "Los Pinos", "region": "Tolima, Colombia",
        "process": "semi-washed", "variety": "bourbon", "altitude_m": 1600,
        "roast_rec": "medium", "price": 25.00,
        "expected_flavor_tags": ["berry", "chocolate", "caramel"],
        "tasting_notes": ["Red Fruits", "White Chocolate", "Caramel"],
        "image": "https://unchainedcoffee.com/cdn/shop/files/Red_Bourbon_Semi_Washed_Maria_del_Pilar_Naranjo.png?v=1770849552&width=800",
        "quantity_available": 70, "is_published": True,
        "metadata_completeness": 85, "farmer_payout_recorded": True,
        "reorder_definite_count": 2, "quantity_pct_remaining": 90,
        "reviews": [{"rating": 4.2}, {"rating": 4.0}, {"rating": 3.8}],
        "ideal_for": "Espresso",
        "sensory": {"aroma": 7, "flavor": 7, "aftertaste": 7, "acidity": 5, "sweetness": 7, "mouthfeel": 8},
    },
    {
        "lot_id": "caturra-washed-8004", "handle": "caturra-washed",
        "title": "Caturra Washed", "producer": "Carlos Eduardo Meza",
        "farm": "El Mirador", "region": "Huila, Colombia",
        "process": "washed", "variety": "caturra", "altitude_m": 1850,
        "roast_rec": "light", "price": 28.00,
        "expected_flavor_tags": ["floral", "citrus", "tea-like"],
        "tasting_notes": ["Green Apple", "Jasmine", "Honey"],
        "image": "https://unchainedcoffee.com/cdn/shop/files/Papayo_Natural_Process_Maria_del_Pilar_Naranjo.png?v=1770848927&width=800",
        "quantity_available": 40, "is_published": True,
        "metadata_completeness": 80, "farmer_payout_recorded": True,
        "reorder_definite_count": 1, "quantity_pct_remaining": 70,
        "reviews": [{"rating": 4.3}, {"rating": 4.5}],
        "ideal_for": "Pour Over",
        "sensory": {"aroma": 8, "flavor": 7, "aftertaste": 6, "acidity": 8, "sweetness": 6, "mouthfeel": 5},
    },
    {
        "lot_id": "tabi-anaerobic-8005", "handle": "tabi-anaerobic",
        "title": "Tabi Anaerobic Fermentation", "producer": "Luz Marina Torres",
        "farm": "La Esperanza", "region": "Narino, Colombia",
        "process": "anaerobic natural", "variety": "tabi", "altitude_m": 2100,
        "roast_rec": "medium-light", "price": 42.00,
        "expected_flavor_tags": ["berry", "chocolate", "funky", "spicy"],
        "tasting_notes": ["Blueberry", "Wine", "Dark Chocolate"],
        "image": "https://unchainedcoffee.com/cdn/shop/files/Geisha_Honey_Process_Maria_del_Pilar_Naranjo.png?v=1770849019&width=800",
        "quantity_available": 20, "is_published": True,
        "metadata_completeness": 75, "farmer_payout_recorded": False,
        "reorder_definite_count": 1, "quantity_pct_remaining": 40,
        "reviews": [{"rating": 4.7}, {"rating": 5.0}, {"rating": 4.2}],
        "ideal_for": "Pour Over",
        "sensory": {"aroma": 9, "flavor": 9, "aftertaste": 8, "acidity": 5, "sweetness": 7, "mouthfeel": 8},
    },
    {
        "lot_id": "castillo-dark-8006", "handle": "castillo-dark",
        "title": "Castillo Dark Roast", "producer": "Familia Ospina",
        "farm": "San Rafael", "region": "Quindio, Colombia",
        "process": "washed", "variety": "castillo", "altitude_m": 1450,
        "roast_rec": "dark", "price": 22.00,
        "expected_flavor_tags": ["chocolate", "nutty", "caramel"],
        "tasting_notes": ["Dark Chocolate", "Brown Sugar", "Walnut"],
        "image": "https://unchainedcoffee.com/cdn/shop/files/Red_Bourbon_Semi_Washed_Maria_del_Pilar_Naranjo.png?v=1770849552&width=800",
        "quantity_available": 100, "is_published": True,
        "metadata_completeness": 70, "farmer_payout_recorded": True,
        "reorder_definite_count": 4, "quantity_pct_remaining": 95,
        "reviews": [{"rating": 3.8}, {"rating": 4.0}, {"rating": 4.2}],
        "ideal_for": "Espresso",
        "sensory": {"aroma": 6, "flavor": 6, "aftertaste": 8, "acidity": 3, "sweetness": 5, "mouthfeel": 9},
    },
]


async def seed_lots():
    for lot in SEED_LOTS:
        existing = await db.lots.find_one({"lot_id": lot["lot_id"]})
        if not existing:
            await db.lots.insert_one({**lot, "created_at": datetime.now(timezone.utc).isoformat()})
        else:
            await db.lots.update_one({"lot_id": lot["lot_id"]}, {"$set": lot})


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
    await db.lots.create_index("lot_id", unique=True, sparse=True)
    await db.lots.create_index("is_published")
    await db.consumer_quiz_profiles.create_index("session_id", unique=True, sparse=True)
    await seed_admin()
    await seed_lots()
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


class QuizBody(BaseModel):
    session_id: str
    consumer_id: Optional[str] = None
    acidity_pref: float = Field(ge=1, le=5)
    bitterness_pref: float = Field(ge=1, le=5)
    body_pref: str
    roast_pref: str
    budget_band: str
    brew_methods: List[str] = []
    drink_style: str = "black"
    flavor_love_tags: List[str] = []
    consent_analytics: bool = True
    consent_marketing: bool = False

    @field_validator("body_pref")
    @classmethod
    def validate_body(cls, v):
        if v not in ("light", "tea-like", "balanced", "thick", "creamy"):
            raise ValueError("body_pref must be light/tea-like/balanced/thick/creamy")
        return v

    @field_validator("budget_band")
    @classmethod
    def validate_budget(cls, v):
        if v not in ("under_15", "15_20", "20_30", "30_plus"):
            raise ValueError("budget_band must be under_15/15_20/20_30/30_plus")
        return v


class RecommendationRequest(BaseModel):
    session_id: str
    limit: int = Field(6, ge=1, le=20)


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


# ============================================================
# PUBLIC: TASTE QUIZ
# ============================================================

@app.post("/api/quiz/submit")
async def submit_quiz(body: QuizBody):
    if not check_rate_limit(f"quiz:{body.session_id}"):
        raise HTTPException(429, "Rate limit exceeded")

    now = datetime.now(timezone.utc).isoformat()
    quiz_data = {
        "session_id": body.session_id,
        "consumer_id": body.consumer_id,
        "acidity_pref": body.acidity_pref,
        "bitterness_pref": body.bitterness_pref,
        "body_pref": body.body_pref,
        "roast_pref": body.roast_pref,
        "budget_band": body.budget_band,
        "brew_methods": body.brew_methods,
        "drink_style": body.drink_style,
        "flavor_love_tags": body.flavor_love_tags,
        "consent_analytics": body.consent_analytics,
        "consent_marketing": body.consent_marketing,
        "updated_at": now,
    }

    await db.consumer_quiz_profiles.update_one(
        {"session_id": body.session_id},
        {"$set": quiz_data, "$setOnInsert": {"quiz_id": str(uuid.uuid4())}},
        upsert=True
    )

    await emit_event("quiz_submitted", body.session_id,
                     consumer_id=body.consumer_id,
                     metadata={"roast_pref": body.roast_pref, "budget_band": body.budget_band,
                               "tag_count": len(body.flavor_love_tags)})

    return {"status": "ok"}


@app.get("/api/quiz/profile")
async def get_quiz_profile(session_id: str = Query(...)):
    profile = await db.consumer_quiz_profiles.find_one(
        {"session_id": session_id}, {"_id": 0}
    )
    if not profile:
        return {"profile": None}
    return {"profile": profile}


# ============================================================
# PUBLIC: RECOMMENDATIONS
# ============================================================

@app.post("/api/recommendations")
async def get_recommendations(body: RecommendationRequest):
    # Fetch quiz profile
    quiz = await db.consumer_quiz_profiles.find_one(
        {"session_id": body.session_id}, {"_id": 0}
    )

    # Fetch all published lots
    lots = await db.lots.find({"is_published": True}, {"_id": 0}).to_list(500)

    if not quiz:
        # Cold start: editor's picks
        lots.sort(key=editors_picks_sort_key)
        picks = lots[:body.limit]
        return {
            "mode": "editors_picks",
            "model_version": "rules_v1",
            "recommendations": [
                {
                    "lot": _lot_public(lot),
                    "score": None,
                    "explanation": ["A top-rated coffee from our collection"],
                    "components": None,
                }
                for lot in picks
            ],
            "quiz_completed": False,
        }

    # Full scoring
    consumer_vector = taste_vector_from_quiz(quiz)
    scored = []
    for lot in lots:
        result = score_lot_for_consumer(lot, consumer_vector)
        if result["eligible"]:
            scored.append({"lot": lot, **result})

    scored.sort(key=lambda x: x["score"], reverse=True)
    top = scored[:body.limit]

    return {
        "mode": "personalized",
        "model_version": "rules_v1",
        "recommendations": [
            {
                "lot": _lot_public(item["lot"]),
                "score": item["score"],
                "explanation": item["explanation"],
                "components": item["components"] if quiz.get("consent_analytics") else None,
            }
            for item in top
        ],
        "quiz_completed": True,
    }


def _lot_public(lot):
    """Strip internal fields for public API response."""
    return {
        "lot_id": lot.get("lot_id"),
        "handle": lot.get("handle"),
        "title": lot.get("title"),
        "producer": lot.get("producer"),
        "farm": lot.get("farm"),
        "region": lot.get("region"),
        "process": lot.get("process"),
        "variety": lot.get("variety"),
        "altitude_m": lot.get("altitude_m"),
        "roast_rec": lot.get("roast_rec"),
        "price": lot.get("price"),
        "image": lot.get("image"),
        "tasting_notes": lot.get("tasting_notes", []),
        "expected_flavor_tags": lot.get("expected_flavor_tags", []),
        "ideal_for": lot.get("ideal_for"),
        "sensory": lot.get("sensory"),
    }


# ============================================================
# PUBLIC: LOT DETAILS
# ============================================================

@app.get("/api/lots")
async def list_lots():
    lots = await db.lots.find({"is_published": True}, {"_id": 0}).to_list(500)
    return {"lots": [_lot_public(lot) for lot in lots]}


@app.get("/api/lots/{lot_id}")
async def get_lot(lot_id: str):
    lot = await db.lots.find_one({"lot_id": lot_id}, {"_id": 0})
    if not lot:
        raise HTTPException(404, "Lot not found")
    return {"lot": _lot_public(lot)}
