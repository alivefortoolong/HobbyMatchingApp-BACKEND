# ProjetAOS Documentation

---

# 1. Project Overview

## Introduction

ProjetAOS is a distributed microservices-based social matching platform designed to manage authentication, user profiles, matching logic, and notifications independently.

The system follows a service-oriented architecture where each service has its own responsibility, database, and API endpoints while communicating through HTTP requests and RabbitMQ events.

The platform supports:

- User registration & authentication
- User profile management
- Like & match system
- Real-time event-based notifications
- Monitoring with Prometheus & Grafana

---

## Tech Stack

| Component | Technology |
|---|---|
| Backend Framework | Django + Django REST Framework |
| Authentication | JWT (SimpleJWT) |
| Databases | PostgreSQL |
| Message Broker | RabbitMQ |
| Monitoring | Prometheus + Grafana |
| Containerization | Docker + Docker Compose |
| API Communication | REST APIs |
| Language | Python |

---

# 2. Architecture Overview

## Microservices Breakdown

| Service | Port | Database | Responsibility |
|---|---|---|---|
| auth_service | 8000 | PostgreSQL | Authentication & JWT issuing |
| user_service | 8001 | PostgreSQL | User profile management |
| matching_service | 8002 | PostgreSQL | Likes, matches, suggestions |
| notification_service | 8003 | PostgreSQL | Notifications & RabbitMQ consumers |

---

## Architecture Diagram

```text
                         +------------------+
                         |     Frontend     |
                         +--------+---------+
                                  |
                                  v
                    +-------------+-------------+
                    |        auth_service       |
                    |  JWT Issuer (HS256)      |
                    +-------------+-------------+
                                  |
             -----------------------------------------
             |                   |                   |
             v                   v                   v

    +----------------+  +----------------+  +----------------------+
    |  user_service  |  | matching_srv   |  | notification_srv     |
    | User Profiles  |  | Likes/Matches  |  | Notifications        |
    +----------------+  +----------------+  +----------------------+
                                 |
                                 v
                           +-----------+
                           | RabbitMQ  |
                           +-----------+
```

---

## Key Design Principle

All services share the same JWT secret key.

- Tokens are generated only by `auth_service`
- Other services validate tokens locally
- No centralized token introspection required
- Authentication remains stateless

This is implemented using a shared `JWT_SECRET_KEY` environment variable across all services.

---

# 3. Security & Authentication

## JWT Authentication Flow

1. User logs in or registers through `auth_service`
2. `auth_service` generates a JWT token
3. Frontend stores token
4. Token is sent in `Authorization: Bearer <token>`
5. Other services validate token locally

---

## JWT Details

| Property | Value |
|---|---|
| Algorithm | HS256 |
| Token Lifetime | 24 hours |
| Issuer | auth_service |
| Authentication Type | Bearer Token |

---

## JWT Payload

```json
{
  "user_id": 1,
  "email": "user@example.com",
  "exp": 1710000000
}
```

---

## RemoteJWTAuthentication

All non-auth services use custom authentication middleware:

```python
RemoteJWTAuthentication
```

Responsibilities:

- Extract bearer token
- Validate signature using shared secret
- Decode JWT payload
- Attach authenticated user to request

---

## Security Concerns

The following development configurations should be flagged before production deployment:

| Concern | Risk |
|---|---|
| DEBUG=True | Exposes stack traces and internal information |
| CORS_ALLOW_ALL_ORIGINS=True | Allows requests from any origin |
| Hardcoded fallback secrets | Weakens authentication security |
| Shared JWT secret across services | Single secret compromise affects all services |

---

# 4. Inter-Service Communication & Flows

# Registration Flow

## Flow Diagram

```text
Client
  |
  | POST /register/
  v
auth_service
  |
  | Create Auth User
  | Generate JWT
  |
  | POST /api/users/me/
  v
user_service
  |
  | Create User Profile
  v
Response Returned
```

---

## Flow Description

1. Client sends registration request
2. `auth_service` creates authentication account
3. JWT token is generated
4. `auth_service` calls `user_service`
5. `user_service` creates profile
6. Final response returns token + user info

---

# Like / Match Flow

## Flow Diagram

```text
Client
  |
  | POST /like/
  v
matching_service
  |
  | Create Like
  | Check Mutual Like
  |
  +------------------------+
  | Mutual?                |
  +-----------+------------+
              |
             Yes
              |
              v
       Create Match
              |
              v
        Publish Event
              |
              v
           RabbitMQ
              |
              v
notification_service
              |
              v
 Create Notifications
```

---

## Match Event Process

If two users like each other:

1. Match is created
2. `new_match` event published to RabbitMQ
3. Notification consumer receives event
4. Notifications created for both users

---

# 5. Setup & Deployment

# Local Setup

Each service follows the same setup pattern.

---

## 1. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 2. Configure Environment Variables

Create `.env`

```env
DEBUG=True
SECRET_KEY=your_secret
DATABASE_URL=postgresql://...
JWT_SECRET_KEY=shared_secret
```

---

## 3. Apply Migrations

```bash
python manage.py migrate
```

---

## 4. Run Service

```bash
python manage.py runserver
```

---

# Docker Compose Setup

## Start Entire Stack

```bash
docker compose up --build
```

---

## Included Containers

| Container | Purpose |
|---|---|
| auth_service | Authentication |
| user_service | User management |
| matching_service | Matching engine |
| notification_service | Notifications |
| postgres_* | Databases |
| rabbitmq | Message broker |
| prometheus | Metrics |
| grafana | Monitoring dashboard |

---

## Networks & Volumes

Docker Compose provides:

- Shared internal network
- Persistent PostgreSQL volumes
- RabbitMQ data persistence

---

## Environment Variables Reference

| Variable | Description |
|---|---|
| SECRET_KEY | Django secret |
| JWT_SECRET_KEY | Shared JWT validation secret |
| DATABASE_URL | PostgreSQL connection |
| RABBITMQ_URL | RabbitMQ connection |
| DEBUG | Debug mode |
| ALLOWED_HOSTS | Allowed domains |

---

# 6. API Endpoints Reference

# auth_service

## Register

| Method | Endpoint |
|---|---|
| POST | /register/ |

### Request

```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

### Response

```json
{
  "token": "jwt_token"
}
```

---

## Login

| Method | Endpoint |
|---|---|
| POST | /login/ |

---

# user_service

## Get Current User Profile

| Method | Endpoint |
|---|---|
| GET | /api/users/me/ |

Authentication Required: Yes

---

## Update Profile

| Method | Endpoint |
|---|---|
| PUT | /api/users/me/ |

---

# matching_service

## Like User

| Method | Endpoint |
|---|---|
| POST | /like/ |

### Request

```json
{
  "liked_user_id": 5
}
```

---

## Suggestions Pool

| Method | Endpoint |
|---|---|
| GET | /suggestions-pool/ |

---

## Matched User

| Method | Endpoint |
|---|---|
| GET | /matched/{id}/ |

---

# notification_service

## Get Notifications

| Method | Endpoint |
|---|---|
| GET | /notifications/ |

---

# 7. RabbitMQ Events

## Queue

```text
activity_events
```

---

## Event Types

| Event | Description |
|---|---|
| new_like | User liked another user |
| new_match | Mutual match created |

---

## new_like Payload

```json
{
  "type": "new_like",
  "from_user": 1,
  "to_user": 2
}
```

---

## new_match Payload

```json
{
  "type": "new_match",
  "user1": 1,
  "user2": 2
}
```

---

## Consumer Responsibilities

The notification consumer:

1. Reads RabbitMQ events
2. Detects event type
3. Creates notification records
4. Stores notifications in database

---

# 8. Monitoring

# Prometheus

Prometheus scrapes metrics from all services.

---

## Example Targets

```yaml
scrape_configs:
  - job_name: 'auth_service'
    static_configs:
      - targets: ['auth_service:8000']

  - job_name: 'user_service'
    static_configs:
      - targets: ['user_service:8001']

  - job_name: 'matching_service'
    static_configs:
      - targets: ['matching_service:8002']

  - job_name: 'notification_service'
    static_configs:
      - targets: ['notification_service:8003']
```

---

# Grafana

Grafana connects to Prometheus as a datasource.

## Default Access

| Service | URL |
|---|---|
| Grafana | http://localhost:3000 |
| Prometheus | http://localhost:9090 |

---

# Conclusion

ProjetAOS demonstrates a clean microservices architecture using:

- Independent services
- Stateless JWT authentication
- Event-driven communication with RabbitMQ
- Containerized deployment
- Centralized monitoring

The architecture is scalable, modular, and suitable for distributed systems learning and experimentation.