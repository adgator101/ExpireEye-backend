# ExpireEye

This repository contains both the backend (FastAPI, Alembic, SQLAlchemy) and frontend (React, Vite, Tailwind CSS, Shadcn UI) for the ExpireEye project.

## Structure

```
backend/   # FastAPI backend
frontend/  # React frontend
.gitignore # Root ignore rules
```

## Backend

- Located in `backend/`
- FastAPI REST API
- Alembic for migrations
- SQLAlchemy ORM

## Frontend

- Located in `frontend/`
- React (Vite)
- React Router for routing
- Shadcn UI for components

## Getting Started

### Backend

```sh
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```sh
cd frontend
npm install
npm run dev
```

## Development Notes

- Keep secrets in `backend/.env` (not committed)
- Use `credentials: "include"` in frontend fetch/axios for cookie-based auth
- All code and config for backend and frontend are separated for clarity

## License

MIT
