<div align="center">

# 🔍 TransactIQ

### Fraud Investigation & Transaction Intelligence Platform

*A full-stack financial intelligence platform built on real PaySim mobile money transaction data*

[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Neo4j](https://img.shields.io/badge/Neo4j-5-008CC1?style=for-the-badge&logo=neo4j&logoColor=white)](https://neo4j.com/)
[![Redis](https://img.shields.io/badge/Redis-7-DC382D?style=for-the-badge&logo=redis&logoColor=white)](https://redis.io/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docs.docker.com/compose/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

</div>

---

## 📌 Overview

**TransactIQ** enables financial intelligence analysts to:

- 🔎 **Search & investigate** target accounts across millions of transactions
- 🕸️ **Explore transaction graphs** with fan-in / fan-out relationship analysis (Neo4j)
- 🧮 **Evaluate explainable risk scores** using a configurable weighted model
- 📊 **Review a ranked suspicious-account queue** with fraud, velocity, and volume signals
- 🧭 **Detect bounded transaction communities and cycles** in Neo4j
- 📂 **Manage investigation cases** with full lifecycle tracking
- 🧾 **Attach evidence and approve fraud / false-positive verdicts** with RBAC
- 🔔 **Receive real-time alerts** via WebSocket push notifications
- 📄 **Export PDF intelligence reports** with graph, risk, evidence, and notes sections
- 🗂️ **Full audit logging** of all analyst actions

> Built on the real **PaySim Kaggle dataset** — 6.3M synthetic mobile money transactions with ground-truth fraud labels (`isFraud = 1`).

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                  React SPA (Vite)                   │
│   Auth · Search · Graph Viewer · Cases · Alerts     │
└────────────────────┬────────────────────────────────┘
                     │ REST API + WebSockets
┌────────────────────▼────────────────────────────────┐
│              FastAPI Backend (Python)               │
│   Auth · Accounts · Graph · Risk · Cases · Export  │
└──────┬─────────────┬─────────────┬──────────────────┘
       │             │             │
  ┌────▼────┐  ┌─────▼─────┐ ┌───▼────┐
  │ Postgres│  │   Neo4j   │ │ Redis  │
  │ (ORM)  │  │  (Cypher) │ │(Cache) │
  └────────┘  └───────────┘ └────────┘
```

---

## 📁 Project Structure

```
TransactIQ/
├── backend/
│   ├── app/
│   │   ├── core/           # Config, Security, DB, Neo4j, Redis, WebSockets
│   │   ├── models/         # SQLAlchemy Models (User, Account, Transaction, Case, AuditLog)
│   │   ├── schemas/        # Pydantic v2 Schemas
│   │   ├── repositories/   # Repository abstraction layer
│   │   ├── services/       # Business logic & Risk Scoring Engine
│   │   ├── routers/        # REST API & WebSocket endpoints
│   │   └── main.py         # FastAPI entrypoint
│   ├── alembic/            # Database migrations
│   ├── tests/              # Pytest unit & integration suite
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── api/            # Axios client with JWT interceptors
│   │   ├── components/     # Navbar, Search, GraphViewer (Cytoscape.js), Cases, Audit, Alerts
│   │   ├── context/        # AuthContext (React Context API)
│   │   └── types/          # TypeScript definitions
│   └── Dockerfile
├── scripts/
│   ├── load_paysim_postgres.py   # PaySim → PostgreSQL ingestion
│   └── load_paysim_neo4j.py      # PaySim → Neo4j batch UNWIND ingestion
├── docker-compose.yml
└── .env.example
```

---

## ⚡ Quick Start

### Option A — Docker Compose (Recommended)

```bash
# 1. Clone the repo
git clone https://github.com/VasaShashank/TransactIQ.git
cd TransactIQ

# 2. Copy and configure environment
cp .env.example .env

# 3. Start all services
docker-compose up -d --build
```

Services will be available at:

| Service | URL |
|---|---|
| React Frontend | http://localhost:3000 |
| FastAPI Backend | http://localhost:8000 |
| Swagger API Docs | http://localhost:8000/docs |
| Neo4j Browser | http://localhost:7474 |

### Option B — Local Development

```bash
# Backend
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

### Data Ingestion

Download `paysim.csv` from [Kaggle PaySim Dataset](https://www.kaggle.com/datasets/ealaxi/paysim1) and place it in the project root, then:

```bash
python scripts/load_paysim_postgres.py   # Load into PostgreSQL
python scripts/load_paysim_neo4j.py      # Load into Neo4j
```

---

## 🔑 Default Credentials

| Role | Email | Password |
|---|---|---|
| **Admin** | `admin@fraud.intel` | `admin123` |
| **Senior Analyst** | `senior@fraud.intel` | `senior123` |
| **Analyst** | `analyst@fraud.intel` | `analyst123` |

> ⚠️ Change these in production via environment variables.

---

## 🧮 Risk Scoring Model

TransactIQ computes a normalized risk score using a configurable weighted formula:

$$\text{Risk Score} = w_1 \cdot \text{FraudFlag} + w_2 \cdot \text{TxnFreq} + w_3 \cdot \text{OutgoingVol} + w_4 \cdot \text{LinkedAccounts} + w_5 \cdot \text{Centrality}$$

| Weight | Feature | Default |
|---|---|---|
| $w_1$ | Confirmed / Flagged Fraud | `0.35` |
| $w_2$ | Transaction Frequency | `0.20` |
| $w_3$ | Outgoing Volume | `0.15` |
| $w_4$ | Linked Accounts Count | `0.15` |
| $w_5$ | Graph Degree Centrality | `0.15` |

All weights are configurable via environment variables.

---

## 🔌 API Reference

The full interactive API reference is available at **http://localhost:8000/docs** (Swagger UI) or **http://localhost:8000/redoc** (ReDoc).

### Key Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/auth/login` | Obtain JWT access token |
| `GET` | `/api/v1/accounts/search` | Search by account ID, phone, email, device, or card |
| `GET` | `/api/v1/accounts/risk-queue` | Ranked suspicious-account queue |
| `GET` | `/api/v1/accounts/{id}/timeline` | Get account transaction timeline |
| `GET` | `/api/v1/accounts/{id}/graph` | N-hop graph traversal (Neo4j) |
| `GET` | `/api/v1/accounts/{id}/cycles` | Detect bounded transaction cycles |
| `GET` | `/api/v1/accounts/{id}/community` | Find connected account community |
| `GET` | `/api/v1/accounts/{id}/risk-score` | Compute explainable risk score |
| `POST` | `/api/v1/cases` | Create investigation case |
| `GET` | `/api/v1/cases` | List all cases |
| `PATCH` | `/api/v1/cases/{id}` | Add notes/evidence or approve closure |
| `DELETE` | `/api/v1/cases/{id}` | Delete case (admin only) |
| `GET` | `/api/v1/cases/{id}/export` | Export PDF report |
| `POST` | `/api/v1/alerts/scan` | Scan and publish high-risk alerts |
| `GET` | `/api/v1/audit` | Audit log (admin only) |
| `WS` | `/ws/alerts` | Real-time alert stream |

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | React 18, TypeScript, Vite, Cytoscape.js, Axios, Lucide Icons |
| **Backend** | FastAPI, Python 3.11+, Pydantic v2, SQLAlchemy 2, Alembic |
| **Auth** | JWT (PyJWT), bcrypt via Passlib |
| **Relational DB** | PostgreSQL 15 |
| **Graph DB** | Neo4j 5 Community (Bolt protocol, Cypher) |
| **Cache** | Redis 7 |
| **PDF Export** | ReportLab |
| **Testing** | Pytest, HTTPX |
| **DevOps** | Docker, Docker Compose |

---

## 🧪 Running Tests

```bash
pytest backend/tests -v
```

---

## 📄 License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) for details.

---

<div align="center">
Made with ❤️ for financial crime intelligence
</div>
