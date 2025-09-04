"""
Learning Material model for storing educational content
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class ContentType(enum.Enum):
    TEXT = "text"
    VIDEO = "video"
    AUDIO = "audio"
    INTERACTIVE = "interactive"
    QUIZ = "quiz"
    SIMULATION = "simulation"


class DifficultyLevel(enum.Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class LearningMaterial(Base):
    __tablename__ = "learning_materials"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    
    # Content information
    content_type = Column(Enum(ContentType), nullable=False)
    content_url = Column(String(500))  # URL to actual content
    content_text = Column(Text)  # Text content for text-based materials
    
    # Learning attributes
    subject = Column(String(100), nullable=False, index=True)
    topic = Column(String(100), nullable=False, index=True)
    difficulty_level = Column(Enum(DifficultyLevel), nullable=False)
    estimated_duration = Column(Integer)  # in minutes
    
    # Personalization attributes
    learning_styles = Column(JSON, default=[])  # List of suitable learning styles
    prerequisites = Column(JSON, default=[])  # List of prerequisite material IDs
    tags = Column(JSON, default=[])  # Additional tags for categorization
    
    # AI features
    content_embedding = Column(JSON)  # Vector embedding of content for similarity matching
    keywords = Column(JSON, default=[])  # Extracted keywords
    complexity_score = Column(Float, default=0.5)  # 0-1 scale
    
    # Quality metrics
    average_rating = Column(Float, default=0.0)
    completion_rate = Column(Float, default=0.0)  # How often students complete this material
    effectiveness_score = Column(Float, default=0.0)  # How effective it is for learning
    
    # Metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    created_by = Column(String(100))  # Instructor/admin who created it
    
    # Relationships
    progress_records = relationship("Progress", back_populates="learning_material")
    
    def __repr__(self):
        return f"<LearningMaterial(id={self.id}, title='{self.title}', subject='{self.subject}')>"