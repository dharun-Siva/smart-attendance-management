from sqlalchemy import or_, select

import app.models
from app.core.database import SessionLocal
from app.core.security import hash_password, verify_password
from app.models.enums import UserRole
from app.models.user import User

ADMIN_USERNAME = "admin"
ADMIN_EMAIL = "admin@smartattendance.local"
ADMIN_PASSWORD = "Admin@123"


def seed_admin() -> str:
    with SessionLocal() as db:
        matches = db.scalars(
            select(User).where(
                or_(User.username == ADMIN_USERNAME, User.email == ADMIN_EMAIL)
            )
        ).all()
        if len({user.id for user in matches}) > 1:
            raise RuntimeError(
                "Cannot seed admin: the configured username and email belong to different users."
            )

        existing = matches[0] if matches else None
        if existing is not None:
            if existing.role != UserRole.ADMIN:
                raise RuntimeError(
                    "Cannot seed admin: the configured username or email belongs to a non-admin user."
                )
            changed = False
            if existing.email != ADMIN_EMAIL:
                existing.email = ADMIN_EMAIL
                changed = True
            if not verify_password(ADMIN_PASSWORD, existing.password_hash):
                existing.password_hash = hash_password(ADMIN_PASSWORD)
                changed = True
            if not existing.is_active:
                existing.is_active = True
                changed = True
            if changed:
                db.commit()
                return f"Existing Admin user updated (id={existing.id})."
            return f"Admin user already exists (id={existing.id})."

        db.add(
            User(
                username=ADMIN_USERNAME,
                email=ADMIN_EMAIL,
                password_hash=hash_password(ADMIN_PASSWORD),
                role=UserRole.ADMIN,
                is_active=True,
            )
        )
        db.commit()
        return "Admin user created successfully."


if __name__ == "__main__":
    print(seed_admin())
