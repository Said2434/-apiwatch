# APIWatch - API Monitoring & Uptime Tracking

> A production-ready full-stack SaaS application for monitoring API uptime and performance with real-time WebSocket updates and intelligent alerting.

[![Live Demo](https://img.shields.io/badge/demo-live-success)](https://apiwatch-livid.vercel.app)
[![Backend](https://img.shields.io/badge/backend-Railway-blueviolet)](https://apiwatch-production.up.railway.app)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

## 🎯 Live Demo

**Frontend**: [https://apiwatch-livid.vercel.app](https://apiwatch-livid.vercel.app)
**Backend API**: [https://apiwatch-production.up.railway.app](https://apiwatch-production.up.railway.app)
**API Docs**: [https://apiwatch-production.up.railway.app/api/docs](https://apiwatch-production.up.railway.app/api/docs)

*Try it out - register an account and start monitoring your APIs!*

---

## 📖 Table of Contents

- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Architecture](#-architecture)
- [Quick Start](#-quick-start)
- [Environment Variables](#-environment-variables)
- [API Documentation](#-api-documentation)
- [Deployment](#-deployment)
- [Project Structure](#-project-structure)
- [Development Journey](#-development-journey)
- [Lessons Learned](#-lessons-learned)

---

## ✨ Features

### Core Functionality
- **API Health Monitoring** - Track uptime and response times for any HTTP/HTTPS endpoint
- **Real-time Updates** - WebSocket integration for live dashboard updates without page refresh
- **Response Time Graphs** - Beautiful charts showing 24-hour performance trends with color-coded indicators
- **Incident Detection** - Automatic downtime detection with incident tracking and history
- **Smart Analytics** - Overall uptime percentage, average response times, and incident counts

### Technical Features
- **JWT Authentication** - Secure user authentication with access tokens
- **Background Workers** - APScheduler for automated health checks every 60 seconds
- **RESTful API** - Clean, documented API with OpenAPI/Swagger
- **WebSocket Server** - Real-time bidirectional communication for live updates
- **Database Migrations** - Alembic for version-controlled schema changes
- **CORS Configured** - Production-ready cross-origin resource sharing

### User Experience
- **Modern UI** - Clean, responsive interface built with React + TailwindCSS
- **Live Indicator** - Shows WebSocket connection status in real-time
- **Color-Coded Metrics** - Instant visual feedback (green = good, yellow = warning, red = critical)
- **Responsive Design** - Works seamlessly on desktop, tablet, and mobile

---

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern, fast Python web framework with async support
- **PostgreSQL** - Robust relational database with ACID compliance
- **SQLAlchemy 2.0** - Powerful async ORM with type hints
- **Alembic** - Database migration management
- **APScheduler** - Background task scheduling for health checks
- **Redis** - Caching and session storage
- **WebSockets** - Real-time bidirectional communication
- **JWT (python-jose)** - Secure token-based authentication
- **bcrypt** - Password hashing
- **httpx** - Async HTTP client for API checks
- **Pydantic** - Data validation and settings management

### Frontend
- **React 18** - Modern UI library with hooks
- **Vite** - Lightning-fast build tool and dev server
- **TailwindCSS** - Utility-first CSS framework
- **Recharts** - Composable charting library for response time graphs
- **React Query (TanStack)** - Powerful async state management
- **Zustand** - Lightweight state management
- **Axios** - HTTP client for API calls
- **Lucide React** - Beautiful icon library

### DevOps & Deployment
- **Railway** - Backend hosting with PostgreSQL database
- **Vercel** - Frontend hosting with CDN
- **Docker** - Containerization (optional for local dev)
- **Git** - Version control

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Client Browser                       │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  React Frontend (Vercel)                            │    │
│  │  - Dashboard UI                                     │    │
│  │  - WebSocket Client                                 │    │
│  │  - Response Time Charts                             │    │
│  └──────────────┬──────────────────────┬───────────────┘    │
└─────────────────┼──────────────────────┼────────────────────┘
                  │                      │
                  │ HTTPS/REST           │ WSS/WebSocket
                  │                      │
┌─────────────────▼──────────────────────▼────────────────────┐
│              FastAPI Backend (Railway)                       │
│  ┌────────────────────────────────────────────────────┐     │
│  │  API Endpoints                                     │     │
│  │  /api/v1/auth      - Authentication                │     │
│  │  /api/v1/monitors  - Monitor CRUD                  │     │
│  │  /api/v1/metrics   - Analytics & Stats             │     │
│  │  /api/v1/ws        - WebSocket Connection          │     │
│  └────────────────────────────────────────────────────┘     │
│                                                              │
│  ┌────────────────────────────────────────────────────┐     │
│  │  Background Workers (APScheduler)                  │     │
│  │  - Health Check Scheduler (60s interval)           │     │
│  │  - WebSocket Manager & Broadcasting                │     │
│  │  - Incident Detection & Tracking                   │     │
│  └────────────────────────────────────────────────────┘     │
│                                                              │
│  ┌───────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  PostgreSQL   │  │    Redis     │  │  WebSocket   │     │
│  │   Database    │  │    Cache     │  │   Manager    │     │
│  └───────────────┘  └──────────────┘  └──────────────┘     │
└──────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **User Registration/Login** → JWT token issued → Stored in localStorage
2. **Create Monitor** → Saved to PostgreSQL → Background worker picks it up
3. **Health Check Cycle** (every 60s):
   - Worker fetches all active monitors
   - Makes HTTP requests to each endpoint
   - Records response time, status, and errors
   - Detects incidents (3 consecutive failures)
   - Broadcasts update via WebSocket
4. **Real-time Update** → WebSocket notifies frontend → Dashboard refreshes automatically

---

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- PostgreSQL 14+
- Node.js 18+
- Redis (optional, for production)

### Backend Setup

```bash
# Clone repository
git clone https://github.com/yourusername/apiwatch.git
cd apiwatch/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration (see Environment Variables section)

# Start PostgreSQL (using Docker)
docker run --name apiwatch-postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=apiwatch \
  -p 5432:5432 \
  -d postgres:14

# Run database migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at `http://localhost:8000`
API Documentation: `http://localhost:8000/api/docs`

### Frontend Setup

```bash
# Navigate to frontend directory
cd ../frontend

# Install dependencies
npm install

# Create environment file
cp .env.example .env
# Edit .env to point to your backend (default: http://localhost:8000)

# Start development server
npm run dev
```

Frontend will be available at `http://localhost:5173`

---

## 🔐 Environment Variables

### Backend (.env)

```bash
# Database Configuration
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/apiwatch
ASYNC_DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/apiwatch

# Security
SECRET_KEY=your-secret-key-here-generate-with-openssl-rand-hex-32
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application Settings
APP_NAME=APIWatch
DEBUG=True

# CORS (comma-separated origins)
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

# Redis (optional)
REDIS_URL=redis://localhost:6379/0

# Health Check Settings
HEALTH_CHECK_INTERVAL=60  # seconds
INCIDENT_THRESHOLD=3      # consecutive failures before incident
```

### Frontend (.env)

```bash
# Backend API URL
VITE_API_URL=http://localhost:8000
```

### Production Environment Variables

**Railway (Backend):**
```bash
DATABASE_URL=postgresql://postgres:xxx@monorail.proxy.rlwy.net:xxxxx/railway
ASYNC_DATABASE_URL=postgresql+asyncpg://postgres:xxx@monorail.proxy.rlwy.net:xxxxx/railway
SECRET_KEY=your-production-secret-key
ALLOWED_ORIGINS=https://apiwatch-livid.vercel.app
REDIS_URL=redis://default:xxx@redis.railway.internal:6379
DEBUG=False
```

**Vercel (Frontend):**
```bash
VITE_API_URL=https://apiwatch-production.up.railway.app
```

---

## 📚 API Documentation

### Authentication Endpoints

#### Register
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123",
  "full_name": "John Doe"
}

Response: 201 Created
{
  "id": 1,
  "email": "user@example.com",
  "created_at": "2025-01-15T10:30:00Z"
}
```

#### Login
```http
POST /api/v1/auth/login
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=SecurePass123

Response: 200 OK
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

### Monitor Endpoints

#### Create Monitor
```http
POST /api/v1/monitors/
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "My API",
  "url": "https://api.example.com/health",
  "check_interval": 60,
  "timeout": 30
}

Response: 201 Created
{
  "id": 1,
  "name": "My API",
  "url": "https://api.example.com/health",
  "is_active": true,
  "created_at": "2025-01-15T10:30:00Z"
}
```

#### List Monitors
```http
GET /api/v1/monitors/
Authorization: Bearer {token}

Response: 200 OK
[
  {
    "id": 1,
    "name": "My API",
    "url": "https://api.example.com/health",
    "is_active": true,
    "last_check": "2025-01-15T10:29:00Z",
    "status": "up"
  }
]
```

### Metrics Endpoints

#### Dashboard Stats
```http
GET /api/v1/metrics/dashboard
Authorization: Bearer {token}

Response: 200 OK
{
  "monitors": [
    {
      "id": 1,
      "name": "My API",
      "uptime_percentage": 99.5,
      "avg_response_time": 245.3,
      "current_status": "up",
      "incident_count": 2
    }
  ],
  "overall_uptime": 99.5
}
```

#### Health Check History
```http
GET /api/v1/metrics/monitor-stats/{monitor_id}?hours=24
Authorization: Bearer {token}

Response: 200 OK
{
  "monitor_id": 1,
  "recent_checks": [
    {
      "checked_at": "2025-01-15T10:29:00Z",
      "is_up": true,
      "response_time": 234,
      "status_code": 200
    }
  ],
  "uptime_percentage": 99.8,
  "avg_response_time": 245.3
}
```

**Full API documentation available at:** `/api/docs` (Swagger UI) or `/api/redoc` (ReDoc)

---

## 🌐 Deployment

This project is deployed using modern cloud platforms:

### Backend - Railway

1. **Create Railway Project**
   ```bash
   # Install Railway CLI
   npm install -g @railway/cli

   # Login and initialize
   railway login
   railway init
   ```

2. **Add PostgreSQL Database**
   - Add PostgreSQL plugin in Railway dashboard
   - Copy `DATABASE_URL` to environment variables

3. **Configure Environment Variables**
   - Add all production environment variables (see Environment Variables section)
   - Set `DEBUG=False`
   - Add Vercel URL to `ALLOWED_ORIGINS`

4. **Deploy**
   ```bash
   railway up
   ```

**Files needed:**
- `runtime.txt` - Specifies Python version (python-3.12.8)
- `requirements.txt` - Python dependencies
- `Procfile` - Deployment command

### Frontend - Vercel

1. **Connect GitHub Repository**
   - Import project in Vercel dashboard
   - Select `frontend` folder as root directory

2. **Configure Build Settings**
   - Build Command: `npm run build`
   - Output Directory: `dist`
   - Install Command: `npm install`

3. **Add Environment Variables**
   - `VITE_API_URL` = Your Railway backend URL

4. **Deploy**
   - Automatic deployment on every git push

---

## 📁 Project Structure

```
apiwatch/
├── backend/
│   ├── app/
│   │   ├── api/                    # API route handlers
│   │   │   ├── auth.py            # Authentication endpoints
│   │   │   ├── monitors.py        # Monitor CRUD endpoints
│   │   │   ├── metrics.py         # Analytics endpoints
│   │   │   └── websocket.py       # WebSocket endpoint
│   │   ├── models/                 # SQLAlchemy ORM models
│   │   │   ├── user.py            # User model
│   │   │   ├── monitor.py         # Monitor model
│   │   │   ├── health_check.py    # HealthCheck model
│   │   │   └── incident.py        # Incident model
│   │   ├── schemas/                # Pydantic schemas
│   │   │   ├── user.py            # User validation schemas
│   │   │   ├── monitor.py         # Monitor schemas
│   │   │   └── metrics.py         # Metrics response schemas
│   │   ├── workers/                # Background tasks
│   │   │   ├── scheduler.py       # APScheduler setup
│   │   │   └── health_checker.py  # Health check worker
│   │   ├── websocket/              # WebSocket management
│   │   │   └── manager.py         # Connection manager
│   │   ├── utils/                  # Utility functions
│   │   │   └── security.py        # Password hashing, JWT
│   │   ├── config.py               # Settings management
│   │   ├── database.py             # Database connection
│   │   └── main.py                 # FastAPI application
│   ├── alembic/                    # Database migrations
│   │   ├── versions/              # Migration files
│   │   └── env.py                 # Alembic configuration
│   ├── requirements.txt            # Python dependencies
│   ├── Procfile                    # Railway deployment
│   └── runtime.txt                 # Python version
│
├── frontend/
│   ├── src/
│   │   ├── components/            # React components
│   │   │   ├── MonitorCard.jsx   # Monitor display card
│   │   │   ├── ResponseTimeChart.jsx  # Chart component
│   │   │   └── Navbar.jsx        # Navigation
│   │   ├── pages/                 # Page components
│   │   │   ├── Dashboard.jsx     # Main dashboard
│   │   │   ├── Login.jsx         # Login page
│   │   │   └── Register.jsx      # Registration page
│   │   ├── services/              # API services
│   │   │   └── api.js            # Axios configuration
│   │   ├── store/                 # State management
│   │   │   └── authStore.js      # Zustand auth store
│   │   ├── App.jsx                # Main app component
│   │   └── main.jsx               # Entry point
│   ├── public/                    # Static assets
│   ├── package.json               # Node dependencies
│   ├── vite.config.js             # Vite configuration
│   └── tailwind.config.js         # TailwindCSS config
│
└── README.md                       # This file
```

---

## 📈 Development Journey

This project was built over 7 days as a portfolio piece, showcasing full-stack development skills:

- **Day 1:** Project setup, database models, FastAPI foundation
  - PostgreSQL schema design
  - SQLAlchemy models (User, Monitor, HealthCheck, Incident)
  - Alembic migrations setup

- **Day 2:** Authentication system, Monitor CRUD API
  - JWT authentication with python-jose
  - Password hashing with bcrypt
  - RESTful API endpoints for monitors

- **Day 3:** Background health checker, incident detection
  - APScheduler for automated checks
  - Async HTTP requests with httpx
  - Incident detection algorithm (3 consecutive failures)

- **Day 4:** Metrics API, health check history
  - Analytics endpoints (uptime %, avg response time)
  - Time-series data queries
  - Dashboard statistics

- **Day 5:** React frontend, dashboard UI
  - Modern UI with TailwindCSS
  - React Query for data fetching
  - Zustand for authentication state

- **Day 6:** WebSocket integration, response time graphs
  - Real-time updates with WebSocket
  - Recharts for data visualization
  - Live connection indicator

- **Day 7:** Production deployment
  - Railway backend deployment
  - Vercel frontend deployment
  - CORS configuration
  - Environment variable management

---

## 💡 Lessons Learned

### Technical Challenges

1. **WebSocket Connection Management**
   - Challenge: Maintaining persistent WebSocket connections
   - Solution: Built connection manager with automatic reconnection and heartbeat

2. **Background Task Coordination**
   - Challenge: APScheduler running health checks while avoiding race conditions
   - Solution: Async/await patterns with proper database session management

3. **CORS in Production**
   - Challenge: Frontend on Vercel couldn't connect to Railway backend
   - Solution: Properly configured ALLOWED_ORIGINS with environment variables

4. **bcrypt Version Compatibility**
   - Challenge: Different bcrypt versions between development and production
   - Solution: Pinned exact version (bcrypt==4.0.1) in requirements.txt

### Architecture Decisions

- **Why FastAPI?** Modern async support, automatic OpenAPI docs, type hints
- **Why PostgreSQL?** ACID compliance, complex queries for time-series data
- **Why React Query?** Automatic caching, background refetching, optimistic updates
- **Why WebSocket?** Real-time updates without polling, reduced server load

### Best Practices Applied

- ✅ Environment-based configuration (dev/prod)
- ✅ Database migrations with Alembic
- ✅ Password hashing, never plaintext
- ✅ JWT tokens with expiration
- ✅ SQL injection protection via ORM
- ✅ Input validation with Pydantic
- ✅ Error handling and logging
- ✅ Responsive UI design
- ✅ Git version control
- ✅ Clear project structure

---

## 🚀 Future Improvements

Potential features to add (great for interviews to discuss):

### High Priority
- [ ] Email notifications (SendGrid/Resend)
- [ ] Slack/Discord webhook alerts
- [ ] Multi-user organizations/teams
- [ ] Public status pages
- [ ] SMS alerts (Twilio)

### Medium Priority
- [ ] API key authentication
- [ ] Custom alert rules (response time thresholds)
- [ ] More chart types (uptime timeline, geographical response times)
- [ ] Export reports (PDF, CSV)
- [ ] Dark mode

### Technical Improvements
- [ ] Unit tests (pytest + React Testing Library)
- [ ] Integration tests
- [ ] Rate limiting (slow API)
- [ ] Caching with Redis
- [ ] Monitoring (Sentry, DataDog)
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] Docker Compose for local development
- [ ] Kubernetes deployment configuration

---

## 🧪 Testing

```bash
# Backend tests (coming soon)
cd backend
pytest

# Frontend tests (coming soon)
cd frontend
npm test
```

---

## 🤝 Contributing

This is a pet project built for fun. However, feedback and suggestions are always welcome!

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Said**
Full-Stack AI Developer specializing in Python, FastAPI, React, and DevOps

- 🛠️ **Skills Demonstrated:**
  - Full-stack development (Python + React)
  - Real-time systems (WebSocket)
  - Background workers & scheduling
  - Database design & optimization
  - RESTful API design
  - Authentication & security
  - Cloud deployment (Railway + Vercel)
  - Modern DevOps practices


## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Amazing Python web framework
- [React](https://react.dev/) - Powerful UI library
- [TailwindCSS](https://tailwindcss.com/) - Utility-first CSS framework
- [Railway](https://railway.app/) - Easy backend deployment
- [Vercel](https://vercel.com/) - Seamless frontend hosting

---

<div align="center">

**⭐ Star this repo if you find it useful!**

Built with ❤️ by Said

</div>
