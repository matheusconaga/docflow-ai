from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
import os
import uuid

from app.core.security import get_current_user, verify_password, hash_password
from fastapi import HTTPException, status
from app.db.database import get_db
from app.models.user import User
from app.schemas.auth_schema import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UpdateProfileRequest,
    UpdatePasswordRequest,
    UserResponse,
)
from app.services.auth_service import (
    authenticate_user,
    create_user,
    generate_token_for_user,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=201)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new user and return a JWT token."""

    user = create_user(db, data)
    token = generate_token_for_user(user)

    return TokenResponse(
        access_token=token,
        user=UserResponse.model_validate(user),
    )


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate a user and return a JWT token."""

    user = authenticate_user(db, data.email, data.password)
    token = generate_token_for_user(user)

    return TokenResponse(
        access_token=token,
        user=UserResponse.model_validate(user),
    )


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)):
    """Return the currently authenticated user."""

    return UserResponse.model_validate(current_user)


@router.put("/profile", response_model=UserResponse)
def update_profile(
    data: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update the current user's profile."""

    update_data = data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(current_user, field, value)

    db.commit()
    db.refresh(current_user)

    return UserResponse.model_validate(current_user)

@router.put("/password")
def update_password(
    data: UpdatePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update the current user's password."""
    
    if not verify_password(data.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Senha atual incorreta."
        )
        
    current_user.password_hash = hash_password(data.new_password)
    db.commit()
    
    return {"message": "Senha atualizada com sucesso."}

@router.post("/avatar", response_model=UserResponse)
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Upload user avatar and update avatar_url."""
    
    # Create static avatars directory if it doesn't exist
    os.makedirs("app/static/avatars", exist_ok=True)
    
    # Generate unique filename
    ext = file.filename.split(".")[-1]
    filename = f"{current_user.id}_{uuid.uuid4().hex[:8]}.{ext}"
    file_path = f"app/static/avatars/{filename}"
    
    # Read file and write to disk
    contents = await file.read()
    with open(file_path, "wb") as f:
        f.write(contents)
    
    # Update user in DB
    # Saving relative path makes it easier to serve across different environments (localhost vs LAN IP)
    avatar_url = f"/static/avatars/{filename}"
    current_user.avatar_url = avatar_url
    
    db.commit()
    db.refresh(current_user)
    
    return UserResponse.model_validate(current_user)
