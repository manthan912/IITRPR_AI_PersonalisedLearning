"""
Advanced progress tracking and analytics service
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict

from app.models.student import Student
from app.models.progress import Progress
from app.models.learning_material import LearningMaterial


class ProgressAnalytics:
    """
    Service for analyzing student progress and generating insights
    """
    
    def __init__(self):
        self.performance_thresholds = {
            'excellent': 90,
            'good': 75,
            'average': 60,
            'poor': 45,
            'critical': 30
        }
    
    def analyze_student_performance(self, student: Student, progress_records: List[Progress], 
                                  time_window_days: int = 30) -> Dict:
        """
        Comprehensive analysis of student performance over specified time window
        """
        # Filter recent records
        cutoff_date = datetime.now() - timedelta(days=time_window_days)
        recent_records = [
            record for record in progress_records 
            if record.created_at and record.created_at >= cutoff_date
        ]
        
        if not recent_records:
            return self._get_default_analysis()
        
        analysis = {
            'overall_performance': self._calculate_overall_performance(recent_records),
            'learning_velocity': self._calculate_learning_velocity(recent_records),
            'subject_breakdown': self._analyze_by_subject(recent_records),
            'learning_patterns': self._identify_learning_patterns(recent_records),
            'strengths_weaknesses': self._identify_strengths_weaknesses(recent_records),
            'engagement_trends': self._analyze_engagement_trends(recent_records),
            'recommendations': self._generate_performance_recommendations(recent_records, student)
        }
        
        return analysis
    
    def _calculate_overall_performance(self, records: List[Progress]) -> Dict:
        """Calculate overall performance metrics"""
        scores = [record.score for record in records if record.score is not None]
        completion_rates = [
            1.0 if record.completion_status == 'completed' else 0.0 
            for record in records
        ]
        
        return {
            'average_score': np.mean(scores) if scores else 0.0,
            'score_std': np.std(scores) if len(scores) > 1 else 0.0,
            'completion_rate': np.mean(completion_rates),
            'total_materials_attempted': len(records),
            'materials_completed': sum(completion_rates),
            'performance_trend': self._calculate_trend(scores) if len(scores) > 2 else 'stable'
        }
    
    def _calculate_learning_velocity(self, records: List[Progress]) -> Dict:
        """Calculate how quickly student learns new material"""
        if len(records) < 2:
            return {'velocity_score': 0.5, 'acceleration': 0.0}
        
        # Sort by creation time
        sorted_records = sorted(records, key=lambda x: x.created_at or datetime.min)
        
        # Calculate time between mastery points
        mastery_times = []
        for record in sorted_records:
            if record.mastery_level and record.mastery_level > 0.8:
                mastery_times.append(record.time_spent)
        
        if len(mastery_times) > 1:
            # Calculate velocity as inverse of average time to mastery
            avg_mastery_time = np.mean(mastery_times)
            velocity_score = 1.0 / (1.0 + avg_mastery_time / 60.0)  # Normalize by hour
            
            # Calculate acceleration (improvement in learning speed)
            early_times = mastery_times[:len(mastery_times)//2]
            late_times = mastery_times[len(mastery_times)//2:]
            
            if early_times and late_times:
                early_avg = np.mean(early_times)
                late_avg = np.mean(late_times)
                acceleration = (early_avg - late_avg) / early_avg if early_avg > 0 else 0.0
            else:
                acceleration = 0.0
        else:
            velocity_score = 0.5
            acceleration = 0.0
        
        return {
            'velocity_score': min(1.0, max(0.0, velocity_score)),
            'acceleration': acceleration,
            'mastery_consistency': np.std(mastery_times) if len(mastery_times) > 1 else 0.0
        }
    
    def _analyze_by_subject(self, records: List[Progress]) -> Dict:
        """Analyze performance breakdown by subject"""
        subject_data = defaultdict(list)
        
        for record in records:
            if record.learning_material and record.learning_material.subject:
                subject = record.learning_material.subject
                subject_data[subject].append({
                    'score': record.score,
                    'completion': 1.0 if record.completion_status == 'completed' else 0.0,
                    'time_spent': record.time_spent,
                    'mastery': record.mastery_level or 0.0
                })
        
        analysis = {}
        for subject, data in subject_data.items():
            scores = [d['score'] for d in data if d['score'] is not None]
            completions = [d['completion'] for d in data]
            times = [d['time_spent'] for d in data if d['time_spent'] > 0]
            mastery_levels = [d['mastery'] for d in data]
            
            analysis[subject] = {
                'average_score': np.mean(scores) if scores else 0.0,
                'completion_rate': np.mean(completions),
                'average_time': np.mean(times) if times else 0.0,
                'mastery_level': np.mean(mastery_levels),
                'material_count': len(data),
                'performance_category': self._categorize_performance(np.mean(scores) if scores else 0.0)
            }
        
        return analysis
    
    def _identify_learning_patterns(self, records: List[Progress]) -> Dict:
        """Identify patterns in how student learns"""
        patterns = {
            'preferred_session_length': 0,
            'peak_performance_time': 'unknown',
            'consistency_pattern': 'stable',
            'challenge_response': 'neutral'
        }
        
        if records:
            # Session length preferences
            session_lengths = [record.time_spent for record in records if record.time_spent > 0]
            if session_lengths:
                patterns['preferred_session_length'] = int(np.median(session_lengths))
            
            # Performance consistency
            scores = [record.score for record in records if record.score is not None]
            if len(scores) > 3:
                score_std = np.std(scores)
                if score_std < 10:
                    patterns['consistency_pattern'] = 'very_consistent'
                elif score_std < 20:
                    patterns['consistency_pattern'] = 'consistent'
                elif score_std < 30:
                    patterns['consistency_pattern'] = 'variable'
                else:
                    patterns['consistency_pattern'] = 'inconsistent'
            
            # Challenge response
            attempts = [record.attempts for record in records if record.attempts > 1]
            if attempts:
                avg_attempts = np.mean(attempts)
                if avg_attempts > 3:
                    patterns['challenge_response'] = 'persistent'
                elif avg_attempts > 2:
                    patterns['challenge_response'] = 'resilient'
                else:
                    patterns['challenge_response'] = 'efficient'
        
        return patterns
    
    def _identify_strengths_weaknesses(self, records: List[Progress]) -> Dict:
        """Identify student's strengths and areas for improvement"""
        strengths = []
        weaknesses = []
        
        # Analyze by content type
        content_performance = defaultdict(list)
        for record in records:
            if record.learning_material and record.score is not None:
                content_type = record.learning_material.content_type.value
                content_performance[content_type].append(record.score)
        
        # Identify strengths and weaknesses
        for content_type, scores in content_performance.items():
            if scores:
                avg_score = np.mean(scores)
                if avg_score >= 85:
                    strengths.append(f"Excellent performance with {content_type} content")
                elif avg_score <= 60:
                    weaknesses.append(f"Difficulty with {content_type} content")
        
        return {
            'strengths': strengths,
            'areas_for_improvement': weaknesses,
            'improvement_suggestions': self._generate_improvement_suggestions(weaknesses)
        }
    
    def _analyze_engagement_trends(self, records: List[Progress]) -> Dict:
        """Analyze engagement patterns over time"""
        if not records:
            return {'trend': 'unknown', 'average_engagement': 0.5}
        
        # Sort by date
        sorted_records = sorted(records, key=lambda x: x.created_at or datetime.min)
        
        engagement_scores = [record.engagement_score for record in sorted_records if record.engagement_score is not None]
        
        if len(engagement_scores) < 3:
            return {'trend': 'insufficient_data', 'average_engagement': np.mean(engagement_scores) if engagement_scores else 0.5}
        
        # Calculate trend
        trend = self._calculate_trend(engagement_scores)
        
        return {
            'trend': trend,
            'average_engagement': np.mean(engagement_scores),
            'engagement_variance': np.var(engagement_scores),
            'recent_engagement': np.mean(engagement_scores[-5:]) if len(engagement_scores) >= 5 else np.mean(engagement_scores)
        }
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction from a series of values"""
        if len(values) < 3:
            return 'stable'
        
        # Simple linear regression slope
        x = np.arange(len(values))
        slope = np.polyfit(x, values, 1)[0]
        
        if slope > 2.0:
            return 'improving'
        elif slope < -2.0:
            return 'declining'
        else:
            return 'stable'
    
    def _categorize_performance(self, score: float) -> str:
        """Categorize performance based on score"""
        for category, threshold in self.performance_thresholds.items():
            if score >= threshold:
                return category
        return 'critical'
    
    def _generate_improvement_suggestions(self, weaknesses: List[str]) -> List[str]:
        """Generate actionable improvement suggestions"""
        suggestions = []
        
        for weakness in weaknesses:
            if 'video' in weakness.lower():
                suggestions.append("Try supplementing video content with interactive exercises")
            elif 'text' in weakness.lower():
                suggestions.append("Consider using visual aids and diagrams alongside text")
            elif 'interactive' in weakness.lower():
                suggestions.append("Start with guided practice before independent exercises")
            elif 'audio' in weakness.lower():
                suggestions.append("Use transcripts and visual notes while listening")
        
        return suggestions
    
    def _generate_performance_recommendations(self, records: List[Progress], student: Student) -> List[str]:
        """Generate recommendations based on performance analysis"""
        recommendations = []
        
        if not records:
            return ["Start with introductory materials to establish baseline performance"]
        
        scores = [record.score for record in records if record.score is not None]
        
        if scores:
            avg_score = np.mean(scores)
            recent_scores = scores[-5:] if len(scores) >= 5 else scores
            recent_avg = np.mean(recent_scores)
            
            if recent_avg > avg_score + 10:
                recommendations.append("Great improvement! Consider advancing to more challenging content")
            elif recent_avg < avg_score - 10:
                recommendations.append("Recent performance dip detected. Consider reviewing fundamentals")
            
            if avg_score > 85:
                recommendations.append("Excellent performance! Ready for advanced challenges")
            elif avg_score < 60:
                recommendations.append("Focus on mastering fundamentals before advancing")
        
        return recommendations
    
    def _get_default_analysis(self) -> Dict:
        """Return default analysis for students with no progress data"""
        return {
            'overall_performance': {
                'average_score': 0.0,
                'completion_rate': 0.0,
                'performance_trend': 'unknown'
            },
            'learning_velocity': {'velocity_score': 0.5, 'acceleration': 0.0},
            'subject_breakdown': {},
            'learning_patterns': {'preferred_session_length': 30, 'consistency_pattern': 'unknown'},
            'strengths_weaknesses': {'strengths': [], 'areas_for_improvement': [], 'improvement_suggestions': []},
            'engagement_trends': {'trend': 'unknown', 'average_engagement': 0.5},
            'recommendations': ['Complete learning style assessment', 'Start with introductory content']
        }