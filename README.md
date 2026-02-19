# CP'S Enterprise POS

<p align="center">
  <img src="assets/logo.png" alt="CP'S Enterprise POS Logo" width="200"/>
</p>

<p align="center">
  <strong>نظام نقاط بيع مؤسسي متقدم</strong><br>
  <strong>Enterprise Point of Sale System</strong>
</p>

<p align="center">
  <a href="#features">Features</a> •
  <a href="#tech-stack">Tech Stack</a> •
  <a href="#getting-started">Getting Started</a> •
  <a href="#api-documentation">API Docs</a> •
  <a href="#deployment">Deployment</a>
</p>

---

## 🌟 Features

### Core Features
- ✅ **Point of Sale (POS)** - Fast and intuitive checkout interface
- ✅ **Product Management** - Complete inventory control with barcode support
- ✅ **Sales Tracking** - Real-time sales monitoring and reporting
- ✅ **User Management** - Role-based access control (Admin, Manager, Cashier, Viewer)
- ✅ **Payment Processing** - Multiple payment methods (Cash, Card, Digital)
- ✅ **Receipt Generation** - Automatic receipt creation and printing
- ✅ **Refund Management** - Easy refund and return processing

### Advanced Features
- 🔐 **JWT Authentication** - Secure token-based authentication
- 📊 **Analytics Dashboard** - Comprehensive business insights
- 🔔 **Low Stock Alerts** - Automatic inventory notifications
- 📱 **Responsive Design** - Works on desktop, tablet, and mobile
- 🌐 **Multi-language Support** - Arabic and English
- 🌙 **Dark/Light Mode** - Theme switching
- 📈 **Real-time Reports** - Sales, inventory, and performance reports

---

## 🛠 Tech Stack

### Backend
- **FastAPI** - Modern, fast web framework
- **SQLAlchemy 2.0** - Async ORM for database operations
- **PostgreSQL** - Primary database
- **Redis** - Caching and session storage
- **Celery** - Background task processing
- **RabbitMQ** - Message broker

### Frontend
- **React 18** - UI library
- **TypeScript** - Type-safe development
- **Vite** - Build tool
- **TailwindCSS** - Utility-first CSS
- **shadcn/ui** - UI components
- **TanStack Query** - Data fetching
- **Zustand** - State management

### Infrastructure
- **Docker** - Containerization
- **Nginx** - Reverse proxy
- **Kubernetes** - Container orchestration
- **Prometheus + Grafana** - Monitoring
- **ELK Stack** - Logging

---

## 🚀 Getting Started

### Prerequisites

- Docker & Docker Compose
- Node.js 18+ (for local frontend development)
- Python 3.12+ (for local backend development)

### Quick Start with Docker

```bash
# Clone the repository
git clone https://github.com/your-org/cps-enterprise-pos.git
cd cps-enterprise-pos

# Copy environment file
cp .env.example .env

# Start all services
docker-compose up -d

# Run database migrations
docker-compose exec api alembic upgrade head

# Create admin user
docker-compose exec api python -c "
from src.database import AsyncSessionLocal
from src.models.user import User
from src.core.security import get_password_hash
import asyncio

async def create_admin():
    async with AsyncSessionLocal() as db:
        user = User(
            username='admin',
            email='admin@cps-enterprise.com',
            password_hash=get_password_hash('Admin123!'),
            first_name='Admin',
            last_name='User',
            role='admin',
            is_active=True
        )
        db.add(user)
        await db.commit()

asyncio.run(create_admin())
"
```

### Access the Application

- **API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Flower (Celery Monitor)**: http://localhost:5555
- **RabbitMQ Management**: http://localhost:15672

---

## 📚 API Documentation

### Authentication

```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=Admin123!"

# Response
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": { ... }
}
```

### Products

```bash
# List products
curl http://localhost:8000/api/v1/products \
  -H "Authorization: Bearer YOUR_TOKEN"

# Create product
curl -X POST http://localhost:8000/api/v1/products \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Wireless Mouse",
    "barcode": "1234567890123",
    "price": 29.99,
    "stock_quantity": 100
  }'
```

### Sales

```bash
# Create sale
curl -X POST http://localhost:8000/api/v1/sales \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {"product_id": "...", "quantity": 2}
    ],
    "payment": {"method": "cash", "amount": 59.98}
  }'
```

For complete API documentation, visit: http://localhost:8000/docs

---

## 🏗 Project Structure

```
cps-enterprise-pos/
├── 📁 backend/                 # FastAPI Backend
│   ├── src/
│   │   ├── core/              # Core modules (config, security, logging)
│   │   ├── models/            # Database models
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── api/v1/            # API routes
│   │   ├── services/          # Business logic
│   │   ├── repositories/      # Data access layer
│   │   └── main.py            # Application entry point
│   ├── alembic/               # Database migrations
│   ├── tests/                 # Test suite
│   └── Dockerfile
│
├── 📁 frontend/                # React Frontend (coming soon)
│
├── 📁 infrastructure/          # Infrastructure as Code
│   ├── docker/                # Docker configurations
│   ├── kubernetes/            # K8s manifests
│   ├── nginx/                 # Nginx configuration
│   └── terraform/             # Terraform scripts
│
├── 📁 docs/                    # Documentation
│   ├── ENTERPRISE_DEVELOPMENT_PLAN.md
│   ├── ARCHITECTURE.md
│   ├── API_SPECIFICATION.md
│   └── SECURITY.md
│
├── docker-compose.yml          # Docker Compose configuration
├── .env.example                # Environment variables template
└── README.md                   # This file
```

---

## 🧪 Testing

```bash
# Run backend tests
cd backend
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_auth.py
```

---

## 🚢 Deployment

### Production Deployment

```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Deploy
docker-compose -f docker-compose.prod.yml up -d
```

### Kubernetes Deployment

```bash
# Apply Kubernetes manifests
kubectl apply -f infrastructure/kubernetes/

# Check deployment status
kubectl get pods -n cps-enterprise
```

---

## 📊 Monitoring

### Prometheus Metrics

Access Prometheus metrics at: http://localhost:8000/metrics

### Grafana Dashboards

Import dashboards from `infrastructure/grafana/dashboards/`

### Health Checks

- **API Health**: http://localhost:8000/health
- **Database**: Check connection pool status
- **Redis**: Check cache connectivity

---

## 🔒 Security

- **Authentication**: JWT with refresh tokens
- **Authorization**: Role-based access control
- **HTTPS**: TLS 1.2+ required in production
- **CORS**: Configured for allowed origins only
- **Rate Limiting**: API endpoint protection
- **Input Validation**: Pydantic schema validation
- **SQL Injection**: Protected by SQLAlchemy ORM
- **XSS Protection**: Content Security Policy headers

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📝 License

This project is proprietary software owned by **CP'S™ Enterprise Tech Solution L.L.C.**

All rights reserved. Unauthorized copying, distribution, or use is strictly prohibited.

---

## 👥 Team

- **Ahmed Hajjaj Mohammad Hashem** - Founder & Lead Developer

---

## 📞 Support

For support, email: support@cps-enterprise.com

---

<p align="center">
  <strong>© 2026 CP'S™ Enterprise Tech Solution L.L.C.</strong><br>
  All Rights Reserved
</p>
