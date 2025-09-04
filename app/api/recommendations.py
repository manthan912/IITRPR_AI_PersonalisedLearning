"""
AI Recommendations API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.database import get_db
from app.models.student import Student
from app.models.learning_material import LearningMaterial
from app.models.progress import Progress
from app.models.recommendation import Recommendation
from app.api.auth import get_current_user
from app.services.recommendation_engine import RecommendationEngine
from app.services.adaptive_learning import AdaptiveLearningEngine

router = APIRouter()

# Pydantic models
class RecommendationResponse(BaseModel):
    id: Optional[int]
    material_id: int
    material_title: str
    subject: str
    topic: str
    recommendation_type: str
    reasoning: str
    confidence_score: float
    priority_score: float
    estimated_duration: Optional[int]
    predicted_performance: Optional[dict]

class LearningPathResponse(BaseModel):
    path_id: str
    total_duration: int
    difficulty_progression: List[str]
    recommendations: List[dict]

class RecommendationFeedback(BaseModel):
    recommendation_id: int
    was_helpful: bool
    was_completed: bool
    student_rating: Optional[float] = None
    feedback_notes: Optional[str] = None


@router.get("/", response_model=List[RecommendationResponse])
async def get_recommendations(
    recommendation_type: Optional[str] = Query(None, description="Filter by type: next_topic, review, challenge"),
    limit: int = Query(5, le=20),
    current_user: Student = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get personalized AI recommendations for student"""
    
    # Get student's progress records
    progress_records = db.query(Progress).filter(
        Progress.student_id == current_user.id
    ).all()
    
    # Get available learning materials
    available_materials = db.query(LearningMaterial).filter(
        LearningMaterial.is_active == True
    ).all()
    
    # Generate recommendations
    recommendation_engine = RecommendationEngine()
    recommendations = recommendation_engine.generate_personalized_recommendations(
        current_user, progress_records, available_materials, limit
    )
    
    # Filter by type if specified
    if recommendation_type:
        recommendations = [
            rec for rec in recommendations 
            if rec.get('type') == recommendation_type
        ]
    
    # Convert to response format
    response_recommendations = []
    for rec in recommendations:
        material = rec['material']
        response_recommendations.append(RecommendationResponse(
            id=None,  # Generated recommendations don't have DB IDs yet
            material_id=material.id,
            material_title=material.title,
            subject=material.subject,
            topic=material.topic,
            recommendation_type=rec['type'],
            reasoning=rec['reasoning'],
            confidence_score=rec.get('score', 0.5),
            priority_score=rec.get('estimated_benefit', 0.5),
            estimated_duration=material.estimated_duration,
            predicted_performance=rec.get('predicted_performance')
        ))
    
    return response_recommendations


@router.get("/learning-path")
async def generate_learning_path(
    subject: str = Query(..., description="Subject for the learning path"),
    target_topics: List[str] = Query(..., description="Topics to include in the path"),
    current_user: Student = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate a complete personalized learning path"""
    
    # Get available materials for the subject
    available_materials = db.query(LearningMaterial).filter(
        LearningMaterial.subject.ilike(f"%{subject}%"),
        LearningMaterial.is_active == True
    ).all()
    
    if not available_materials:
        raise HTTPException(
            status_code=404, 
            detail=f"No learning materials found for subject: {subject}"
        )
    
    # Generate learning path
    adaptive_engine = AdaptiveLearningEngine()
    learning_path = adaptive_engine.generate_learning_path(
        current_user, subject, target_topics, available_materials
    )
    
    if not learning_path:
        raise HTTPException(
            status_code=404,
            detail=f"Could not generate learning path for topics: {target_topics}"
        )
    
    # Calculate total duration and difficulty progression
    total_duration = sum(item.get('estimated_duration', 30) for item in learning_path)
    difficulty_progression = [item['difficulty'] for item in learning_path]
    
    return LearningPathResponse(
        path_id=f"{subject}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        total_duration=total_duration,
        difficulty_progression=difficulty_progression,
        recommendations=learning_path
    )


@router.get("/similar/{material_id}")
async def get_similar_materials(
    material_id: int,
    limit: int = Query(5, le=10),
    current_user: Student = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get materials similar to specified material"""
    
    # Get target material
    target_material = db.query(LearningMaterial).filter(
        LearningMaterial.id == material_id
    ).first()
    
    if not target_material:
        raise HTTPException(status_code=404, detail="Learning material not found")
    
    # Get all materials for similarity comparison
    all_materials = db.query(LearningMaterial).filter(
        LearningMaterial.is_active == True
    ).all()
    
    # Find similar materials
    recommendation_engine = RecommendationEngine()
    similar_materials = recommendation_engine.find_similar_materials(
        target_material, all_materials, limit
    )
    
    return {
        "target_material": {
            "id": target_material.id,
            "title": target_material.title,
            "subject": target_material.subject,
            "topic": target_material.topic
        },
        "similar_materials": [
            {
                "id": material.id,
                "title": material.title,
                "subject": material.subject,
                "topic": material.topic,
                "similarity_score": similarity,
                "difficulty_level": material.difficulty_level.value,
                "estimated_duration": material.estimated_duration
            }
            for material, similarity in similar_materials
        ]
    }


@router.post("/feedback")
async def submit_recommendation_feedback(
    feedback: RecommendationFeedback,
    current_user: Student = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit feedback on recommendation effectiveness"""
    
    # Find the recommendation record (if it exists in DB)
    recommendation = db.query(Recommendation).filter(
        Recommendation.id == feedback.recommendation_id
    ).first()
    
    if recommendation:
        # Update recommendation with feedback
        recommendation.was_accepted = feedback.was_helpful
        recommendation.was_completed = feedback.was_completed
        recommendation.student_rating = feedback.student_rating
        recommendation.updated_at = datetime.now()
        
        # Calculate effectiveness score
        effectiveness = 0.0
        if feedback.was_helpful:
            effectiveness += 0.5
        if feedback.was_completed:
            effectiveness += 0.3
        if feedback.student_rating:
            effectiveness += (feedback.student_rating / 5.0) * 0.2
        
        recommendation.effectiveness_score = effectiveness
        
        db.commit()
    
    return {"message": "Feedback recorded successfully"}


@router.get("/adaptive-suggestions")
async def get_adaptive_suggestions(
    current_user: Student = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get adaptive learning suggestions based on recent performance"""
    
    # Get recent progress (last 10 records)
    recent_progress = db.query(Progress).filter(
        Progress.student_id == current_user.id
    ).order_by(Progress.created_at.desc()).limit(10).all()
    
    # Generate adaptive suggestions
    adaptive_engine = AdaptiveLearningEngine()
    pace_adjustments = adaptive_engine.adjust_learning_pace(current_user, recent_progress)
    
    # Get recent performance scores for difficulty adjustment
    recent_scores = [record.score for record in recent_progress if record.score is not None]
    optimal_difficulty = adaptive_engine.calculate_optimal_difficulty(current_user, '', recent_scores)
    
    return {
        "pace_adjustments": pace_adjustments,
        "optimal_difficulty": optimal_difficulty,
        "learning_velocity": current_user.learning_rate,
        "suggestions": {
            "session_length": pace_adjustments.get('recommended_session_length', 30),
            "break_frequency": pace_adjustments.get('break_recommendation', 15),
            "difficulty_level": optimal_difficulty,
            "focus_areas": recent_progress[0].learning_material.subject if recent_progress and recent_progress[0].learning_material else None
        },
        "performance_trend": "improving" if recent_scores and len(recent_scores) > 2 and recent_scores[-1] > recent_scores[0] else "stable"
    }