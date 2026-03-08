from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, Integer, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    total_score: Mapped[int] = mapped_column(Integer, default=0)
    current_title: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    qualifications: Mapped[List["UserQualification"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

class Qualification(Base):
    __tablename__ = "qualifications"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    category: Mapped[str] = mapped_column(String(50), index=True)
    tier: Mapped[int] = mapped_column(Integer)
    base_score: Mapped[int] = mapped_column(Integer)
    affiliate_link: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Relationships
    user_qualifications: Mapped[List["UserQualification"]] = relationship(
        back_populates="qualification"
    )
    synergy_requirements: Mapped[List["SynergyRequirement"]] = relationship(
        back_populates="qualification"
    )

class UserQualification(Base):
    __tablename__ = "user_qualifications"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    qualification_id: Mapped[int] = mapped_column(ForeignKey("qualifications.id"), index=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user: Mapped["User"] = relationship(back_populates="qualifications")
    qualification: Mapped["Qualification"] = relationship(back_populates="user_qualifications")

class Synergy(Base):
    __tablename__ = "synergies"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    title_name: Mapped[str] = mapped_column(String(100), unique=True)
    bonus_score: Mapped[int] = mapped_column(Integer)
    description: Mapped[str] = mapped_column(String(500))
    
    # Relationships
    requirements: Mapped[List["SynergyRequirement"]] = relationship(
        back_populates="synergy", cascade="all, delete-orphan"
    )

class SynergyRequirement(Base):
    __tablename__ = "synergy_requirements"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    synergy_id: Mapped[int] = mapped_column(ForeignKey("synergies.id"), index=True)
    
    # 必須カテゴリ（特定の資格ではなくカテゴリ単位で要求される場合）
    required_category: Mapped[Optional[str]] = mapped_column(String(50), nullable=True) 
    # 必須資格（特定の資格が要求される場合）
    required_qualification_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("qualifications.id"), nullable=True
    )
    
    # Relationships
    synergy: Mapped["Synergy"] = relationship(back_populates="requirements")
    qualification: Mapped[Optional["Qualification"]] = relationship(
        back_populates="synergy_requirements"
    )
