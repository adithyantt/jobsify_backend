from sqlalchemy import Boolean, Column, Index, Integer, String

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, nullable=False, default="user", index=True)
    phone = Column(String, nullable=True)
    email_verified = Column(Boolean, default=False, index=True)
    blocked = Column(Boolean, default=False, index=True)

    __table_args__ = (
        Index('idx_users_role_blocked', 'role', 'blocked'),
        Index('idx_users_email_verified', 'email_verified'),
    )

    @property
    def display_name(self) -> str:
        full_name = " ".join(
            part.strip() for part in [self.first_name or "", self.last_name or ""] if part and part.strip()
        ).strip()
        if full_name:
            return full_name
        if self.email and "@" in self.email:
            return self.email.split("@")[0]
        return "User"
