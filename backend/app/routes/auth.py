from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from app.schemas.auth import LoginRequest, RegisterRequest
from app.utils.errors import AuthError
from app.models.user import User
from app.db.session import get_db
import bcrypt
from datetime import datetime
from app.utils.jwt import create_access_token
from sqlalchemy.exc import SQLAlchemyError

router = APIRouter()


@router.post("/login")
def login(data: LoginRequest, response: Response, db: Session = Depends(get_db)):
    try:
        email = data.email
        password = data.password

        if not email:
            raise HTTPException(detail="Email is required")
        if not password:
            raise HTTPException(detail="Password is required")

        user = db.query(User).filter(User.email == email).first()

        if not user:
            raise AuthError(status_code=401, detail="Invalid email or password")

        if not bcrypt.checkpw(password.encode("utf-8"), user.password.encode("utf-8")):
            raise AuthError(status_code=401, detail="Invalid email or password")

        # Generate JWT token
        access_token = create_access_token(
            data={"userId": user.id, "email": user.email}
        )

        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            max_age=10 * 24 * 60 * 60,  # 10 days in seconds
        )

        return {
            "message": "Login successful",
            "token": access_token,
        }

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/signup")
def signup(data: RegisterRequest, db: Session = Depends(get_db)):
    try:

        name = data.name
        email = data.email
        password = data.password
        dob = data.dob

        # Check if user already exists
        existing_user = db.query(User).filter(User.email == email).first()

        if existing_user:
            raise HTTPException(status_code=409, detail="User already exists")

        if not email:
            raise HTTPException(status_code=400, detail="Email is required")

        if not password:
            raise HTTPException(status_code=400, detail="Password is required")

        if not dob:
            dob = ""

        if password and len(password) < 6:
            raise HTTPException(
                status_code=400, detail="Password must be at least 6 characters long"
            )

        new_user = User(
            name=name,
            email=email,
            password=bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode(
                "utf-8"
            ),
            # password = password,
            dob=dob,
            created_at=datetime.utcnow().isoformat(),
        )
        # Add user to the database
        db.add(new_user)
        # Commit the transaction
        db.commit()
        db.refresh(new_user)

        return {
            "message": "User created successfully",
            "userId": new_user.id,
            "email": new_user.email,
            "dob": new_user.dob,
            "created_at": new_user.created_at,
        }
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Internal server error")
