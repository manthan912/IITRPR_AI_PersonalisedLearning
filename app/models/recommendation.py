"""
Recommendation model for AI-generated learning suggestions
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Recommendation(Base):
    __tablename__ = "recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False, index=True)
    learning_material_id = Column(Integer, ForeignKey("learning_materials.id"), nullable=False, index=True)
    
    # Recommendation details
    recommendation_type = Column(String(50), nullable=False)  # next_topic, review, challenge, remedial
    confidence_score = Column(Float, nullable=False)  # 0-1 confidence in recommendation
    priority_score = Column(Float, default=0.5)  # 0-1 priority level
    
    # Reasoning
    reasoning = Column(Text)  # Human-readable explanation
    ai_factors = Column(JSON, default={})  # Factors that influenced the recommendation
    
    # Timing and context
    optimal_time = Column(DateTime, nullable=True)  # When this should be studied
    estimated_duration = Column(Integer)  # Estimated time to complete (minutes)
    difficulty_adjustment = Column(Float, default=0.0)  # -1 to 1, adjust from base difficulty
    
    # Effectiveness tracking
    was_accepted = Column(Boolean, default=False)
    was_completed = Column(Boolean, default=False)
    effectiveness_score = Column(Float, nullable=True)  # How effective it was (post-completion)
    student_rating = Column(Float, nullable=True)  # Student's rating of the recommendation
    
    # Metadata
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime)  # When this recommendation expires
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    student = relationship("Student", back_populates="recommendations")
    learning_material = relationship("LearningMaterial")
    
    def __repr__(self):
        return f"<Recommendation(id={self.id}, student_id={self.student_id}, type='{self.recommendation_type}')>"