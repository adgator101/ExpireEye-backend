# ExpireEye Backend

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-red?style=for-the-badge&logo=sqlalchemy)](https://www.sqlalchemy.org/)

## Project Structure

```
ExpireEye-backend/
├── 📁 app/
│   ├── 📁 core/               # Core settings, config, security
│   ├── 📁 db/                 # Database session & configuration
│   ├── 📁 models/             # SQLAlchemy ORM models
│   │   ├── user_model.py      # User database model
│   │   ├── product_model.py   # Product database model
│   │   └── user_product.py    # User-Product relationship model
│   ├── 📁 routers/            # FastAPI route handlers
│   │   ├── auth.py            # Authentication endpoints
│   │   ├── warehouse.py       # Product management endpoints
│   │   └── user_inventory.py  # User inventory endpoints
│   ├── 📁 schemas/            # Pydantic request/response models
│   │   └── auth_schema.py     # Authentication schemas
│   ├── 📁 utils/              # Utility functions
│   │   ├── jwt.py             # JWT token utilities
│   │   └── errors.py          # Custom error handlers
│   ├── main.py                # FastAPI application entrypoint
│   └── dependencies.py        # Dependency injection
├── 📁 alembic/                # Database migrations
├── requirements.txt           # Python dependencies
├── .env.example              # Environment variables template
├── alembic.ini               # Alembic configuration
└── README.md                 # Project documentation
```

## Quick Start

### Prerequisites

- Python 3.8+
- MySQL/PostgreSQL database
- Virtual environment (recommended)

### 1. Clone & Setup

```bash
git clone https://github.com/adgator101/ExpireEye-backend
cd ExpireEye-backend

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

Create a `.env` file from the template:

```bash
cp .env.example .env
```

### 3. Database Setup

```bash
# Run database migrations
alembic upgrade head
```

### 4. Start the Server

```bash
uvicorn app.main:app --reload
```

**Your server is now running!**

- **API Base URL**: http://localhost:8000/api
- **Interactive Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

---

## Database Management

For handling database migrations Alembic is used here. Below are the command and steps:

### 1. Initialize Alembic (only once)

```bash
alembic init alembic
```

### 2. Generate a New Migration

Autogenerate migration scripts based on your models:

```bash
alembic revision --autogenerate -m "Migration message"
```

### 3. Apply Migrations

Upgrade your database to the latest revision:

```bash
alembic upgrade head
```

### 4. Downgrade (if needed)

Revert the last migration:

```bash
alembic downgrade -1
```

### 5. Alembic Configuration

- Edit `alembic.ini` for DB connection settings if needed.
- Edit `alembic/env.py` to set up model imports and metadata.

---
