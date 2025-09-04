"""
Progress tracking model for student learning analytics
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Progress(Base):
    __tablename__ = "progress"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False, index=True)
    learning_material_id = Column(Integer, ForeignKey("learning_materials.id"), nullable=False, index=True)
    
    # Progress metrics
    completion_status = Column(String(20), default="not_started")  # not_started, in_progress, completed, abandoned
    completion_percentage = Column(Float, default=0.0)  # 0-100
    time_spent = Column(Integer, default=0)  # in minutes
    
    # Performance metrics
    score = Column(Float, nullable=True)  # Assessment score if applicable
    attempts = Column(Integer, default=1)
    correct_answers = Column(Integer, default=0)
    total_questions = Column(Integer, default=0)
    
    # Learning analytics
    interaction_data = Column(JSON, default={})  # Detailed interaction logs
    difficulty_rating = Column(Float, nullable=True)  # Student's rating of difficulty
    engagement_score = Column(Float, default=0.5)  # AI-calculated engagement
    
    # Adaptive learning data
    mastery_level = Column(Float, default=0.0)  # 0-1 scale
    confidence_score = Column(Float, default=0.0)  # Student's confidence
    learning_velocity = Column(Float, default=1.0)  # Speed of learning
    
    # Temporal data
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    last_accessed = Column(DateTime, server_default=func.now())
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    student = relationship("Student", back_populates="progress_records")
    learning_material = relationship("LearningMaterial", back_populates="progress_records")
    
    def __repr__(self):
        return f"<Progress(student_id={self.student_id}, material_id={self.learning_material_id}, status='{self.completion_status}')>"