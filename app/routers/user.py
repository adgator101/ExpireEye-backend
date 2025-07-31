from fastapi import APIRouter, Depends, HTTPException, Response, Request
from app.models.user_model import User
from app.db.session import get_db
from sqlalchemy.orm import Session
from app.utils.errors import AuthError
from app.schemas.auth_schema import LoginRequest, RegisterRequest

router = APIRouter()


@router.get("/profile")
def get_user_profile(
    response: Response, request: Request, db: Session = Depends(get_db)
):
    access_token = request.state.user
    user_id = access_token.get("userId")

    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "id": user.id,
        "name": user.name,
        "dob": user.dob,
        "email": user.email,
        "createdAt": user.created_at,
        "updatedAt": user.updated_at,
    }
