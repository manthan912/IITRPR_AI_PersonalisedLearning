"""
Student management API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.database import get_db
from app.models.student import Student
from app.models.progress import Progress
from app.models.learning_style import LearningStyle
from app.api.auth import get_current_user
from app.services.learning_style_detector import LearningStyleDetector
from app.services.progress_analytics import ProgressAnalytics

router = APIRouter()

# Pydantic models
class StudentProfile(BaseModel):
    id: int
    username: str
    email: str
    first_name: str
    last_name: str
    learning_style_scores: Optional[dict] = None
    dominant_learning_style: Optional[str] = None
    difficulty_preference: Optional[str] = None
    performance_score: float
    learning_streak: int
    total_study_time: int

class StudentUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    difficulty_preference: Optional[str] = None

class LearningStyleAssessment(BaseModel):
    visual_score: float
    auditory_score: float
    kinesthetic_score: float
    reading_writing_score: float


@router.get("/profile", response_model=StudentProfile)
async def get_student_profile(current_user: Student = Depends(get_current_user)):
    """Get current student's profile"""
    return StudentProfile(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        learning_style_scores=current_user.learning_style_scores,
        dominant_learning_style=current_user.dominant_learning_style,
        difficulty_preference=current_user.difficulty_preference,
        performance_score=current_user.performance_score,
        learning_streak=current_user.learning_streak,
        total_study_time=current_user.total_study_time
    )


@router.put("/profile")
async def update_student_profile(
    profile_update: StudentUpdate, 
    current_user: Student = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update student profile"""
    if profile_update.first_name:
        current_user.first_name = profile_update.first_name
    if profile_update.last_name:
        current_user.last_name = profile_update.last_name
    if profile_update.difficulty_preference:
        current_user.difficulty_preference = profile_update.difficulty_preference
    
    current_user.updated_at = datetime.now()
    db.commit()
    
    return {"message": "Profile updated successfully"}


@router.post("/learning-style-assessment")
async def submit_learning_style_assessment(
    assessment: LearningStyleAssessment,
    current_user: Student = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit or update learning style assessment"""
    
    # Update student's learning style scores
    style_scores = {
        'visual': assessment.visual_score,
        'auditory': assessment.auditory_score,
        'kinesthetic': assessment.kinesthetic_score,
        'reading_writing': assessment.reading_writing_score
    }
    
    # Find dominant learning style
    dominant_style = max(style_scores.items(), key=lambda x: x[1])[0]
    
    # Update student record
    current_user.learning_style_scores = style_scores
    current_user.dominant_learning_style = dominant_style
    current_user.updated_at = datetime.now()
    
    # Create or update LearningStyle record
    learning_style = db.query(LearningStyle).filter(
        LearningStyle.student_id == current_user.id
    ).first()
    
    if learning_style:
        learning_style.visual_score = assessment.visual_score
        learning_style.auditory_score = assessment.auditory_score
        learning_style.kinesthetic_score = assessment.kinesthetic_score
        learning_style.reading_writing_score = assessment.reading_writing_score
        learning_style.updated_at = datetime.now()
    else:
        learning_style = LearningStyle(
            student_id=current_user.id,
            visual_score=assessment.visual_score,
            auditory_score=assessment.auditory_score,
            kinesthetic_score=assessment.kinesthetic_score,
            reading_writing_score=assessment.reading_writing_score
        )
        db.add(learning_style)
    
    db.commit()
    
    return {
        "message": "Learning style assessment updated",
        "dominant_style": dominant_style,
        "style_scores": style_scores
    }


@router.get("/analytics")
async def get_student_analytics(
    current_user: Student = Depends(get_current_user),
    db: Session = Depends(get_db),
    days: int = 30
):
    """Get comprehensive analytics for current student"""
    
    # Get progress records
    progress_records = db.query(Progress).filter(
        Progress.student_id == current_user.id
    ).all()
    
    # Generate analytics
    analytics_service = ProgressAnalytics()
    analysis = analytics_service.analyze_student_performance(
        current_user, progress_records, days
    )
    
    return analysis


@router.get("/learning-style")
async def get_learning_style_analysis(
    current_user: Student = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get AI-detected learning style based on behavioral data"""
    
    # Get progress records for analysis
    progress_records = db.query(Progress).filter(
        Progress.student_id == current_user.id
    ).all()
    
    # Detect learning style
    detector = LearningStyleDetector()
    detected_styles = detector.detect_learning_style(current_user, progress_records)
    
    return {
        "detected_styles": detected_styles,
        "current_styles": current_user.learning_style_scores,
        "dominant_style": max(detected_styles.items(), key=lambda x: x[1])[0],
        "confidence": max(detected_styles.values()),
        "analysis_date": datetime.now().isoformat()
    }