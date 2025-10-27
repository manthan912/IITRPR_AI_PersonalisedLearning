"""
Learning Style model for tracking and analyzing student learning preferences
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class LearningStyle(Base):
    __tablename__ = "learning_styles"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False, index=True)
    
    # VARK Learning Style scores (0-1 scale)
    visual_score = Column(Float, default=0.25)      # Charts, diagrams, images
    auditory_score = Column(Float, default=0.25)    # Lectures, discussions, audio
    kinesthetic_score = Column(Float, default=0.25) # Hands-on, movement, practice
    reading_writing_score = Column(Float, default=0.25)  # Text, reading, writing
    
    # Additional learning preferences
    social_vs_solitary = Column(Float, default=0.5)  # 0=solitary, 1=social
    sequential_vs_global = Column(Float, default=0.5)  # 0=sequential, 1=global
    intuitive_vs_sensing = Column(Float, default=0.5)  # 0=sensing, 1=intuitive
    
    # Behavioral patterns
    preferred_session_length = Column(Integer, default=30)  # in minutes
    optimal_time_of_day = Column(String(20), default="morning")  # morning, afternoon, evening
    break_frequency = Column(Integer, default=15)  # minutes between breaks
    
    # AI-detected patterns
    attention_span = Column(Float, default=30.0)  # in minutes
    learning_momentum = Column(Float, default=0.5)  # How well they build on previous knowledge
    mistake_tolerance = Column(Float, default=0.5)  # How they handle making mistakes
    
    # Confidence levels by subject
    subject_confidence = Column(JSON, default={})  # {subject: confidence_score}
    
    # Assessment metadata
    last_assessment_date = Column(DateTime)
    assessment_count = Column(Integer, default=0)
    confidence_level = Column(Float, default=0.5)  # How confident we are in this profile
    
    # Metadata
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    student = relationship("Student")
    
    def get_dominant_learning_style(self):
        """Return the dominant learning style based on scores"""
        scores = {
            'visual': self.visual_score,
            'auditory': self.auditory_score,
            'kinesthetic': self.kinesthetic_score,
            'reading_writing': self.reading_writing_score
        }
        return max(scores.items(), key=lambda x: x[1])[0]
    
    def __repr__(self):
        return f"<LearningStyle(student_id={self.student_id}, dominant='{self.get_dominant_learning_style()}')>"