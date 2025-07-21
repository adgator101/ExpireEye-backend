# FastAPI Backend

Professional backend structure for FastAPI projects.
\n\n## Directory Structure Overview\n\n
```
fastapi_backend/
├── app/
│   ├── api/                # API route definitions (routers)
│   ├── core/               # Core settings, config, security
│   ├── models/             # Pydantic models and ORM models
│   ├── db/                 # Database session, migrations
│   ├── services/           # Business logic/services
│   ├── schemas/            # Request/response schemas
│   ├── utils/              # Utility/helper functions
│   ├── main.py             # FastAPI app entrypoint
│   └── dependencies.py     # Dependency injection
├── alembic/                # Database migrations (if using Alembic)
├── requirements.txt        # Python dependencies
├── README.md               # Project documentation
├── .env                    # Environment variables
├── .gitignore              # Git ignore rules
└── pyproject.toml          # Project metadata/config (optional)
```

### Folder & File Descriptions

  - **api/**: Contains API route definitions, organized by version (e.g., v1, v2).
  - **core/**: Core settings, configuration, and security logic.
  - **models/**: Database ORM models and Pydantic data models.
  - **db/**: Database session management and migration scripts.
  - **services/**: Business logic and service layer functions.
  - **schemas/**: Pydantic schemas for request and response validation.
  - **utils/**: Utility and helper functions.
  - **main.py**: FastAPI application entrypoint.
  - **dependencies.py**: Dependency injection functions for routes/services.

---

## How to Run the App

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Start the FastAPI server with Uvicorn:
   ```bash
   uvicorn app.main:app --reload
   ```
   - The `--reload` flag enables auto-reload on code changes (useful for development).
   - By default, the app will be available at http://127.0.0.1:8000

3. API documentation:
   - Swagger UI: http://127.0.0.1:8000/docs
   - ReDoc: http://127.0.0.1:8000/redoc

---


---

## Database Migrations with Alembic

For handling database migrations Alembic is used here. Below are the command and steps:

### 1. Initialize Alembic (only once, already done in this repo)
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

## .env Template

Create a `.env` file in your project root with the following content:

```env
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=your_db_host
DB_PORT=3306
DB_NAME=your_db_name
```

- Replace values with your actual credentials.


