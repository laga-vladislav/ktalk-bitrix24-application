from sqlalchemy import String, DateTime, Integer, Boolean, ForeignKeyConstraint, ForeignKey
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import datetime, timezone


class Base(AsyncAttrs, DeclarativeBase):
    pass


class PortalScheme(Base):
    __tablename__ = "portal"

    member_id: Mapped[str] = mapped_column(String, primary_key=True)
    client_endpoint: Mapped[str] = mapped_column(String, nullable=False)
    scope: Mapped[str] = mapped_column(String, nullable=False)

    ktalk_space = relationship("KtalkSpaceScheme", back_populates="portal")
    user = relationship("UserScheme", back_populates="portal")
    user_auth = relationship("UserAuthScheme", back_populates="portal", overlaps="user")


class KtalkSpaceScheme(Base):
    __tablename__ = "ktalk_space"
    
    member_id: Mapped[str] = mapped_column(String, ForeignKey(
        "portal.member_id",
        onupdate="CASCADE",
        ondelete="CASCADE"
    ), unique=True, primary_key=True)
    space: Mapped[str] = mapped_column(String, nullable=False)
    api_key: Mapped[str] = mapped_column(String, nullable=False)
    admin_email: Mapped[str] = mapped_column(String, nullable=False)

    portal = relationship("PortalScheme", back_populates="ktalk_space")


class UserScheme(Base):
    __tablename__ = "user"

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    member_id: Mapped[str] = mapped_column(String, ForeignKey(
        "portal.member_id",
        onupdate="CASCADE",
        ondelete="CASCADE"
    ), primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    last_name: Mapped[str] = mapped_column(String, nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, nullable=False)

    portal = relationship("PortalScheme", back_populates="user")
    user_auth = relationship(
        "UserAuthScheme",
        back_populates="user",
        overlaps="portal,user_auth",
        uselist=False
    )


class UserAuthScheme(Base):
    __tablename__ = 'user_auth'

    member_id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    access_token: Mapped[str] = mapped_column(String, nullable=False)
    refresh_token: Mapped[str] = mapped_column(String, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.now(timezone.utc), nullable=False
    )

    __table_args__ = (
        ForeignKeyConstraint(
            ['user_id', 'member_id'],
            ['user.user_id', 'user.member_id'],
            name='fk_user_auth_user',
            onupdate="CASCADE",
            ondelete="CASCADE"
        ),
        ForeignKeyConstraint(
            ['member_id'],
            ['portal.member_id'],
            name='fk_user_auth_portal',
            onupdate="CASCADE",
            ondelete="CASCADE"
        ),
    )

    user = relationship("UserScheme", back_populates="user_auth", overlaps="portal")
    portal = relationship("PortalScheme", back_populates="user_auth", overlaps="user")

    @property
    def client_endpoint(self):
        return self.portal.client_endpoint
    
    def to_dict(self):
        data = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        data['client_endpoint'] = self.client_endpoint
        return data
    