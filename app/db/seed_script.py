import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from app.db.session import SessionLocal
from app.models.base_class import Base  # Cambiamos la importación
from app.models.user import User
from app.core.security import get_password_hash

def seed_database():
    db = SessionLocal()
    try:
        # Superadmin
        superadmin = {
            "email": "cborja@discdc.com",
            "full_name": "andres",
            "employee_id": "1155",
            "hashed_password": get_password_hash("admin123"),
            "is_active": True,
            "is_superuser": True
        }

        # Usuarios regulares
        regular_users = [
            {
                "email": "usuario1@discdc.com",
                "full_name": "Usuario Uno",
                "employee_id": "2001",
                "hashed_password": get_password_hash("user123"),
                "is_active": True,
                "is_superuser": False
            },
            {
                "email": "usuario2@discdc.com",
                "full_name": "Usuario Dos",
                "employee_id": "2002",
                "hashed_password": get_password_hash("user123"),
                "is_active": True,
                "is_superuser": False
            },
            {
                "email": "usuario3@discdc.com",
                "full_name": "Usuario Tres",
                "employee_id": "2003",
                "hashed_password": get_password_hash("user123"),
                "is_active": True,
                "is_superuser": False
            },
            {
                "email": "usuario4@discdc.com",
                "full_name": "Usuario Cuatro",
                "employee_id": "2004",
                "hashed_password": get_password_hash("user123"),
                "is_active": True,
                "is_superuser": False
            },
            {
                "email": "usuario5@discdc.com",
                "full_name": "Usuario Cinco",
                "employee_id": "2005",
                "hashed_password": get_password_hash("user123"),
                "is_active": True,
                "is_superuser": False
            }
        ]

        # Verificar superadmin
        existing_admin = db.query(User).filter(User.email == superadmin["email"]).first()
        if not existing_admin:
            db.add(User(**superadmin))
            print(f"Superadmin creado: {superadmin['email']}")
        else:
            print(f"Superadmin ya existe: {superadmin['email']}")

        # Crear usuarios regulares
        for user_data in regular_users:
            existing_user = db.query(User).filter(User.email == user_data["email"]).first()
            if not existing_user:
                db.add(User(**user_data))
                print(f"Usuario regular creado: {user_data['email']}")
            else:
                print(f"Usuario ya existe: {user_data['email']}")

        db.commit()
        print("Base de datos poblada exitosamente")

    except Exception as e:
        print(f"Error poblando la base de datos: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("Iniciando población de la base de datos...")
    seed_database()
    print("Proceso completado.")
