# Unchained Coffee - Taste Fit MVP v0 PRD

## Original Problem Statement
Build MVP v0: a "Taste Fit" Affective Form widget that appears on Shopify PDP pages and an internal Admin Dashboard to view aggregated results. The widget collects (A) baseline taste preferences and (B) optional "This coffee" tasting feedback using a 1-9 affective scale. Store everything in MongoDB (adapted from Postgres spec) and log key events for funnel analysis.

## Architecture
- **Frontend**: React 18 + Tailwind CSS 3 + React Router 6 + Recharts
- **Backend**: FastAPI + Motor (async MongoDB driver) + JWT auth
- **Database**: MongoDB (collections: events, consumer_taste_profiles, product_affective_responses, admin_users)
- **Identity**: Anonymous session UUID stored in localStorage

## User Personas
1. **Coffee Consumer** (Widget): Specialty coffee enthusiast, 25-45, mobile-heavy, browsing Shopify PDP
2. **Admin** (Dashboard): Unchained Coffee ops team viewing product insights, funnel analytics, and managing data

## Core Requirements (Implemented)
- [x] Widget UI with dual modes: "My Preferences" / "I'm drinking it now"
- [x] 1-9 affective scale (9 tappable squares) for 6 attributes + overall liking
- [x] Canonical + product-derived standout tags (max 5 selections)
- [x] Fit/Issue tags for "I'm drinking it now" mode
- [x] Consent toggles (analytics default on, marketing default off)
- [x] Anonymous session-based identity (UUID cookie)
- [x] Profile prefill from existing session
- [x] Demo PDP page simulating Shopify product page
- [x] Desktop: right-column panel widget
- [x] Mobile: sticky "Your Taste Fit" button → bottom drawer
- [x] Admin auth (JWT, bcrypt hashed passwords, admin/viewer roles)
- [x] Admin: Product list with search + product insights (distributions, averages, tags, notes)
- [x] Admin: Funnel analytics (product_viewed → form_viewed → form_opened → form_submitted)
- [x] Admin: Preference segments by band (1-3, 4-6, 7-9)
- [x] Admin: CSV export by product + date range
- [x] Admin: Privacy deletion by session_id or consumer_id
- [x] Rate limiting on public POST endpoints
- [x] Input sanitization (HTML stripping, 280 char limit on notes, max 5 tags)
- [x] Client retry with exponential backoff
- [x] Event logging for funnel analysis
- [x] Validation: 1-9 range enforcement, tasted mode requires all fields

## What's Been Implemented (Feb 16, 2026)
### Backend (FastAPI)
- Health check, auth (login), profile CRUD, response creation, event tracking
- Admin endpoints: products list, product summary, segments, funnel, CSV export, privacy delete
- **Taste-Fit Score API**: POST /api/affective/taste-fit (single product) + POST /api/affective/taste-fit/batch (multiple products)
- Score algorithm: per-attribute match (1 - |pref - sensory| / 8), curved for meaningful distribution, labels from "Different Vibe" to "Perfect Match"
- MongoDB indexes for performance
- Seeded admin + viewer accounts

### Frontend (React)
- Demo PDP with 3 Unchained Coffee products (Papayo Natural, Geisha Honey, Red Bourbon)
- TasteFit Widget with mode toggle, 6 attribute scales, consent toggles
- "I'm drinking it now" mode: overall liking + standout tags + fit tags + notes
- **Taste-Fit Score Card**: Animated circular ring with %, expandable per-attribute breakdown with delta arrows, positioned between sensory profile and price on PDP
- Score shows "Discover your Taste Fit" CTA when no profile exists
- Score auto-refreshes after widget submission
- Admin: Login, Products, Product Detail (with Recharts distributions), Funnel, Segments, Privacy
- Responsive design with bottom drawer for mobile (includes score card)
- Design tokens via CSS variables (widget dark/earthy theme, admin clean Swiss style)

## Test Results
- Backend: 17/17 tests passed (100%)
- Frontend: Core functionality working (85%+ - browser automation limited)

## Prioritized Backlog
### P0 (Next)
- Shopify embed script (actual Liquid snippet + script loader)
- Real product ID mapping from Shopify catalog

### P1
- Variant change listener for live variant updates
- Profile merge when consumer logs in (session_id → consumer_id)
- Admin: Notes text viewer/search
- Admin: Time-series charts for response trends

### P2
- Personalization engine (taste-fit score matching)
- QR code flow for in-store tasting
- Consumer accounts / rewards
- A/B test different widget placements
- Email notification when high-value feedback received
