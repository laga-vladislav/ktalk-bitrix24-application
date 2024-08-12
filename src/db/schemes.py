from sqlalchemy import ForeignKey
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import datetime


class Base(AsyncAttrs, DeclarativeBase):
    pass


class PortalScheme(Base):
    __tablename__ = "portal"

    member_id: Mapped[str] = mapped_column(primary_key=True)
    endpoint: Mapped[str] = mapped_column()
    scope: Mapped[str] = mapped_column()


class AuthScheme(Base):
    __tablename__ = "auth"

    id_auth: Mapped[int] = mapped_column(primary_key=True)
    access_token: Mapped[str]
    refresh_token: Mapped[str]
    created_at: Mapped[datetime]


class UserScheme(Base):
    __tablename__ = "user"

    user_id: Mapped[int] = mapped_column(primary_key=True)
    member_id: Mapped[str] = mapped_column(
        ForeignKey(PortalScheme.member_id), primary_key=True)
    id_auth: Mapped[int] = mapped_column(ForeignKey(AuthScheme.id_auth))
    is_admin: Mapped[bool] = mapped_column(default=False)