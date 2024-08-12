from sqlalchemy import ForeignKey, String, Integer, Boolean, DateTime
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import datetime, timezone


class Base(AsyncAttrs, DeclarativeBase):
    pass


class PortalScheme(Base):
    __tablename__ = "portal"

    member_id: Mapped[str] = mapped_column(String, primary_key=True)
    endpoint: Mapped[str] = mapped_column(String, nullable=False)
    scope: Mapped[str] = mapped_column(String, nullable=False)


class AuthScheme(Base):
    __tablename__ = "auth"

    id_auth: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    access_token: Mapped[str] = mapped_column(String, nullable=False)
    refresh_token: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.now(timezone.utc), nullable=False
    )


class UserScheme(Base):
    __tablename__ = "user"

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    member_id: Mapped[str] = mapped_column(
        String, ForeignKey(PortalScheme.member_id), primary_key=True
    )
    id_auth: Mapped[int] = mapped_column(
        Integer, ForeignKey(AuthScheme.id_auth), nullable=False
    )
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
