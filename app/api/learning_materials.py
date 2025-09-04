"""
Learning Materials API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.database import get_db
from app.models.learning_material import LearningMaterial, ContentType, DifficultyLevel
from app.models.student import Student
from app.api.auth import get_current_user
from app.services.adaptive_learning import AdaptiveLearningEngine

router = APIRouter()

# Pydantic models
class LearningMaterialResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    content_type: str
    content_url: Optional[str]
    subject: str
    topic: str
    difficulty_level: str
    estimated_duration: Optional[int]
    learning_styles: List[str]
    tags: List[str]
    average_rating: float
    complexity_score: float

class MaterialCreate(BaseModel):
    title: str
    description: Optional[str] = None
    content_type: ContentType
    content_url: Optional[str] = None
    content_text: Optional[str] = None
    subject: str
    topic: str
    difficulty_level: DifficultyLevel
    estimated_duration: Optional[int] = None
    learning_styles: List[str] = []
    prerequisites: List[int] = []
    tags: List[str] = []


@router.get("/", response_model=List[LearningMaterialResponse])
async def get_learning_materials(
    subject: Optional[str] = Query(None),
    topic: Optional[str] = Query(None),
    difficulty: Optional[str] = Query(None),
    content_type: Optional[str] = Query(None),
    personalized: bool = Query(False),
    limit: int = Query(20, le=100),
    current_user: Student = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get learning materials with optional filtering and personalization"""
    
    query = db.query(LearningMaterial).filter(LearningMaterial.is_active == True)
    
    # Apply filters
    if subject:
        query = query.filter(LearningMaterial.subject.ilike(f"%{subject}%"))
    if topic:
        query = query.filter(LearningMaterial.topic.ilike(f"%{topic}%"))
    if difficulty:
        query = query.filter(LearningMaterial.difficulty_level == difficulty)
    if content_type:
        query = query.filter(LearningMaterial.content_type == content_type)
    
    materials = query.limit(limit).all()
    
    if personalized:
        # Sort by suitability for current user
        adaptive_engine = AdaptiveLearningEngine()
        scored_materials = []
        
        for material in materials:
            suitability = adaptive_engine.calculate_content_suitability(material, current_user)
            scored_materials.append((material, suitability))
        
        # Sort by suitability score
        scored_materials.sort(key=lambda x: x[1], reverse=True)
        materials = [material for material, score in scored_materials]
    
    return [
        LearningMaterialResponse(
            id=material.id,
            title=material.title,
            description=material.description,
            content_type=material.content_type.value,
            content_url=material.content_url,
            subject=material.subject,
            topic=material.topic,
            difficulty_level=material.difficulty_level.value,
            estimated_duration=material.estimated_duration,
            learning_styles=material.learning_styles or [],
            tags=material.tags or [],
            average_rating=material.average_rating,
            complexity_score=material.complexity_score
        )
        for material in materials
    ]


@router.get("/{material_id}", response_model=LearningMaterialResponse)
async def get_learning_material(
    material_id: int,
    current_user: Student = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific learning material"""
    material = db.query(LearningMaterial).filter(
        LearningMaterial.id == material_id,
        LearningMaterial.is_active == True
    ).first()
    
    if not material:
        raise HTTPException(status_code=404, detail="Learning material not found")
    
    return LearningMaterialResponse(
        id=material.id,
        title=material.title,
        description=material.description,
        content_type=material.content_type.value,
        content_url=material.content_url,
        subject=material.subject,
        topic=material.topic,
        difficulty_level=material.difficulty_level.value,
        estimated_duration=material.estimated_duration,
        learning_styles=material.learning_styles or [],
        tags=material.tags or [],
        average_rating=material.average_rating,
        complexity_score=material.complexity_score
    )


@router.get("/{material_id}/suitability")
async def get_material_suitability(
    material_id: int,
    current_user: Student = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get personalized suitability score for specific material"""
    material = db.query(LearningMaterial).filter(
        LearningMaterial.id == material_id
    ).first()
    
    if not material:
        raise HTTPException(status_code=404, detail="Learning material not found")
    
    adaptive_engine = AdaptiveLearningEngine()
    suitability_score = adaptive_engine.calculate_content_suitability(material, current_user)
    prediction = adaptive_engine.predict_student_performance(current_user, material)
    
    return {
        "material_id": material_id,
        "suitability_score": suitability_score,
        "performance_prediction": prediction,
        "recommended": suitability_score > 0.7,
        "analysis_timestamp": datetime.now().isoformat()
    }


@router.get("/subjects/list")
async def get_available_subjects(
    current_user: Student = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of all available subjects"""
    subjects = db.query(LearningMaterial.subject).distinct().all()
    return {
        "subjects": [subject[0] for subject in subjects if subject[0]]
    }


@router.get("/topics/list")
async def get_available_topics(
    subject: Optional[str] = Query(None),
    current_user: Student = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of available topics, optionally filtered by subject"""
    query = db.query(LearningMaterial.topic).distinct()
    
    if subject:
        query = query.filter(LearningMaterial.subject.ilike(f"%{subject}%"))
    
    topics = query.all()
    return {
        "topics": [topic[0] for topic in topics if topic[0]]
    }