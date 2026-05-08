# 🎯 ProjetAOS — Hobby-Based Matching Platform

> A microservices backend that connects people based on shared interests.

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)
![Django](https://img.shields.io/badge/Django-REST_Framework-green?logo=django)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-blue?logo=postgresql)
![RabbitMQ](https://img.shields.io/badge/RabbitMQ-Messaging-orange?logo=rabbitmq)
![Docker](https://img.shields.io/badge/Docker-Compose-blue?logo=docker)
![Prometheus](https://img.shields.io/badge/Prometheus-Monitoring-red?logo=prometheus)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Security & Authentication](#security--authentication)
- [Inter-Service Communication](#inter-service-communication)
- [Getting Started](#getting-started)
- [API Reference](#api-reference)
- [RabbitMQ Events](#rabbitmq-events)
- [Monitoring](#monitoring)
- [Infrastructure](#infrastructure)

---

## Overview

**ProjetAOS** is a hobby-based matching platform built with a microservices architecture. Users register with their full profile in a single call, browse other users, like them, and get matched when the like is mutual. Notifications are delivered asynchronously via RabbitMQ.

### ✨ Features

- Single-call registration — auth account and full profile created atomically
- JWT authentication shared across all services via a common secret (no inter-service auth calls)
- Browse all user profiles with hobby filtering
- Like system with automatic match detection on mutual likes
- Async notifications via RabbitMQ (`new_like`, `new_match` events)
- Load-balanced `matching_service` (two replicas behind Traefik)
- Monitoring with Prometheus & Grafana
- Service discovery via Consul

### 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python · Django · Django REST Framework |
| Database | PostgreSQL (one DB per service) |
| Messaging | RabbitMQ |
| Auth | JWT — HS256, shared secret across all services |
| API Gateway | Traefik v3 (routing + rate limiting + CORS) |
| Service Discovery | Consul |
| Caching | Redis |
| Monitoring | Prometheus + Grafana |
| Containerization | Docker + Docker Compose |
| Docs | drf-spectacular (Swagger / Redoc) |

---

## Architecture

4 independent microservices, each with its own database and port.

```
┌───────────────────────────────────────────────────┐
│                    Frontend                        │
└───────────────────────┬───────────────────────────┘
                        │
                        ▼
┌───────────────────────────────────────────────────┐
│              Traefik API Gateway :80               │
│      (routing · rate-limit · CORS headers)        │
└──┬────────────┬──────────────┬────────────────────┘
   │            │              │              │
   ▼            ▼              ▼              ▼
:8000        :8001          :8002/:8012    :8003
auth_svc   user_svc      matching_svc   notif_svc
   │            ▲              │              ▲
   │            │              │ RabbitMQ     │
   └────────────┘              └──────────────┘
  (profile create on register)   (async events)
```

| Service | Port | Database | Role |
|---------|------|----------|------|
| `auth_service` | 8000 | `projetaos_auth` | Registration, Login, JWT issuance |
| `user_service` | 8001 | `projetaos_users` | Profiles, hobbies, preferences |
| `matching_service` | 8002 / 8012 | `projetaos_matching` | Like, match detection, suggestions |
| `notification_service` | 8003 | `projetaos_notifications` | Notifications, RabbitMQ consumer |

### Key Principle — Shared JWT

All 4 services use the **same `JWT_SECRET_KEY`** to validate tokens locally — no HTTP calls needed for auth. The token is issued by `auth_service` and accepted by all others via a custom `RemoteJWTAuthentication` class.

---

## Security & Authentication

### JWT Flow

1. User registers or logs in through `auth_service`
2. `auth_service` issues an HS256 JWT containing `user_id` and `email`
3. Client stores the token and sends it as `Authorization: Bearer <token>`
4. Each downstream service validates the signature locally using the shared secret

### JWT Properties

| Property | Value |
|----------|-------|
| Algorithm | HS256 |
| Lifetime | 24 hours |
| Issuer | `auth_service` |
| Payload fields | `user_id`, `email`, `exp` |

### Production Checklist

Before deploying to production, address these development-only settings:

| Concern | Risk |
|---------|------|
| `DEBUG=True` | Exposes stack traces |
| `CORS_ALLOW_ALL_ORIGINS=True` | Accepts requests from any origin |
| Hardcoded fallback secrets in settings files | Weakens security if `.env` is missing |
| Single shared JWT secret | One compromise affects all services |

---

## Inter-Service Communication

### Registration Flow

```
Client  ──POST /register/──▶  auth_service
                                │  1. Create User
                                │  2. Generate JWT
                                │
                                └──POST /api/users/me/──▶  user_service
                                                              │  Create Profile
                                                              ▼
                               ◀──{ id, token }─────────────────────────
```

### Like / Match Flow

```
Client  ──POST /like/──▶  matching_service
                            │  1. Create Like record
                            │  2. Check mutual like
                            │
                   ┌────────┴────────┐
                 Mutual?           Not mutual
                   │                 │
                   ▼                 ▼
             Create Match       { liked: true }
                   │
                   ▼
             Publish to RabbitMQ
                   │
                   ▼
          notification_service consumer
                   │
                   ▼
        Create Notification for both users
```

---

## Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL
- RabbitMQ *(optional — the app works without it; notifications just won't be created)*

### Database Setup

```sql
createdb projetaos_auth
createdb projetaos_users
createdb projetaos_matching
createdb projetaos_notifications
```

### Environment Variables

Each service needs a `.env` file at its root. **`JWT_SECRET_KEY` must be identical across all services.**

```env
# Common to all services
SECRET_KEY=your-django-secret-key
JWT_SECRET_KEY=same-key-in-all-four-services
DB_NAME=projetaos_<service>
DB_USER=postgres
DB_PASSWORD=postgres123
DB_HOST=localhost
DB_PORT=5432
```

`auth_service` and `matching_service` also need:
```env
USER_SERVICE_URL=http://127.0.0.1:8001
```

`matching_service` and `notification_service` also need:
```env
RABBITMQ_URL=amqp://guest:guest@localhost:5672/
```

### Running Locally

```powershell
# Terminal 1 — Auth Service
cd projetaos\auth_service
.\venv\Scripts\activate
python manage.py migrate
python manage.py runserver 8000

# Terminal 2 — User Service
cd projetaos\user_service
.\venv\Scripts\activate
python manage.py migrate
python manage.py runserver 8001

# Terminal 3 — Matching Service
cd projetaos\matching_service
.\venv\Scripts\activate
python manage.py migrate
python manage.py runserver 8002

# Terminal 4 — Notification Service
cd projetaos\notification_service
.\venv\Scripts\activate
python manage.py migrate
python manage.py runserver 8003

# Terminal 5 — RabbitMQ Consumer (optional)
cd projetaos\notification_service
.\venv\Scripts\activate
python notifications/consumer.py
```

### Running with Docker

```bash
# Build and start the full stack
docker compose up --build

# Run in background
docker compose up --build -d

# Stop everything
docker compose down

# Full reset (delete volumes)
docker compose down -v
```

**Docker Compose includes:** auth, user, matching (×2), notification, PostgreSQL (×4), RabbitMQ, Traefik, Consul, Redis, Prometheus, Grafana.

---

## API Reference

All endpoints except `register` and `login` require:
```
Authorization: Bearer <token>
```

---

### 🔐 Auth Service — `http://127.0.0.1:8000/api/auth/`

#### `POST /register/`

Creates the user account **and** the full profile in a single call. Returns a usable token immediately.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `email` | string | ✅ | |
| `password` | string | ✅ | min 8 chars |
| `nom` | string | ✅ | |
| `prenom` | string | ✅ | |
| `gender` | string | ✅ | `M` / `F` / `O` |
| `age` | integer | ✅ | 18–99 |
| `town` | string | ✅ | |
| `social_link` | string | ❌ | URL |
| `pref_gender` | string | ❌ | `M` / `F` / `O` / `A` (default: `A`) |
| `pref_age_min` | integer | ❌ | default 18 |
| `pref_age_max` | integer | ❌ | default 99 |
| `hobbies` | array of strings | ❌ | e.g. `["Hiking", "Reading"]` |

**Response `201`**
```json
{ "id": 8, "token": "<jwt_access_token>" }
```

#### `POST /login/`

```json
{ "email": "ali@test.com", "pwd": "12345678" }
```

**Response `200`**
```json
{ "id": 8, "token": "<jwt_access_token>" }
```

> **Note:** The password field is `pwd` on login.

---

### 👤 User Service — `http://127.0.0.1:8001/api/users/`

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | **fetchUsers** — all profiles except the requesting user's |
| `GET` | `/<user_id>/` | **fetchUser** — single user's public profile |
| `GET` | `/preferences/<user_id>/` | **getPref** — user's matching preferences |
| `PATCH` | `/preferences/edit/` | **editPref** — update preferences |

**Profile fields:** `id`, `user_id`, `nom`, `prenom`, `sexe`, `age`, `ville`, `link`, `hobbies`

**Preferences fields:** `prefGender`, `minAge`, `maxAge`, `ville`, `hobbies`

**editPref request body:**
```json
{
  "user_id": 8,
  "prefGender": "F",
  "minAge": 22,
  "maxAge": 35,
  "hobbies": ["Hiking", "Gaming"]
}
```

---

### 💘 Matching Service — `http://127.0.0.1:8002/api/matching/`

#### `POST /like/`

| Field | Type | Description |
|-------|------|-------------|
| `idT` | integer | ID of the liker (defaults to JWT user if omitted) |
| `idR` | integer | ID of the liked user |

**Response `201` — like only:**
```json
{ "liked": true }
```

**Response `201` — mutual match:**
```json
{ "matched": true, "match_id": 2 }
```

#### `GET /matches/<user_id>/`

Returns all confirmed matches enriched with profile data from `user_service`.

```json
[
  {
    "match_id": 2,
    "matched_at": "2026-04-20T14:30:00Z",
    "user": { "user_id": 9, "nom": "Amrani", "prenom": "Sara", ... }
  }
]
```

---

### 🔔 Notification Service — `http://127.0.0.1:8003/api/notifications/<user_id>/`

#### `POST /`

Returns all notifications for the given user, enriched with sender profile data.

```json
[
  {
    "id": 1,
    "from_user_id": 9,
    "nom": "Amrani",
    "prenom": "Sara",
    "sexe": "F",
    "hobbies": ["Hiking"],
    "msg": "Someone liked your profile!",
    "type": "like",
    "read": false,
    "created_at": "2026-04-20T14:28:00Z"
  }
]
```

---

### 📖 API Docs (Swagger / Redoc)

Auto-generated docs are served by `auth_service`:

| Interface | URL |
|-----------|-----|
| Swagger UI | `http://127.0.0.1:8000/api/docs/` |
| Redoc | `http://127.0.0.1:8000/api/redoc/` |
| OpenAPI schema | `http://127.0.0.1:8000/api/schema/` |

---

## RabbitMQ Events

`matching_service` publishes to the `activity_events` queue. `notification_service` consumes them via a dedicated worker process (`notifications/consumer.py`).

| Event | Triggered by | Payload |
|-------|-------------|---------|
| `new_like` | `POST /like/` | `{ "event": "new_like", "from_user": 8, "to_user": 9 }` |
| `new_match` | Mutual like detected | `{ "event": "new_match", "user1": 8, "user2": 9 }` |

If RabbitMQ is unavailable, the app continues working — likes and matches still persist, only notification creation is skipped (error is logged as a warning).

---

## Monitoring

### Prometheus

Prometheus scrapes metrics from all services every 15 seconds.

| Dashboard | URL |
|-----------|-----|
| Prometheus | `http://localhost:9090` |
| Grafana | `http://localhost:3000` (admin / `admin123`) |
| RabbitMQ Management | `http://localhost:15672` |
| Traefik Dashboard | `http://localhost:8080` |
| Consul UI | `http://localhost:8501` |

---

## Infrastructure

### Traefik (API Gateway)

All traffic enters through Traefik on port 80. It handles:
- Path-based routing to the correct service
- Rate limiting (100 req/s average, burst 50)
- CORS headers for all routes
- Load balancing across `matching_service` and `matching_service_2`

### Consul (Service Discovery)

Each service can self-register with Consul via its `consul_register.py` script. Consul performs TCP health checks every 10 seconds.

### Load Balancing

The `matching_service` runs as two replicas (ports 8002 and 8012) behind Traefik's round-robin load balancer.

---

*ProjetAOS — Last updated May 2026*
