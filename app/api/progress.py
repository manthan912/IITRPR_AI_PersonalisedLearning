"""
Progress tracking API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.database import get_db
from app.models.progress import Progress
from app.models.learning_material import LearningMaterial
from app.models.student import Student
from app.api.auth import get_current_user
from app.services.learning_style_detector import LearningStyleDetector

router = APIRouter()

# Pydantic models
class ProgressCreate(BaseModel):
    learning_material_id: int
    completion_percentage: float
    time_spent: int  # minutes
    score: Optional[float] = None
    difficulty_rating: Optional[float] = None
    interaction_data: Optional[dict] = None

class ProgressUpdate(BaseModel):
    completion_percentage: Optional[float] = None
    time_spent: Optional[int] = None
    score: Optional[float] = None
    completion_status: Optional[str] = None
    difficulty_rating: Optional[float] = None
    confidence_score: Optional[float] = None
    interaction_data: Optional[dict] = None

class ProgressResponse(BaseModel):
    id: int
    learning_material_id: int
    material_title: str
    subject: str
    topic: str
    completion_status: str
    completion_percentage: float
    time_spent: int
    score: Optional[float]
    mastery_level: float
    created_at: datetime
    updated_at: datetime


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_progress_record(
    progress_data: ProgressCreate,
    current_user: Student = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new progress record"""
    
    # Verify learning material exists
    material = db.query(LearningMaterial).filter(
        LearningMaterial.id == progress_data.learning_material_id
    ).first()
    
    if not material:
        raise HTTPException(status_code=404, detail="Learning material not found")
    
    # Check if progress record already exists
    existing_progress = db.query(Progress).filter(
        Progress.student_id == current_user.id,
        Progress.learning_material_id == progress_data.learning_material_id
    ).first()
    
    if existing_progress:
        raise HTTPException(
            status_code=400, 
            detail="Progress record already exists. Use PUT to update."
        )
    
    # Determine completion status
    completion_status = "not_started"
    if progress_data.completion_percentage > 0:
        completion_status = "in_progress"
    if progress_data.completion_percentage >= 100:
        completion_status = "completed"
    
    # Calculate mastery level based on score and completion
    mastery_level = 0.0
    if progress_data.score and progress_data.completion_percentage >= 100:
        mastery_level = min(1.0, progress_data.score / 100.0)
    elif progress_data.completion_percentage >= 100:
        mastery_level = 0.8  # Completed but no score
    else:
        mastery_level = progress_data.completion_percentage / 200.0  # Partial mastery
    
    # Create progress record
    progress = Progress(
        student_id=current_user.id,
        learning_material_id=progress_data.learning_material_id,
        completion_status=completion_status,
        completion_percentage=progress_data.completion_percentage,
        time_spent=progress_data.time_spent,
        score=progress_data.score,
        difficulty_rating=progress_data.difficulty_rating,
        mastery_level=mastery_level,
        interaction_data=progress_data.interaction_data or {},
        started_at=datetime.now(),
        completed_at=datetime.now() if completion_status == "completed" else None
    )
    
    db.add(progress)
    
    # Update student's overall stats
    current_user.total_study_time += progress_data.time_spent
    
    # Update learning style based on new progress
    if completion_status == "completed":
        style_detector = LearningStyleDetector()
        updated_scores = style_detector.update_learning_style_profile(current_user, progress)
        current_user.learning_style_scores = updated_scores
        current_user.dominant_learning_style = max(updated_scores.items(), key=lambda x: x[1])[0]
    
    db.commit()
    
    return {"message": "Progress recorded successfully", "progress_id": progress.id}


@router.put("/{progress_id}")
async def update_progress_record(
    progress_id: int,
    progress_update: ProgressUpdate,
    current_user: Student = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update existing progress record"""
    
    progress = db.query(Progress).filter(
        Progress.id == progress_id,
        Progress.student_id == current_user.id
    ).first()
    
    if not progress:
        raise HTTPException(status_code=404, detail="Progress record not found")
    
    # Update fields
    if progress_update.completion_percentage is not None:
        old_time = progress.time_spent
        progress.completion_percentage = progress_update.completion_percentage
        
        # Update completion status
        if progress_update.completion_percentage >= 100:
            progress.completion_status = "completed"
            progress.completed_at = datetime.now()
        elif progress_update.completion_percentage > 0:
            progress.completion_status = "in_progress"
    
    if progress_update.time_spent is not None:
        time_diff = progress_update.time_spent - progress.time_spent
        progress.time_spent = progress_update.time_spent
        current_user.total_study_time += time_diff
    
    if progress_update.score is not None:
        progress.score = progress_update.score
    
    if progress_update.completion_status is not None:
        progress.completion_status = progress_update.completion_status
    
    if progress_update.difficulty_rating is not None:
        progress.difficulty_rating = progress_update.difficulty_rating
    
    if progress_update.confidence_score is not None:
        progress.confidence_score = progress_update.confidence_score
    
    if progress_update.interaction_data is not None:
        progress.interaction_data = progress_update.interaction_data
    
    # Recalculate mastery level
    if progress.score and progress.completion_percentage >= 100:
        progress.mastery_level = min(1.0, progress.score / 100.0)
    elif progress.completion_percentage >= 100:
        progress.mastery_level = 0.8
    
    progress.updated_at = datetime.now()
    progress.last_accessed = datetime.now()
    
    db.commit()
    
    return {"message": "Progress updated successfully"}


@router.get("/", response_model=List[ProgressResponse])
async def get_progress_records(
    subject: Optional[str] = Query(None),
    limit: int = Query(50, le=200),
    current_user: Student = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get student's progress records"""
    
    query = db.query(Progress).filter(Progress.student_id == current_user.id)
    
    if subject:
        query = query.join(LearningMaterial).filter(
            LearningMaterial.subject.ilike(f"%{subject}%")
        )
    
    progress_records = query.order_by(Progress.updated_at.desc()).limit(limit).all()
    
    return [
        ProgressResponse(
            id=record.id,
            learning_material_id=record.learning_material_id,
            material_title=record.learning_material.title if record.learning_material else "Unknown",
            subject=record.learning_material.subject if record.learning_material else "Unknown",
            topic=record.learning_material.topic if record.learning_material else "Unknown",
            completion_status=record.completion_status,
            completion_percentage=record.completion_percentage,
            time_spent=record.time_spent,
            score=record.score,
            mastery_level=record.mastery_level,
            created_at=record.created_at,
            updated_at=record.updated_at
        )
        for record in progress_records
    ]


@router.get("/summary")
async def get_progress_summary(
    current_user: Student = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get overall progress summary for student"""
    
    # Get all progress records
    progress_records = db.query(Progress).filter(
        Progress.student_id == current_user.id
    ).all()
    
    if not progress_records:
        return {
            "total_materials": 0,
            "completed_materials": 0,
            "in_progress_materials": 0,
            "total_study_time": 0,
            "average_score": 0.0,
            "subjects_studied": []
        }
    
    # Calculate summary statistics
    completed = len([r for r in progress_records if r.completion_status == "completed"])
    in_progress = len([r for r in progress_records if r.completion_status == "in_progress"])
    total_time = sum(r.time_spent for r in progress_records)
    scores = [r.score for r in progress_records if r.score is not None]
    avg_score = sum(scores) / len(scores) if scores else 0.0
    
    # Get subjects studied
    subjects = set()
    for record in progress_records:
        if record.learning_material and record.learning_material.subject:
            subjects.add(record.learning_material.subject)
    
    return {
        "total_materials": len(progress_records),
        "completed_materials": completed,
        "in_progress_materials": in_progress,
        "total_study_time": total_time,
        "average_score": round(avg_score, 1),
        "subjects_studied": list(subjects),
        "completion_rate": round(completed / len(progress_records) * 100, 1) if progress_records else 0.0
    }