# test_data_generator.py
from datetime import datetime, timedelta
import random
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.access_log import AccessLog
from app.core.security import encrypt_fingerprint

def generate_test_data(db: Session):
    """Genera datos de prueba para el sistema de acceso biométrico"""
    
    # 1. Crear usuarios de prueba
    test_users = [
        {
            "email": "user1@test.com",
            "full_name": "Usuario Activo",
            "employee_id": "2024001",
            "is_active": True,
            "fingerprint_template": encrypt_fingerprint("template_activo_1")
        },
        {
            "email": "user2@test.com",
            "full_name": "Usuario Inactivo",
            "employee_id": "2024002",
            "is_active": False,
            "fingerprint_template": encrypt_fingerprint("template_inactivo_1")
        },
        {
            "email": "user3@test.com",
            "full_name": "Juan Pérez",
            "employee_id": "2024003",
            "is_active": True,
            "fingerprint_template": encrypt_fingerprint("template_activo_2")
        },
        {
            "email": "user4@test.com",
            "full_name": "María García",
            "employee_id": "2024004",
            "is_active": True,
            "fingerprint_template": encrypt_fingerprint("template_activo_3")
        }
    ]

    created_users = []
    for user_data in test_users:
        user = User(
            email=user_data["email"],
            full_name=user_data["full_name"],
            employee_id=user_data["employee_id"],
            is_active=user_data["is_active"],
            fingerprint_template=user_data["fingerprint_template"],
            hashed_password="$2b$12$D8L2kP5kXAALFyfvR4MbX.Dt6D1E7eo22ADp.Uf3p6RjpYWsjNrEy"  # password123
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        created_users.append(user)
    
    # 2. Generar registros de acceso históricos
    start_date = datetime.now() - timedelta(days=30)  # Último mes
    end_date = datetime.now()
    
    access_types = ["entry", "exit"]
    devices = ["MAIN_DOOR", "SIDE_DOOR", "GARAGE"]
    statuses = ["success", "denied"]

    # Generar registros para cada usuario
    for user in created_users:
        # Determinar cuántos registros generar para este usuario
        num_records = random.randint(20, 50)
        
        for _ in range(num_records):
            # Generar timestamp aleatorio entre start_date y end_date
            random_timestamp = start_date + timedelta(
                seconds=random.randint(0, int((end_date - start_date).total_seconds()))
            )
            
            # Si el usuario está inactivo, algunos registros deberían ser denegados
            status = "denied" if not user.is_active and random.random() < 0.7 else "success"
            
            access_log = AccessLog(
                user_id=user.id,
                access_type=random.choice(access_types),
                device_id=random.choice(devices),
                status=status,
                timestamp=random_timestamp
            )
            db.add(access_log)
    
    db.commit()
    
    print("Datos de prueba generados exitosamente:")
    print(f"- {len(created_users)} usuarios creados")
    print(f"- Registros de acceso generados para el período: {start_date.date()} - {end_date.date()}")
    
    return created_users


def clear_test_data(db: Session):
    """Limpia solo los datos de prueba de la base de datos"""
    # Eliminar solo los registros de acceso de usuarios de prueba
    test_emails = ["user1@test.com", "user2@test.com", "user3@test.com", "user4@test.com"]

    # Primero obtener los IDs de usuarios de prueba
    test_users = db.query(User).filter(User.email.in_(test_emails)).all()
    test_user_ids = [user.id for user in test_users]

    # Eliminar los registros de acceso de estos usuarios
    if test_user_ids:
        db.query(AccessLog).filter(AccessLog.user_id.in_(test_user_ids)).delete()

    # Eliminar solo los usuarios de prueba
    db.query(User).filter(User.email.in_(test_emails)).delete()

    db.commit()
    print("Datos de prueba eliminados exitosamente")

# Ejemplo de uso:

from app.db.session import SessionLocal

def main():
    db = SessionLocal()
    try:
        generate_test_data(db)
        #clear_test_data(db)
        print("¡Proceso completado!")
    finally:
        db.close()

if __name__ == "__main__":
    main()

