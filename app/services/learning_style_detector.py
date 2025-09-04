"""
AI-based learning style detection service using behavioral analysis
"""

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from typing import Dict, List, Tuple
import json
from datetime import datetime, timedelta

from app.models.student import Student
from app.models.progress import Progress
from app.models.learning_material import LearningMaterial, ContentType


class LearningStyleDetector:
    """
    AI service to detect and analyze student learning styles based on:
    - Content interaction patterns
    - Performance across different content types
    - Time spent on different activities
    - Learning velocity patterns
    """
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        self.is_trained = False
    
    def extract_behavioral_features(self, student_id: int, progress_records: List[Progress]) -> Dict:
        """
        Extract behavioral features from student's learning history
        """
        if not progress_records:
            return self._get_default_features()
        
        features = {
            # Content type preferences (time spent / performance)
            'visual_preference': 0.0,
            'auditory_preference': 0.0,
            'kinesthetic_preference': 0.0,
            'text_preference': 0.0,
            
            # Learning patterns
            'avg_session_length': 0.0,
            'completion_rate': 0.0,
            'retry_frequency': 0.0,
            'help_seeking_behavior': 0.0,
            
            # Performance patterns
            'improvement_rate': 0.0,
            'consistency_score': 0.0,
            'difficulty_progression': 0.0,
            
            # Temporal patterns
            'learning_momentum': 0.0,
            'break_pattern': 0.0
        }
        
        # Analyze content type interactions
        content_type_data = {}
        for record in progress_records:
            content_type = record.learning_material.content_type.value if record.learning_material else 'unknown'
            
            if content_type not in content_type_data:
                content_type_data[content_type] = {
                    'total_time': 0,
                    'total_score': 0,
                    'count': 0,
                    'completions': 0
                }
            
            content_type_data[content_type]['total_time'] += record.time_spent
            if record.score:
                content_type_data[content_type]['total_score'] += record.score
            content_type_data[content_type]['count'] += 1
            if record.completion_status == 'completed':
                content_type_data[content_type]['completions'] += 1
        
        # Calculate content type preferences
        total_interactions = sum(data['count'] for data in content_type_data.values())
        if total_interactions > 0:
            # Map content types to learning styles
            style_mapping = {
                'video': 'visual_preference',
                'interactive': 'kinesthetic_preference', 
                'audio': 'auditory_preference',
                'text': 'text_preference',
                'quiz': 'text_preference',  # Quizzes often involve reading
                'simulation': 'kinesthetic_preference'
            }
            
            for content_type, data in content_type_data.items():
                if content_type in style_mapping:
                    preference_key = style_mapping[content_type]
                    
                    # Factor in both time spent and performance
                    time_weight = data['total_time'] / max(1, sum(d['total_time'] for d in content_type_data.values()))
                    performance_weight = (data['total_score'] / max(1, data['count'])) / 100.0 if data['count'] > 0 else 0
                    completion_weight = data['completions'] / max(1, data['count'])
                    
                    features[preference_key] = (time_weight * 0.4 + performance_weight * 0.4 + completion_weight * 0.2)
        
        # Calculate other learning patterns
        if progress_records:
            # Session patterns
            session_lengths = [record.time_spent for record in progress_records if record.time_spent > 0]
            features['avg_session_length'] = np.mean(session_lengths) if session_lengths else 30.0
            
            # Completion rate
            completed = len([r for r in progress_records if r.completion_status == 'completed'])
            features['completion_rate'] = completed / len(progress_records)
            
            # Improvement rate
            scores = [(record.score or 0, record.created_at) for record in progress_records if record.score is not None]
            if len(scores) > 1:
                scores.sort(key=lambda x: x[1])  # Sort by date
                early_avg = np.mean([s[0] for s in scores[:len(scores)//2]])
                late_avg = np.mean([s[0] for s in scores[len(scores)//2:]])
                features['improvement_rate'] = (late_avg - early_avg) / 100.0
            
            # Retry patterns
            retry_count = sum(record.attempts - 1 for record in progress_records)
            features['retry_frequency'] = retry_count / len(progress_records)
        
        return features
    
    def _get_default_features(self) -> Dict:
        """Return default feature values for new students"""
        return {
            'visual_preference': 0.25,
            'auditory_preference': 0.25,
            'kinesthetic_preference': 0.25,
            'text_preference': 0.25,
            'avg_session_length': 30.0,
            'completion_rate': 0.0,
            'retry_frequency': 0.0,
            'help_seeking_behavior': 0.0,
            'improvement_rate': 0.0,
            'consistency_score': 0.5,
            'difficulty_progression': 0.5,
            'learning_momentum': 0.5,
            'break_pattern': 0.5
        }
    
    def detect_learning_style(self, student: Student, progress_records: List[Progress]) -> Dict[str, float]:
        """
        Detect student's learning style based on behavioral data
        Returns scores for each learning style (0-1 scale)
        """
        features = self.extract_behavioral_features(student.id, progress_records)
        
        # Calculate learning style scores based on behavioral patterns
        style_scores = {
            'visual': self._calculate_visual_score(features),
            'auditory': self._calculate_auditory_score(features),
            'kinesthetic': self._calculate_kinesthetic_score(features),
            'reading_writing': self._calculate_text_score(features)
        }
        
        # Normalize scores to sum to 1
        total_score = sum(style_scores.values())
        if total_score > 0:
            style_scores = {k: v/total_score for k, v in style_scores.items()}
        else:
            style_scores = {k: 0.25 for k in style_scores.keys()}
        
        return style_scores
    
    def _calculate_visual_score(self, features: Dict) -> float:
        """Calculate visual learning style score"""
        base_score = features.get('visual_preference', 0.25)
        
        # Visual learners often prefer shorter, focused sessions
        session_factor = 1.2 if features.get('avg_session_length', 30) < 25 else 0.8
        
        # Visual learners often have good completion rates with visual content
        completion_factor = 1.0 + features.get('completion_rate', 0) * 0.3
        
        return min(1.0, base_score * session_factor * completion_factor)
    
    def _calculate_auditory_score(self, features: Dict) -> float:
        """Calculate auditory learning style score"""
        base_score = features.get('auditory_preference', 0.25)
        
        # Auditory learners often prefer longer sessions
        session_factor = 1.2 if features.get('avg_session_length', 30) > 35 else 0.8
        
        # Lower retry frequency (they get it the first time when explained well)
        retry_factor = 1.2 if features.get('retry_frequency', 0) < 0.3 else 0.9
        
        return min(1.0, base_score * session_factor * retry_factor)
    
    def _calculate_kinesthetic_score(self, features: Dict) -> float:
        """Calculate kinesthetic learning style score"""
        base_score = features.get('kinesthetic_preference', 0.25)
        
        # Kinesthetic learners often learn through trial and error
        retry_factor = 1.1 if features.get('retry_frequency', 0) > 0.5 else 0.9
        
        # They show good improvement over time
        improvement_factor = 1.0 + max(0, features.get('improvement_rate', 0)) * 0.5
        
        return min(1.0, base_score * retry_factor * improvement_factor)
    
    def _calculate_text_score(self, features: Dict) -> float:
        """Calculate reading/writing learning style score"""
        base_score = features.get('text_preference', 0.25)
        
        # Text learners often have high completion rates
        completion_factor = 1.0 + features.get('completion_rate', 0) * 0.4
        
        # They prefer consistent, methodical learning
        consistency_factor = 1.0 + features.get('consistency_score', 0.5) * 0.3
        
        return min(1.0, base_score * completion_factor * consistency_factor)
    
    def update_learning_style_profile(self, student: Student, new_progress: Progress) -> Dict[str, float]:
        """
        Update learning style profile based on new progress data
        Uses exponential smoothing to gradually adapt the profile
        """
        current_scores = student.learning_style_scores or {
            'visual': 0.25, 'auditory': 0.25, 'kinesthetic': 0.25, 'reading_writing': 0.25
        }
        
        # Get recent progress for analysis
        # In a real implementation, you'd query the database here
        recent_progress = [new_progress]  # Simplified for this example
        
        # Detect new scores
        new_scores = self.detect_learning_style(student, recent_progress)
        
        # Apply exponential smoothing (alpha = 0.1 for gradual adaptation)
        alpha = 0.1
        updated_scores = {}
        for style in current_scores.keys():
            updated_scores[style] = (1 - alpha) * current_scores[style] + alpha * new_scores[style]
        
        return updated_scores