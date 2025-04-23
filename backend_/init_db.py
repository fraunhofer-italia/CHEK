from sqlalchemy.orm import sessionmaker
from api.models.models import User
from api.schemas.schemas import CreateUser
from api.utils.utils import hash_pass
from database import engine, Base
import os

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

def create_admin_user():
    admin_email = os.getenv('ADMIN_EMAIL', '')
    admin_password = os.getenv('ADMIN_PASSWORD', '')

    db = SessionLocal()

    try:
        admin_user = db.query(User).filter(User.email == admin_email).first()
        if not admin_user:
            admin_user_data = CreateUser(
                email=admin_email,
                password=admin_password,
                first_name="Admin",
                last_name="Fraunhofer ITALIA",
                municipality="Bolzano",
                city="Bolzano",
                country="Italy",
                language="English",
                zip_code="39100",
                role="admin"
            )
            hashed_password = hash_pass(admin_user_data.password)
            new_admin_user = User(
                email=admin_user_data.email,
                password=hashed_password,
                role=admin_user_data.role,
                first_name=admin_user_data.first_name,
                last_name=admin_user_data.last_name,
                municipality=admin_user_data.municipality,
                city=admin_user_data.city,
                country=admin_user_data.country,
                language=admin_user_data.language,
                zip_code=admin_user_data.zip_code,
                email_active=True
            )
            db.add(new_admin_user)
            db.commit()
            db.refresh(new_admin_user)
            print(f"Admin user created with email: {admin_email}")
        else:
            print(f"Admin user already exists with email: {admin_email}")
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_user()