"""
Adaptive Learning Algorithm that personalizes content delivery
"""

import numpy as np
import math
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from sklearn.metrics.pairwise import cosine_similarity

from app.models.student import Student
from app.models.learning_material import LearningMaterial, DifficultyLevel
from app.models.progress import Progress


class AdaptiveLearningEngine:
    """
    Core adaptive learning algorithm that:
    1. Adjusts content difficulty based on performance
    2. Selects optimal content types based on learning style
    3. Determines optimal learning path sequencing
    4. Manages learning pace and timing
    """
    
    def __init__(self):
        self.difficulty_weights = {
            DifficultyLevel.BEGINNER: 0.3,
            DifficultyLevel.INTERMEDIATE: 0.6,
            DifficultyLevel.ADVANCED: 1.0
        }
    
    def calculate_optimal_difficulty(self, student: Student, subject: str, recent_performance: List[float]) -> str:
        """
        Calculate optimal difficulty level for next content
        Uses Zone of Proximal Development theory
        """
        if not recent_performance:
            return student.difficulty_preference or "intermediate"
        
        avg_performance = np.mean(recent_performance)
        performance_std = np.std(recent_performance) if len(recent_performance) > 1 else 0.0
        
        # Calculate confidence and consistency
        confidence = avg_performance / 100.0  # Convert to 0-1 scale
        consistency = 1.0 - (performance_std / 100.0) if performance_std > 0 else 1.0
        
        # Adaptive difficulty adjustment
        if confidence > 0.85 and consistency > 0.8:
            # Student is mastering current level, increase difficulty
            if student.difficulty_preference == "beginner":
                return "intermediate"
            elif student.difficulty_preference == "intermediate":
                return "advanced"
            else:
                return "advanced"
        elif confidence < 0.6 or consistency < 0.5:
            # Student is struggling, decrease difficulty
            if student.difficulty_preference == "advanced":
                return "intermediate"
            elif student.difficulty_preference == "intermediate":
                return "beginner"
            else:
                return "beginner"
        else:
            # Maintain current difficulty
            return student.difficulty_preference or "intermediate"
    
    def calculate_content_suitability(self, material: LearningMaterial, student: Student) -> float:
        """
        Calculate how suitable a learning material is for a specific student
        Returns score from 0-1
        """
        suitability_score = 0.0
        
        # Learning style compatibility (40% weight)
        if student.learning_style_scores:
            style_compatibility = self._calculate_style_compatibility(material, student.learning_style_scores)
            suitability_score += style_compatibility * 0.4
        else:
            suitability_score += 0.5 * 0.4  # Default score
        
        # Difficulty appropriateness (30% weight)
        difficulty_score = self._calculate_difficulty_appropriateness(material, student)
        suitability_score += difficulty_score * 0.3
        
        # Content effectiveness (20% weight)
        effectiveness_score = material.effectiveness_score or 0.5
        suitability_score += effectiveness_score * 0.2
        
        # Novelty factor (10% weight) - prefer content not recently seen
        novelty_score = self._calculate_novelty_score(material, student)
        suitability_score += novelty_score * 0.1
        
        return min(1.0, suitability_score)
    
    def _calculate_style_compatibility(self, material: LearningMaterial, style_scores: Dict[str, float]) -> float:
        """Calculate how well material matches student's learning style"""
        if not material.learning_styles:
            return 0.5  # Neutral score for materials without style tags
        
        compatibility = 0.0
        for style in material.learning_styles:
            if style in style_scores:
                compatibility += style_scores[style]
        
        return compatibility / len(material.learning_styles) if material.learning_styles else 0.5
    
    def _calculate_difficulty_appropriateness(self, material: LearningMaterial, student: Student) -> float:
        """Calculate if material difficulty matches student's current level"""
        material_difficulty = self.difficulty_weights.get(material.difficulty_level, 0.6)
        
        # Get student's current performance level (simplified)
        target_difficulty = {
            "beginner": 0.3,
            "intermediate": 0.6,
            "advanced": 1.0
        }.get(student.difficulty_preference, 0.6)
        
        # Calculate appropriateness based on closeness to target
        difference = abs(material_difficulty - target_difficulty)
        appropriateness = 1.0 - difference
        
        return max(0.0, appropriateness)
    
    def _calculate_novelty_score(self, material: LearningMaterial, student: Student) -> float:
        """Calculate novelty/freshness score to avoid repetition"""
        # In a real implementation, check when student last accessed this material
        # For now, return a default score
        return 0.8  # Assume most content is relatively novel
    
    def generate_learning_path(self, student: Student, subject: str, target_topics: List[str], 
                             available_materials: List[LearningMaterial]) -> List[Dict]:
        """
        Generate personalized learning path for a student
        """
        learning_path = []
        
        # Filter materials by subject and target topics
        relevant_materials = [
            material for material in available_materials
            if material.subject.lower() == subject.lower() and 
            any(topic.lower() in (material.topic.lower() or '') for topic in target_topics)
        ]
        
        if not relevant_materials:
            return learning_path
        
        # Group materials by topic and difficulty
        topic_materials = {}
        for material in relevant_materials:
            topic = material.topic
            if topic not in topic_materials:
                topic_materials[topic] = []
            topic_materials[topic].append(material)
        
        # Generate path for each topic
        for topic in target_topics:
            if topic in topic_materials:
                # Sort materials by suitability
                materials = topic_materials[topic]
                scored_materials = [
                    (material, self.calculate_content_suitability(material, student))
                    for material in materials
                ]
                scored_materials.sort(key=lambda x: x[1], reverse=True)
                
                # Add top materials to learning path
                for material, suitability in scored_materials[:3]:  # Top 3 per topic
                    learning_path.append({
                        'material_id': material.id,
                        'material_title': material.title,
                        'topic': material.topic,
                        'difficulty': material.difficulty_level.value,
                        'estimated_duration': material.estimated_duration,
                        'suitability_score': suitability,
                        'recommended_order': len(learning_path) + 1
                    })
        
        return learning_path
    
    def adjust_learning_pace(self, student: Student, recent_progress: List[Progress]) -> Dict[str, float]:
        """
        Adjust learning pace based on recent performance and engagement
        """
        if not recent_progress:
            return {'pace_multiplier': 1.0, 'break_recommendation': 15}
        
        # Analyze recent performance
        recent_scores = [p.score for p in recent_progress if p.score is not None]
        recent_engagement = [p.engagement_score for p in recent_progress if p.engagement_score is not None]
        recent_times = [p.time_spent for p in recent_progress if p.time_spent > 0]
        
        pace_multiplier = 1.0
        
        # Adjust based on performance
        if recent_scores:
            avg_score = np.mean(recent_scores)
            if avg_score > 85:
                pace_multiplier *= 1.2  # Speed up for high performers
            elif avg_score < 60:
                pace_multiplier *= 0.8  # Slow down for struggling students
        
        # Adjust based on engagement
        if recent_engagement:
            avg_engagement = np.mean(recent_engagement)
            if avg_engagement < 0.4:
                pace_multiplier *= 0.7  # Slow down for low engagement
            elif avg_engagement > 0.8:
                pace_multiplier *= 1.1  # Maintain momentum for engaged students
        
        # Calculate break recommendation
        avg_session_time = np.mean(recent_times) if recent_times else 30
        break_recommendation = min(30, max(5, int(avg_session_time / 3)))
        
        return {
            'pace_multiplier': max(0.5, min(2.0, pace_multiplier)),
            'break_recommendation': break_recommendation,
            'recommended_session_length': int(avg_session_time * pace_multiplier)
        }
    
    def predict_student_performance(self, student: Student, material: LearningMaterial) -> Dict[str, float]:
        """
        Predict how well a student will perform on given material
        """
        # Base prediction on learning style compatibility
        style_compatibility = self._calculate_style_compatibility(material, student.learning_style_scores or {})
        
        # Factor in difficulty appropriateness
        difficulty_match = self._calculate_difficulty_appropriateness(material, student)
        
        # Consider student's historical performance in this subject
        base_performance = student.performance_score / 100.0 if student.performance_score else 0.5
        
        # Combine factors
        predicted_score = (
            style_compatibility * 0.4 +
            difficulty_match * 0.3 +
            base_performance * 0.3
        ) * 100.0
        
        # Estimate completion probability
        completion_probability = (
            style_compatibility * 0.3 +
            difficulty_match * 0.4 +
            (student.learning_streak / 30.0) * 0.3  # Streak factor
        )
        
        # Estimate time to completion
        base_time = material.estimated_duration or 30
        time_multiplier = 2.0 - student.learning_rate if student.learning_rate else 1.0
        estimated_time = int(base_time * time_multiplier)
        
        return {
            'predicted_score': min(100.0, max(0.0, predicted_score)),
            'completion_probability': min(1.0, max(0.0, completion_probability)),
            'estimated_completion_time': estimated_time,
            'confidence': (style_compatibility + difficulty_match) / 2.0
        }