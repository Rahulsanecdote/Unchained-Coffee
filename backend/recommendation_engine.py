"""
Unchained Coffee — Rules-Based Recommendation Engine (rules_v1)
Taste Vector → Lot Scoring per spec.
"""

# ============================================================
# 1. PROXY TABLES
# ============================================================

PROCESS_PROFILES = {
    "washed":    {"acidity": (4, 5), "sweetness": (2, 3), "body": (2, 3), "funk": 1},
    "honey":     {"acidity": (3, 4), "sweetness": (3, 4), "body": (3, 4), "funk": 2},
    "natural":   {"acidity": (2, 3), "sweetness": (4, 5), "body": (4, 5), "funk": 3.5},
    "anaerobic": {"acidity": (2, 4), "sweetness": (3, 5), "body": (3, 5), "funk": 4.5},
    "anaerobic natural": {"acidity": (2, 4), "sweetness": (3, 5), "body": (3, 5), "funk": 4.5},
    "semi-washed": {"acidity": (3, 4), "sweetness": (3, 4), "body": (3, 4), "funk": 2},
}
PROCESS_DEFAULT = {"acidity": (3, 3), "sweetness": (3, 3), "body": (3, 3), "funk": 2}

VARIETY_PROFILES = {
    "gesha":    {"acidity": "high",         "body": "light-medium", "character": "Floral, jasmine, tea-like"},
    "geisha":   {"acidity": "high",         "body": "light-medium", "character": "Floral, jasmine, tea-like"},
    "sl28":     {"acidity": "high",         "body": "medium",       "character": "Blackcurrant, citrus"},
    "sl34":     {"acidity": "high",         "body": "medium",       "character": "Blackcurrant, citrus"},
    "bourbon":  {"acidity": "medium-high",  "body": "medium",       "character": "Caramel, red fruit, balanced"},
    "typica":   {"acidity": "medium",       "body": "light-medium", "character": "Clean, delicate, floral"},
    "caturra":  {"acidity": "medium-high",  "body": "light-medium", "character": "Citrus, clean, versatile"},
    "castillo": {"acidity": "medium",       "body": "medium",       "character": "Mild fruit, approachable"},
    "pacamara": {"acidity": "medium-high",  "body": "heavy",        "character": "Chocolate, complex, herbal"},
    "tabi":     {"acidity": "medium",       "body": "medium",       "character": "Mild fruit, balanced"},
    "colombia": {"acidity": "medium",       "body": "medium",       "character": "Balanced, versatile"},
}
VARIETY_DEFAULT = {"acidity": "medium", "body": "medium", "character": "Neutral proxy"}

BODY_TENDENCY_TO_MODIFIER = {
    "light": -0.5,
    "light-medium": 0,
    "medium": 0,
    "medium-heavy": 0.5,
    "heavy": 1.0,
}

ALTITUDE_MODIFIERS = [
    (0,    1200, -1.0),
    (1200, 1500,  0.0),
    (1500, 1800,  0.5),
    (1800, 2100,  1.0),
    (2100, 99999, 1.5),
]

ROAST_MATCH_MATRIX = {
    ("light", "light"): 5,       ("light", "medium"): 2,       ("light", "medium-dark"): 0,  ("light", "dark"): 0,
    ("medium", "light"): 2,      ("medium", "medium"): 5,      ("medium", "medium-dark"): 3, ("medium", "dark"): 1,
    ("dark", "light"): 0,        ("dark", "medium"): 3,        ("dark", "medium-dark"): 5,   ("dark", "dark"): 5,
    ("medium-light", "light"): 3,("medium-light", "medium"): 4,("medium-light", "medium-dark"): 1, ("medium-light", "dark"): 0,
    ("light-medium", "light"): 3,("light-medium", "medium"): 4,("light-medium", "medium-dark"): 1, ("light-medium", "dark"): 0,
}

BUDGET_BANDS = {
    "under_15": {"max": 15, "range": 15},
    "15_20":    {"max": 22, "range": 7},
    "20_30":    {"max": 33, "range": 13},
    "30_plus":  {"max": 9999, "range": 50},
}

BODY_PREF_TO_NUMERIC = {
    "light":    1.5,
    "tea-like": 1.5,
    "balanced": 3.0,
    "thick":    4.5,
    "creamy":   4.5,
}

DRINK_STYLE_BODY_MOD = {
    "black":      0,
    "with_milk":  0.5,
    "with_sugar": 0,
    "milk_sugar": 0.5,
    "depends":    0,
}

CANONICAL_TAGS = {"chocolate", "caramel", "nutty", "citrus", "berry", "tropical", "floral", "tea-like", "spicy", "funky"}

SCORE_WEIGHTS = {
    "acidity":    0.25,
    "bitterness": 0.15,
    "body":       0.15,
    "funk":       0.10,
    "tag":        0.20,
    "roast":      0.10,
    "budget":     0.05,
}

# ============================================================
# 2. HELPER FUNCTIONS
# ============================================================

def _clamp(v, lo=1.0, hi=5.0):
    return max(lo, min(hi, v))


def _midpoint(rng):
    if isinstance(rng, (tuple, list)):
        return (rng[0] + rng[1]) / 2
    return float(rng)


def _altitude_modifier(altitude_m):
    for lo, hi, mod in ALTITUDE_MODIFIERS:
        if lo <= altitude_m < hi:
            return mod
    return 0


def _normalize_process(process_str):
    return process_str.lower().strip() if process_str else "other"


def _normalize_variety(variety_str):
    return variety_str.lower().strip() if variety_str else "other"


def _normalize_roast(roast_str):
    return roast_str.lower().strip() if roast_str else "medium"


# ============================================================
# 3. LOT FLAVOR VECTOR
# ============================================================

def lot_flavor_vector_compute(lot):
    """Compute derived flavor vector from lot attributes."""
    process = _normalize_process(lot.get("process", "other"))
    variety = _normalize_variety(lot.get("variety", "other"))
    altitude_m = lot.get("altitude_m", 1500)
    roast = _normalize_roast(lot.get("roast_rec", lot.get("roast", "medium")))

    proc = PROCESS_PROFILES.get(process, PROCESS_DEFAULT)
    var_profile = VARIETY_PROFILES.get(variety, VARIETY_DEFAULT)

    # Acidity: process midpoint + altitude modifier
    lot_acidity = _clamp(_midpoint(proc["acidity"]) + _altitude_modifier(altitude_m))

    # Sweetness: from process
    lot_sweetness = _midpoint(proc["sweetness"])

    # Body: process midpoint + variety body modifier
    body_tendency = var_profile.get("body", "medium")
    body_mod = BODY_TENDENCY_TO_MODIFIER.get(body_tendency, 0)
    lot_body = _clamp(_midpoint(proc["body"]) + body_mod)

    # Funk: from process
    lot_funk = proc["funk"] if isinstance(proc["funk"], (int, float)) else _midpoint(proc["funk"])

    # Bitterness: inverse proxy of acidity
    lot_bitterness = _clamp(5 - lot_acidity)

    return {
        "acidity": round(lot_acidity, 2),
        "sweetness": round(lot_sweetness, 2),
        "body": round(lot_body, 2),
        "funk": round(lot_funk, 2),
        "bitterness": round(lot_bitterness, 2),
        "roast": roast,
        "variety_character": var_profile.get("character", ""),
    }


# ============================================================
# 4. TASTE VECTOR FROM QUIZ
# ============================================================

def taste_vector_from_quiz(quiz):
    """Convert consumer quiz responses into a normalized taste vector."""
    acidity_pref = float(quiz.get("acidity_pref", 3))
    bitterness_pref = float(quiz.get("bitterness_pref", 3))

    body_raw = quiz.get("body_pref", "balanced")
    body_pref = BODY_PREF_TO_NUMERIC.get(body_raw, 3.0)

    # Drink style modifier applied to body pref
    drink_style = quiz.get("drink_style", "black")
    body_pref = _clamp(body_pref + DRINK_STYLE_BODY_MOD.get(drink_style, 0))

    # Funk pref inferred from flavor_love_tags if not explicitly set
    flavor_tags = set(t.lower() for t in quiz.get("flavor_love_tags", []))
    if quiz.get("funk_pref") is not None:
        funk_pref = float(quiz["funk_pref"])
    elif "funky" in flavor_tags:
        funk_pref = 4.0
    elif "floral" in flavor_tags or "tea-like" in flavor_tags:
        funk_pref = 1.0
    elif "tropical" in flavor_tags or "berry" in flavor_tags:
        funk_pref = 2.5
    else:
        funk_pref = 2.0

    roast_pref = quiz.get("roast_pref", "not_sure")
    budget_band = quiz.get("budget_band", "20_30")
    brew_methods = quiz.get("brew_methods", [])

    return {
        "acidity_pref": _clamp(acidity_pref),
        "bitterness_pref": _clamp(bitterness_pref),
        "body_pref": body_pref,
        "funk_pref": _clamp(funk_pref),
        "roast_pref": _normalize_roast(roast_pref),
        "flavor_love_tags": flavor_tags,
        "budget_band": budget_band,
        "brew_methods": [b.lower() for b in brew_methods],
        "drink_style": drink_style,
    }


# ============================================================
# 5. SCORE_LOT_FOR_CONSUMER
# ============================================================

def _dimension_match(consumer_val, lot_val):
    """Delta → match score: MAX(0, 5 - delta * 1.5), clamped [0, 5]."""
    delta = abs(consumer_val - lot_val)
    return _clamp(5 - delta * 1.5, 0, 5)


def _tag_overlap_score(consumer_tags, lot_tags):
    """Matching tags × 2, max 5."""
    if not consumer_tags or not lot_tags:
        return 0
    matching = consumer_tags & set(t.lower() for t in lot_tags)
    return min(len(matching) * 2, 5)


def _roast_match_score(consumer_roast, lot_roast):
    """Roast pref → lot roast score from matrix."""
    if consumer_roast in ("not_sure", "not sure", "i'm not sure"):
        return 3
    if lot_roast in ("not_sure", "not sure"):
        return 3
    key = (consumer_roast, lot_roast)
    return ROAST_MATCH_MATRIX.get(key, 3)


def _budget_fit_score(lot_price, budget_band):
    band = BUDGET_BANDS.get(budget_band, BUDGET_BANDS["20_30"])
    if lot_price > band["max"]:
        return 0
    headroom = (band["max"] - lot_price) / max(band["range"], 1)
    if headroom >= 0.3:
        return 5
    return 3


def _check_hard_filters(lot, consumer_vector):
    """Returns (passes, reason) tuple."""
    if lot.get("quantity_available", 999) <= 0:
        return False, "out_of_stock"
    if not lot.get("is_published", True):
        return False, "not_published"
    band = BUDGET_BANDS.get(consumer_vector.get("budget_band", "20_30"), BUDGET_BANDS["20_30"])
    if lot.get("price", 0) > band["max"]:
        return False, "over_budget"
    return True, None


def score_lot_for_consumer(lot, consumer_vector, lot_vector=None, purchase_history=None):
    """
    Full scoring pipeline per spec.
    Returns: { score, raw_score, components, explanation, model_version, eligible }
    """
    # Step 0: Hard filters
    eligible, filter_reason = _check_hard_filters(lot, consumer_vector)
    if not eligible:
        return {
            "score": 0,
            "raw_score": 0,
            "components": {},
            "explanation": [],
            "model_version": "rules_v1",
            "eligible": False,
            "filter_reason": filter_reason,
        }

    # Step 1: Lot flavor vector
    if lot_vector is None:
        lot_vector = lot_flavor_vector_compute(lot)

    # Step 2: Dimension match scores
    acidity_match = _dimension_match(consumer_vector["acidity_pref"], lot_vector["acidity"])
    bitterness_match = _dimension_match(consumer_vector["bitterness_pref"], lot_vector["bitterness"])
    body_match = _dimension_match(consumer_vector["body_pref"], lot_vector["body"])
    funk_match = _dimension_match(consumer_vector["funk_pref"], lot_vector["funk"])

    # Step 3: Tag overlap
    lot_tags = set(t.lower() for t in lot.get("expected_flavor_tags", []))
    tag_score = _tag_overlap_score(consumer_vector["flavor_love_tags"], lot_tags)

    # Step 4: Roast match
    roast_score = _roast_match_score(consumer_vector["roast_pref"], lot_vector["roast"])

    # Step 5: Budget fit
    budget_score = _budget_fit_score(lot.get("price", 0), consumer_vector.get("budget_band", "20_30"))

    # Step 7: Weighted aggregation
    raw_score = (
        acidity_match    * SCORE_WEIGHTS["acidity"] +
        bitterness_match * SCORE_WEIGHTS["bitterness"] +
        body_match       * SCORE_WEIGHTS["body"] +
        funk_match       * SCORE_WEIGHTS["funk"] +
        tag_score        * SCORE_WEIGHTS["tag"] +
        roast_score      * SCORE_WEIGHTS["roast"] +
        budget_score     * SCORE_WEIGHTS["budget"]
    )
    normalized = round((raw_score / 5.0) * 100)

    # Step 8: Boost/Penalty
    adjustments = []
    reviews = lot.get("reviews", [])
    if len(reviews) >= 3:
        avg_rating = sum(r.get("rating", 0) for r in reviews) / len(reviews)
        if avg_rating >= 4.0:
            normalized += 5
            adjustments.append(("verified_reviews_boost", +5))

    reorder_count = lot.get("reorder_definite_count", 0)
    if reorder_count >= 2:
        normalized += 3
        adjustments.append(("reorder_intent_boost", +3))

    if purchase_history:
        for ph in purchase_history:
            if ph.get("lot_id") == lot.get("id") and ph.get("rating", 5) < 3:
                normalized -= 100
                adjustments.append(("negative_purchase_suppress", -100))

    quantity_pct = lot.get("quantity_pct_remaining", 100)
    if quantity_pct < 10:
        normalized -= 3
        adjustments.append(("low_stock_penalty", -3))

    if lot.get("farmer_payout_recorded"):
        normalized += 2
        adjustments.append(("farmer_payout_boost", +2))

    metadata_completeness = lot.get("metadata_completeness", 50)
    if metadata_completeness >= 80:
        normalized += 3
        adjustments.append(("metadata_quality_boost", +3))
    elif metadata_completeness < 40:
        normalized -= 5
        adjustments.append(("metadata_poor_penalty", -5))

    normalized = max(0, min(100, normalized))

    # Components for analytics
    components = {
        "acidity_match": round(acidity_match, 2),
        "bitterness_match": round(bitterness_match, 2),
        "body_match": round(body_match, 2),
        "funk_match": round(funk_match, 2),
        "tag_score": round(tag_score, 2),
        "roast_score": round(roast_score, 2),
        "budget_score": round(budget_score, 2),
        "raw_weighted": round(raw_score, 3),
        "adjustments": adjustments,
        "lot_vector": lot_vector,
    }

    # Generate explanation
    explanation = _generate_explanation(
        consumer_vector, lot_vector, lot,
        acidity_match, body_match, tag_score, roast_score, funk_match
    )

    return {
        "score": normalized,
        "raw_score": round(raw_score, 3),
        "components": components,
        "explanation": explanation,
        "model_version": "rules_v1",
        "eligible": True,
    }


# ============================================================
# 6. EXPLANATION GENERATOR
# ============================================================

def _generate_explanation(consumer, lot_vector, lot, acid_m, body_m, tag_s, roast_s, funk_m):
    """Generate 1-2 'Why recommended' attribute labels."""
    reasons = []

    # Collect matches sorted by strength
    matches = [
        (acid_m, "acidity"),
        (body_m, "body"),
        (funk_m, "funk"),
        (roast_s, "roast"),
    ]
    matches.sort(key=lambda x: x[0], reverse=True)

    # Best dimension match
    if matches[0][0] >= 4:
        dim = matches[0][1]
        if dim == "acidity":
            level = "bright" if lot_vector["acidity"] >= 3.5 else "mellow"
            reasons.append(f"Matches your love of {level} acidity")
        elif dim == "body":
            level = "full" if lot_vector["body"] >= 3.5 else "light"
            reasons.append(f"Aligns with your preference for {level}-bodied coffee")
        elif dim == "funk":
            if lot_vector["funk"] >= 3:
                reasons.append("Right amount of natural funk for your palate")
            else:
                reasons.append("Clean profile that matches your style")
        elif dim == "roast":
            reasons.append(f"The {lot_vector['roast']} roast is right in your zone")

    # Tag overlap
    consumer_tags = consumer.get("flavor_love_tags", set())
    lot_tags = set(t.lower() for t in lot.get("expected_flavor_tags", []))
    overlap = consumer_tags & lot_tags
    if overlap and len(reasons) < 2:
        tag_list = ", ".join(sorted(overlap)[:2])
        reasons.append(f"Features {tag_list} notes you enjoy")

    # Second dimension if only 1 reason so far
    if len(reasons) < 2 and matches[1][0] >= 3.5:
        dim = matches[1][1]
        if dim == "acidity" and "acidity" not in str(reasons):
            level = "bright" if lot_vector["acidity"] >= 3.5 else "smooth"
            reasons.append(f"Its {level} acidity complements your taste")
        elif dim == "body" and "body" not in str(reasons) and "bodied" not in str(reasons):
            level = "rich" if lot_vector["body"] >= 3.5 else "delicate"
            reasons.append(f"The {level} body suits your preferences")

    # Fallback
    if not reasons:
        reasons.append("A well-balanced coffee that aligns with your profile")

    return reasons[:2]


# ============================================================
# 7. COLD START (EDITOR'S PICKS)
# ============================================================

def editors_picks_sort_key(lot):
    """Sort for cold start: avg review DESC, metadata completeness DESC."""
    reviews = lot.get("reviews", [])
    avg_rating = sum(r.get("rating", 0) for r in reviews) / max(len(reviews), 1) if reviews else 3.0
    metadata = lot.get("metadata_completeness", 50)
    return (-avg_rating, -metadata)
