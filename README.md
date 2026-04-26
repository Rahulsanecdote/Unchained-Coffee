# Unchained Coffee — Taste Fit MVP v0

> A "Taste Fit" affective-form widget for Shopify PDPs + internal admin dashboard.  
> Collects customer taste preferences on a 1–9 scale, computes personalized match scores, and surfaces product-level insights for the ops team.

---

## Architecture

```
Frontend (React 18 + Tailwind 3)        Backend (FastAPI + Motor)
┌──────────────────────────┐             ┌──────────────────────────┐
│  Demo PDP / Collection   │  ── API ──▶ │  /api/affective/*        │
│  Taste Fit Widget        │             │  /api/events             │
│  Taste Fit Score Card    │             │  /api/auth/login         │
│  Admin Dashboard         │             │  /api/admin/*            │
└──────────────────────────┘             └──────────┬───────────────┘
                                                    │
                                                    ▼
                                            ┌───────────────┐
                                            │   MongoDB      │
                                            │  (4 collections│
                                            │   + indexes)   │
                                            └───────────────┘
```

| Layer     | Stack                                                |
|-----------|------------------------------------------------------|
| Frontend  | React 18, React Router 6, Tailwind CSS 3, Recharts   |
| Backend   | FastAPI, Motor (async MongoDB), Pydantic, python-jose |
| Database  | MongoDB (events, consumer_taste_profiles, product_affective_responses, admin_users) |
| Auth      | JWT (bcrypt-hashed passwords, admin/viewer roles)     |
| Identity  | Anonymous UUID session stored in localStorage         |

---

## Repo Structure

```
/app
├── backend/
│   ├── server.py              # FastAPI app — all routes in one file
│   ├── .env                   # Backend env vars (see below)
│   └── requirements.txt       # Python deps (pip freeze)
├── frontend/
│   ├── public/
│   │   └── index.html         # Shell with Google Fonts (Fraunces, Inter, JetBrains Mono)
│   ├── src/
│   │   ├── App.js             # React Router config
│   │   ├── index.js / index.css
│   │   ├── components/
│   │   │   ├── widget/
│   │   │   │   ├── TasteFitWidget.js    # Main widget (modes, scales, tags, submit)
│   │   │   │   ├── TasteFitScore.js     # Animated score ring + breakdown
│   │   │   │   ├── AffectiveScale.js    # 1–9 tappable-square scale
│   │   │   │   ├── TagChips.js          # Multi-select chip component
│   │   │   │   ├── BottomDrawer.js      # Mobile bottom-sheet
│   │   │   │   └── ConsentToggles.js    # Analytics/marketing toggles
│   │   │   └── admin/
│   │   │       └── AdminLayout.js       # Sidebar + auth guard
│   │   ├── pages/
│   │   │   ├── DemoPDP.js               # Simulated Shopify product page
│   │   │   ├── AdminLogin.js
│   │   │   ├── AdminProducts.js
│   │   │   ├── AdminProductDetail.js    # Distributions, averages, tags
│   │   │   ├── AdminFunnel.js
│   │   │   ├── AdminSegments.js
│   │   │   └── AdminPrivacy.js
│   │   ├── data/
│   │   │   └── mockProducts.js          # 6 demo coffees + canonical tags
│   │   ├── hooks/
│   │   │   └── useSessionId.js          # UUID session cookie
│   │   └── utils/
│   │       └── api.js                   # Fetch wrapper with retry + admin auth
│   ├── .env                   # Frontend env vars
│   ├── package.json
│   ├── tailwind.config.js
│   └── postcss.config.js
└── memory/
    └── PRD.md                 # Living product requirements doc
```

---

## Environment Variables

### `backend/.env`

```env
MONGO_URL=mongodb://localhost:27017
DB_NAME=unchained_coffee
JWT_SECRET=<random-secret>
ADMIN_EMAIL=admin@unchainedcoffee.com
ADMIN_PASSWORD=unchained2025
```

### `frontend/.env`

```env
REACT_APP_BACKEND_URL=http://localhost:8001
```

> In production / preview, `REACT_APP_BACKEND_URL` points to the deployed API domain.

---

## Local Setup

### Prerequisites
- Node.js 18+, Yarn
- Python 3.11+
- MongoDB running on `localhost:27017`

### 1. Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# copy .env.example to .env and fill in values
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

### 2. Frontend

```bash
cd frontend
yarn install
yarn start          # runs on port 3000
```

### 3. Seed Admin

The admin user is **auto-seeded on first startup** from `ADMIN_EMAIL` / `ADMIN_PASSWORD` env vars.

| Role   | Email                          | Password        |
|--------|--------------------------------|-----------------|
| admin  | admin@unchainedcoffee.com      | unchained2025   |
| viewer | viewer@unchainedcoffee.com     | viewer2025      |

---

## API Reference

### Public Endpoints

| Method | Path                           | Description                                      |
|--------|--------------------------------|--------------------------------------------------|
| GET    | `/api/health`                  | Health check                                     |
| POST   | `/api/auth/login`              | Admin login → JWT token                          |
| POST   | `/api/affective/profile`       | Upsert taste profile (6 prefs + consent)         |
| GET    | `/api/affective/profile`       | Get profile by `?session_id=`                    |
| POST   | `/api/affective/response`      | Submit product affective response                |
| POST   | `/api/events`                  | Log a client-side event                          |
| POST   | `/api/affective/taste-fit`     | Compute taste-fit score for one product          |
| POST   | `/api/affective/taste-fit/batch` | Compute scores for multiple products           |

### Admin Endpoints (Bearer token required)

| Method | Path                             | Description                                    | Role    |
|--------|----------------------------------|------------------------------------------------|---------|
| GET    | `/api/admin/products`            | List products with response counts             | any     |
| GET    | `/api/admin/products/summary`    | Product insights (averages, distributions, tags)| any    |
| GET    | `/api/admin/segments`            | Preference band breakdowns                     | any     |
| GET    | `/api/admin/funnel`              | Funnel event counts                            | any     |
| GET    | `/api/admin/export.csv`          | CSV export of responses                        | admin   |
| DELETE | `/api/admin/data`                | Privacy deletion by session/consumer ID        | admin   |

---

## Data Model (MongoDB Collections)

### `events`
Tracks funnel events: `product_viewed`, `affective_form_viewed`, `affective_form_opened`, `affective_form_submitted`, `taste_profile_updated`, `consent_updated`, `data_deleted`.

| Field        | Type          | Notes                           |
|--------------|---------------|---------------------------------|
| event_id     | string (uuid) | Primary key                    |
| event_name   | string        |                                 |
| event_time   | string (ISO)  | Server timestamp                |
| actor_type   | string        | consumer / system / internal_ops|
| session_id   | string        |                                 |
| consumer_id  | string / null |                                 |
| source       | string        | web / qr                        |
| product_id   | string / null |                                 |
| variant_id   | string / null |                                 |
| metadata     | object        |                                 |

### `consumer_taste_profiles`
One record per session. Upserted on each preference submission.

| Field               | Type     | Notes              |
|---------------------|----------|--------------------|
| profile_id          | uuid     | Primary key        |
| session_id          | string   | Unique, sparse     |
| consumer_id         | uuid/null|                    |
| aroma_pref_1to9     | int 1–9  |                    |
| flavor_pref_1to9    | int 1–9  |                    |
| aftertaste_pref_1to9| int 1–9  |                    |
| acidity_pref_1to9   | int 1–9  |                    |
| sweetness_pref_1to9 | int 1–9  |                    |
| mouthfeel_pref_1to9 | int 1–9  |                    |
| consent_analytics   | bool     |                    |
| consent_marketing   | bool     |                    |
| updated_at          | ISO date |                    |

### `product_affective_responses`
One record per submission (per product per session).

| Field                | Type          | Notes                          |
|----------------------|---------------|--------------------------------|
| response_id          | uuid          | Primary key                    |
| session_id           | string        |                                |
| consumer_id          | uuid / null   |                                |
| product_id           | string        |                                |
| variant_id           | string / null |                                |
| mode                 | string        | `preference_only` or `tasted`  |
| aroma_1to9           | int / null    | Required if mode = tasted      |
| flavor_1to9          | int / null    |                                |
| aftertaste_1to9      | int / null    |                                |
| acidity_1to9         | int / null    |                                |
| sweetness_1to9       | int / null    |                                |
| mouthfeel_1to9       | int / null    |                                |
| overall_liking_1to9  | int / null    | Only in tasted mode            |
| notes                | string / null | Max 280 chars, HTML-stripped   |
| standout_tags        | string[]      | Max 5                          |
| standout_tags_source | string / null | canonical / derived            |
| fit_tags             | string[]      |                                |
| consent_analytics    | bool          |                                |
| consent_marketing    | bool          |                                |
| created_at           | ISO date      | Server timestamp               |

### `admin_users`
Seeded on startup from env vars.

---

## Taste-Fit Score Algorithm

Compares user preference profile (6 attributes, 1–9) against a product's sensory profile:

```
per_attribute_match = 1 - |preference - product_sensory| / 8
raw_score = average(all_attribute_matches) * 100
curved_score = clamp(raw_score * 1.1 - 5, 0, 99)
```

| Score Range | Label           |
|-------------|-----------------|
| 90–99       | Perfect Match   |
| 75–89       | Great Match     |
| 60–74       | Good Fit        |
| 45–59       | Decent Fit      |
| 0–44        | Different Vibe  |

The breakdown includes per-attribute match %, preference value, product value, and delta direction.

---

## Widget Modes

### "My Preferences" (default)
- 6 attribute scales (1–9 tappable squares)
- Consent toggles
- Saves to `consumer_taste_profiles` + creates `product_affective_response` (mode=preference_only)

### "I'm drinking it now"
- Same 6 attributes + Overall Liking scale
- Standout tag chips (canonical flavor families + product tasting notes, max 5)
- Fit/issue chips (Too bright, Not sweet enough, Too bitter, etc., max 3)
- Notes textarea (280 char limit)
- Consent toggles
- Creates `product_affective_response` (mode=tasted)

---

## Shopify Integration (Future)

Add this snippet to your Shopify PDP template (Liquid):

```html
<div id="taste-fit-widget"
     data-product-id="{{ product.id }}"
     data-variant-id="{{ product.selected_or_first_available_variant.id }}"
     data-product-handle="{{ product.handle }}">
</div>
<script src="https://YOUR_DEPLOYED_URL/widget.js" defer></script>
```

The widget listens for variant changes and updates `variant_id` in submissions.

---

## Admin Dashboard Pages

| Route                          | Description                                  |
|--------------------------------|----------------------------------------------|
| `/admin/login`                 | Email + password login                       |
| `/admin/products`              | Product list with search, response counts    |
| `/admin/products/:productId`   | Distributions, averages, tags, CSV export    |
| `/admin/funnel`                | product_viewed → form_viewed → form_opened → form_submitted |
| `/admin/segments`              | Preference bands (1–3, 4–6, 7–9) per attribute |
| `/admin/privacy`               | Delete all data by session_id or consumer_id |

---

## Validation & Security

- All 1–9 fields validated as integers in [1..9]
- `mode=tasted` requires all 7 rating fields (6 attributes + overall liking)
- Notes: HTML stripped, max 280 chars
- Standout tags: max 5 selections
- Rate limiting: 10 submissions per session/day on public POST endpoints, 50 events/day
- Passwords stored as bcrypt hashes
- JWT tokens expire after 24 hours
- Admin role required for CSV export and data deletion
- Client-side retry with exponential backoff on network failures

---

## Events Tracked

| Event Name                  | When                                  | Metadata                          |
|-----------------------------|---------------------------------------|-----------------------------------|
| `product_viewed`            | PDP loads                             | `{handle}`                        |
| `affective_form_viewed`     | Widget renders                        | `{product_id}`                    |
| `affective_form_opened`     | Mode toggle clicked                   | `{product_id, mode}`              |
| `affective_form_submitted`  | Form submitted                        | `{product_id, mode, has_notes}`   |
| `taste_profile_updated`     | Profile saved/updated                 | `{fields_changed[]}`              |
| `consent_updated`           | Consent toggles changed               | `{consent_analytics, consent_marketing}` |
| `data_deleted`              | Admin privacy deletion                | `{deleted_by, counts}`            |

---

## Design Tokens

The app uses CSS custom properties for theming (defined in `index.css`):

**Widget theme** (dark/earthy — matches Unchained Coffee brand):
`--w-bg`, `--w-surface`, `--w-accent`, `--w-text`, etc.

**Admin theme** (clean SaaS):
`--a-bg`, `--a-surface`, `--a-primary`, `--a-text`, etc.

Fonts: **Fraunces** (headings), **Inter** (body), **JetBrains Mono** (data/numbers).

---

## License

Proprietary — Unchained Coffee, LLC.
