"""
Student model for the personalized learning system
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Student(Base):
    __tablename__ = "students"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
    # Personal information
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    age = Column(Integer)
    
    # Learning profile
    learning_style_scores = Column(JSON, default={})  # Scores for each learning style
    dominant_learning_style = Column(String(50))  # visual, auditory, kinesthetic, reading_writing
    difficulty_preference = Column(String(20), default="intermediate")
    
    # System tracking
    total_study_time = Column(Integer, default=0)  # in minutes
    learning_streak = Column(Integer, default=0)  # consecutive days
    performance_score = Column(Float, default=0.0)  # 0-100 scale
    
    # Adaptive learning parameters
    learning_rate = Column(Float, default=1.0)  # How quickly they learn
    retention_rate = Column(Float, default=0.8)  # How well they retain information
    motivation_level = Column(Float, default=0.5)  # 0-1 scale
    
    # Metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    last_login = Column(DateTime)
    
    # Relationships
    progress_records = relationship("Progress", back_populates="student")
    recommendations = relationship("Recommendation", back_populates="student")
    
    def __repr__(self):
        return f"<Student(id={self.id}, username='{self.username}')>"