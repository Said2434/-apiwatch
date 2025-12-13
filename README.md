# APIWatch - API Monitoring & Uptime Tracking

A full-stack API monitoring application built with FastAPI and React. Monitor API uptime, response times, and receive real-time alerts when your endpoints go down.

## 🚀 Features

- **API Health Monitoring** - Track uptime and response times for any HTTP endpoint
- **Real-time Alerts** - Get notified when your APIs go down
- **User Authentication** - JWT-based secure authentication
- **Dashboard** - Visual analytics and monitoring dashboard
- **WebSocket Updates** - Real-time status updates
- **Incident Tracking** - Automatic downtime detection and history

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **PostgreSQL** - Reliable relational database
- **SQLAlchemy** - Powerful ORM
- **Alembic** - Database migrations
- **APScheduler** - Background task scheduling
- **Redis** - Caching and pub/sub
- **JWT** - Secure authentication
- **httpx** - Async HTTP client

### Frontend
- **React** - UI library
- **Vite** - Build tool
- **TailwindCSS** - Styling
- **Recharts** - Data visualization
- **React Query** - Data fetching
- **Zustand** - State management

## 📦 Installation

### Prerequisites
- Python 3.10+
- PostgreSQL 14+
- Docker (optional)
- Node.js 18+ (for frontend)

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
# Edit .env with your database credentials

# Start PostgreSQL (Docker)
docker run --name apiwatch-postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=apiwatch \
  -p 5432:5432 \
  -d postgres:14

# Run migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload
```

API will be available at `http://localhost:8000`

API Documentation: `http://localhost:8000/api/docs`

### Frontend Setup (Coming Soon)

```bash
cd frontend
npm install
npm run dev
```

## 🗄️ Database Schema

- **users** - User authentication
- **api_monitors** - Monitor configurations
- **health_checks** - Check results and metrics
- **incidents** - Downtime tracking

## 📝 API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and get JWT token
- `GET /api/v1/auth/me` - Get current user

### Monitors
- `POST /api/v1/monitors/` - Create monitor
- `GET /api/v1/monitors/` - List user's monitors
- `GET /api/v1/monitors/{id}` - Get monitor details
- `PUT /api/v1/monitors/{id}` - Update monitor
- `DELETE /api/v1/monitors/{id}` - Delete monitor

### Metrics (Coming Soon)
- `GET /api/v1/metrics/{monitor_id}/health-checks` - Get health check history
- `GET /api/v1/metrics/{monitor_id}/incidents` - Get incident history
- `GET /api/v1/metrics/{monitor_id}/stats` - Get statistics

## 🏗️ Project Structure

```
apiwatch/
├── backend/
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   ├── models/       # SQLAlchemy models
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── workers/      # Background tasks
│   │   ├── websocket/    # WebSocket handlers
│   │   └── utils/        # Utilities
│   ├── alembic/          # Database migrations
│   └── requirements.txt
└── frontend/             # React application (coming soon)
```

## 🔒 Security

- Passwords hashed with bcrypt
- JWT token authentication
- SQL injection protection via SQLAlchemy ORM
- CORS configuration
- Environment variable management

## 📊 Development Progress

- [x] Day 1: Project setup, database models, FastAPI foundation
- [x] Day 2: Authentication system, Monitor CRUD API
- [ ] Day 3: Background health checker, incident detection
- [ ] Day 4: Metrics API, health check history
- [ ] Day 5: React frontend, dashboard
- [ ] Day 6: WebSocket integration, real-time updates
- [ ] Day 7: Deployment, production setup

## 🤝 Contributing

This is a portfolio project, but feedback and suggestions are welcome!

## 📄 License

MIT License

## 👤 Author

**Said** - Backend AI Developer
- Building this as a portfolio project for senior developer interviews
- Showcasing FastAPI, PostgreSQL, React, and real-time systems

---

⭐ Star this repo if you find it useful!
