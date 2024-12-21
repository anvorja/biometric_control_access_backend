from datetime import timedelta
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder

from app.core.config import get_settings
from app.core.security import create_access_token, get_password_hash, verify_password
from app.api import deps
from app.schemas import user as user_schemas
from app.models.user import User

settings = get_settings()
router = APIRouter()


@router.post("/register", response_model=user_schemas.User)
def register_user(
        *,
        db: Session = Depends(deps.get_db),
        user_in: user_schemas.UserCreate,
        # is_admin: bool = Query(True, description="Crear como administrador")  # Parámetro temporal
) -> Any:
    """
    Registrar un nuevo usuario.
    """
    # Verificar si el email ya existe
    user = db.query(User).filter(User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="Este correo ya está registrado en el sistema."
        )

    # Verificar si el employee_id ya existe
    user = db.query(User).filter(User.employee_id == user_in.employee_id).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="Este ID de empleado ya está registrado."
        )

    # Crear el usuario
    user = User(
        email=user_in.email,
        full_name=user_in.full_name,
        employee_id=user_in.employee_id,
        hashed_password=get_password_hash(user_in.password),
        is_active=True,
        # is_superuser=is_admin  # Aquí usamos el nuevo parámetro
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login")
def login(
        db: Session = Depends(deps.get_db),
        form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    Login OAuth2 compatible con obtención de token JWT.
    Solo para administradores.
    """
    user = db.query(User).filter(User.email == form_data.username).first()

    # Primero verificamos si es superuser
    if not user or not user.is_superuser:
        print("Solo ingreso permitido a Superusuarios")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Acceso permitido solo para administradores",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Luego verificamos la contraseña
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Contraseña incorrecta",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario inactivo"
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {
        "access_token": token,
        "token_type": "bearer"
    }


@router.post("/logout")
async def logout(current_user: User = Depends(deps.get_current_user)):
    """
    Endpoint para registrar el logout del usuario
    """
    print("------- Logout Endpoint Hit -------")
    print(f"User: {current_user.email}")
    print(f"ID: {current_user.id}")
    print(f"Full name: {current_user.full_name}")
    print("----------------------------------")
    return {"message": f"Logout exitoso para usuario {current_user.email}"}


@router.get("/me", response_model=user_schemas.User)
def read_current_user(
        current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Obtener usuario actual.
    """
    return current_user


@router.put("/me", response_model=user_schemas.User)
def update_current_user(
        *,
        db: Session = Depends(deps.get_db),
        current_user: User = Depends(deps.get_current_user),
        user_in: user_schemas.UserUpdate,
) -> Any:
    """
    Actualizar usuario actual.
    """
    # Si se está actualizando el email, verificar que no exista
    if user_in.email and user_in.email != current_user.email:
        user = db.query(User).filter(User.email == user_in.email).first()
        if user:
            raise HTTPException(
                status_code=400,
                detail="Este correo ya está registrado."
            )

    # Actualizar los campos que vienen en la petición
    for field, value in user_in.model_dump(exclude_unset=True).items():
        if field == "password" and value:
            setattr(current_user, "hashed_password", get_password_hash(value))
        else:
            setattr(current_user, field, value)

    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user


@router.patch("/me", response_model=user_schemas.User)
def partial_update_user(
        *,
        db: Session = Depends(deps.get_db),
        current_user: User = Depends(deps.get_current_user),
        user_in: user_schemas.UserUpdate,
) -> Any:
    """
    Actualizar parcialmente datos del usuario actual.
    Solo actualiza los campos que se envían.
    """
    stored_user_data = jsonable_encoder(current_user)
    update_data = user_in.model_dump(exclude_unset=True)

    # Si se está actualizando el email, verificar que no exista
    if "email" in update_data and update_data["email"] != current_user.email:
        if db.query(User).filter(User.email == update_data["email"]).first():
            raise HTTPException(
                status_code=400,
                detail="Este correo ya está registrado."
            )

    # Al actualizar la contraseña, hashearla
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))

    for field in stored_user_data:
        if field in update_data:
            setattr(current_user, field, update_data[field])

    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user


@router.get("/users", response_model=List[user_schemas.User])
def get_users(
        db: Session = Depends(deps.get_db),
        current_user: User = Depends(deps.get_current_admin)
):
    """
    Obtener todos los usuarios (solo admin)
    """
    users = db.query(User).all()
    # Verifica que los usuarios tengan el campo fingerprint_template
    # print("Users with fingerprints:", [
    #     (u.id, bool(u.fingerprint_template)) for u in users
    # ])

    return users

@router.get("/users/{user_id}", response_model=user_schemas.User)
def get_user(
    user_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_admin)
) -> Any:
    """
    Obtener un usuario por ID
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail="Usuario no encontrado"
        )
    return user


@router.put("/users/{user_id}", response_model=user_schemas.User)
def update_user(
        user_id: int,
        user_in: user_schemas.UserUpdate,
        db: Session = Depends(deps.get_db),
        current_user: User = Depends(deps.get_current_admin)
) -> Any:
    """Actualizar un usuario por ID (solo admin)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    for field, value in user_in.model_dump(exclude_unset=True).items():
        if field == "password":
            user.hashed_password = get_password_hash(value)
        else:
            setattr(user, field, value)

    db.add(user)
    db.commit()
    db.refresh(user)
    return user