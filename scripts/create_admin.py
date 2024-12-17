# scripts/create_admin.py
# import os
# import sys
# from pathlib import Path
# from sqlalchemy.orm import Session
# from app.db.session import SessionLocal
# from app.models.user import User
# from app.core.security import get_password_hash
#
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sys
import os
from pathlib import Path
from app.db.session import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash

# Agregar el directorio raíz del proyecto al path
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))


def create_first_admin():
    db = SessionLocal()
    try:
        # Verificar si ya existe un admin
        admin_exists = db.query(User).filter(User.is_superuser == True).first()
        if admin_exists:
            print("Ya existe un usuario administrador")
            return

        # Crear admin
        admin = User(
            email="admin@example.com",
            full_name="Admin User",
            employee_id="ADMIN001",
            hashed_password=get_password_hash("admin123"),
            is_active=True,
            is_superuser=True
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        print("Usuario administrador creado exitosamente")
        print("Email: admin@example.com")
        print("Password: admin123")

    except Exception as e:
        print(f"Error creando el administrador: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    create_first_admin()
