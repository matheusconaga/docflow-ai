from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.schemas.auth_schema import RegisterRequest


def create_user(db: Session, data: RegisterRequest) -> User:
    """Create a new user. Raises 409 if email already exists."""

    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Este email já está cadastrado",
        )

    user = User(
        name=data.name,
        email=data.email,
        password_hash=hash_password(data.password),
        role="teacher",
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def authenticate_user(db: Session, email: str, password: str) -> User:
    """Authenticate a user by email and password. Raises 401 on failure."""

    user = db.query(User).filter(User.email == email).first()

    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Conta desativada. Entre em contato com o suporte.",
        )

    return user


def generate_token_for_user(user: User) -> str:
    """Generate a JWT access token for the given user."""
    return create_access_token(data={"sub": user.id, "role": user.role})


def seed_admin_user(db: Session) -> None:
    """Create a default admin user if none exists."""

    admin = db.query(User).filter(User.role == "admin").first()

    if admin is None:
        admin_user = User(
            name="Administrador",
            email="admin@educassist.com",
            password_hash=hash_password("admin123"),
            role="admin",
        )
        db.add(admin_user)
        db.commit()
        print("✅ Admin seed criado: admin@educassist.com / admin123")
    else:
        print("ℹ️  Admin já existe, seed ignorado.")
