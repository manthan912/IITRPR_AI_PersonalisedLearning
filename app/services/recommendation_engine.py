"""
AI-powered recommendation engine for personalized learning
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from sentence_transformers import SentenceTransformer
import json

from app.models.student import Student
from app.models.learning_material import LearningMaterial, ContentType, DifficultyLevel
from app.models.progress import Progress
from app.models.recommendation import Recommendation
from app.services.adaptive_learning import AdaptiveLearningEngine
from app.services.learning_style_detector import LearningStyleDetector
from app.services.progress_analytics import ProgressAnalytics


class RecommendationEngine:
    """
    Intelligent recommendation system that combines multiple AI approaches:
    1. Collaborative filtering (students with similar profiles)
    2. Content-based filtering (material similarity)
    3. Knowledge graph traversal (prerequisite relationships)
    4. Adaptive difficulty adjustment
    5. Learning style optimization
    """
    
    def __init__(self):
        self.adaptive_engine = AdaptiveLearningEngine()
        self.style_detector = LearningStyleDetector()
        self.analytics = ProgressAnalytics()
        
        # Initialize sentence transformer for content similarity
        try:
            self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception:
            self.sentence_model = None
            print("Warning: Sentence transformer not available. Using fallback similarity.")
    
    def generate_personalized_recommendations(self, student: Student, progress_records: List[Progress],
                                            available_materials: List[LearningMaterial],
                                            max_recommendations: int = 5) -> List[Dict]:
        """
        Generate comprehensive personalized recommendations
        """
        recommendations = []
        
        # Analyze current student state
        performance_analysis = self.analytics.analyze_student_performance(student, progress_records)
        
        # Get next learning objectives
        next_topics = self._identify_next_learning_objectives(student, progress_records, available_materials)
        
        # Generate different types of recommendations
        recommendations.extend(self._generate_next_topic_recommendations(
            student, next_topics, available_materials, max_recommendations // 2
        ))
        
        recommendations.extend(self._generate_review_recommendations(
            student, progress_records, available_materials, max_recommendations // 4
        ))
        
        recommendations.extend(self._generate_challenge_recommendations(
            student, performance_analysis, available_materials, max_recommendations // 4
        ))
        
        # Score and rank all recommendations
        scored_recommendations = []
        for rec in recommendations:
            score = self._calculate_recommendation_score(rec, student, performance_analysis)
            rec['score'] = score
            scored_recommendations.append(rec)
        
        # Sort by score and return top recommendations
        scored_recommendations.sort(key=lambda x: x['score'], reverse=True)
        return scored_recommendations[:max_recommendations]
    
    def _identify_next_learning_objectives(self, student: Student, progress_records: List[Progress],
                                         available_materials: List[LearningMaterial]) -> List[str]:
        """
        Identify what the student should learn next based on:
        1. Completed prerequisites
        2. Subject progression
        3. Learning gaps
        """
        # Get completed materials
        completed_materials = [
            record.learning_material_id for record in progress_records
            if record.completion_status == 'completed' and record.mastery_level and record.mastery_level > 0.7
        ]
        
        # Find materials where prerequisites are met
        ready_topics = set()
        for material in available_materials:
            prerequisites = material.prerequisites or []
            if all(prereq in completed_materials for prereq in prerequisites):
                ready_topics.add(material.topic)
        
        # Remove already mastered topics
        mastered_topics = set()
        for record in progress_records:
            if (record.completion_status == 'completed' and 
                record.mastery_level and record.mastery_level > 0.8 and
                record.learning_material):
                mastered_topics.add(record.learning_material.topic)
        
        next_topics = list(ready_topics - mastered_topics)
        
        # If no clear next topics, suggest review or foundational topics
        if not next_topics:
            # Find topics with partial progress
            partial_topics = set()
            for record in progress_records:
                if (record.completion_percentage and record.completion_percentage > 0.1 and
                    record.completion_percentage < 0.8 and record.learning_material):
                    partial_topics.add(record.learning_material.topic)
            
            next_topics = list(partial_topics)
        
        return next_topics[:5]  # Limit to top 5 objectives
    
    def _generate_next_topic_recommendations(self, student: Student, next_topics: List[str],
                                           available_materials: List[LearningMaterial],
                                           max_count: int) -> List[Dict]:
        """Generate recommendations for new topics to learn"""
        recommendations = []
        
        # Get optimal difficulty for student
        recent_performance = [
            record.score for record in student.progress_records[-10:]
            if record.score is not None
        ]
        optimal_difficulty = self.adaptive_engine.calculate_optimal_difficulty(
            student, '', recent_performance
        )
        
        for topic in next_topics:
            # Find best materials for this topic
            topic_materials = [
                material for material in available_materials
                if material.topic.lower() == topic.lower() and material.is_active
            ]
            
            # Score materials for this student
            scored_materials = []
            for material in topic_materials:
                suitability = self.adaptive_engine.calculate_content_suitability(material, student)
                prediction = self.adaptive_engine.predict_student_performance(student, material)
                
                scored_materials.append((material, suitability, prediction))
            
            # Sort by suitability and take best match
            scored_materials.sort(key=lambda x: x[1], reverse=True)
            
            if scored_materials and len(recommendations) < max_count:
                material, suitability, prediction = scored_materials[0]
                recommendations.append({
                    'type': 'next_topic',
                    'material_id': material.id,
                    'material': material,
                    'topic': topic,
                    'reasoning': f"Ready to learn {topic} - prerequisites completed",
                    'suitability_score': suitability,
                    'predicted_performance': prediction,
                    'estimated_benefit': suitability * 0.8 + prediction['completion_probability'] * 0.2
                })
        
        return recommendations
    
    def _generate_review_recommendations(self, student: Student, progress_records: List[Progress],
                                       available_materials: List[LearningMaterial], max_count: int) -> List[Dict]:
        """Generate recommendations for reviewing/reinforcing previous learning"""
        recommendations = []
        
        # Find topics that might need review
        review_candidates = []
        
        for record in progress_records:
            if (record.learning_material and record.completion_status == 'completed' and
                record.created_at and record.created_at < datetime.now() - timedelta(days=14)):
                
                # Calculate forgetting curve impact
                days_since = (datetime.now() - record.created_at).days
                retention_probability = student.retention_rate ** (days_since / 7.0)  # Weekly decay
                
                if retention_probability < 0.6:  # Below 60% retention
                    review_candidates.append((record, retention_probability))
        
        # Sort by urgency (lowest retention first)
        review_candidates.sort(key=lambda x: x[1])
        
        for record, retention_prob in review_candidates[:max_count]:
            if record.learning_material:
                recommendations.append({
                    'type': 'review',
                    'material_id': record.learning_material.id,
                    'material': record.learning_material,
                    'topic': record.learning_material.topic,
                    'reasoning': f"Review recommended - retention probability: {retention_prob:.1%}",
                    'urgency': 1.0 - retention_prob,
                    'estimated_benefit': (1.0 - retention_prob) * 0.8
                })
        
        return recommendations
    
    def _generate_challenge_recommendations(self, student: Student, performance_analysis: Dict,
                                          available_materials: List[LearningMaterial], max_count: int) -> List[Dict]:
        """Generate challenging recommendations for high-performing students"""
        recommendations = []
        
        overall_perf = performance_analysis.get('overall_performance', {})
        avg_score = overall_perf.get('average_score', 0)
        
        # Only generate challenges for students performing well
        if avg_score < 75:
            return recommendations
        
        # Find advanced materials in student's strong subjects
        strong_subjects = []
        subject_breakdown = performance_analysis.get('subject_breakdown', {})
        
        for subject, data in subject_breakdown.items():
            if data.get('average_score', 0) > 80:
                strong_subjects.append(subject)
        
        # Find advanced materials in strong subjects
        challenge_materials = [
            material for material in available_materials
            if (material.subject in strong_subjects and 
                material.difficulty_level == DifficultyLevel.ADVANCED and
                material.is_active)
        ]
        
        # Score challenge materials
        for material in challenge_materials[:max_count]:
            suitability = self.adaptive_engine.calculate_content_suitability(material, student)
            
            recommendations.append({
                'type': 'challenge',
                'material_id': material.id,
                'material': material,
                'topic': material.topic,
                'reasoning': f"Advanced challenge in your strong subject: {material.subject}",
                'suitability_score': suitability,
                'estimated_benefit': suitability * 0.6 + (avg_score / 100.0) * 0.4
            })
        
        return recommendations
    
    def _calculate_recommendation_score(self, recommendation: Dict, student: Student, 
                                      performance_analysis: Dict) -> float:
        """Calculate final recommendation score"""
        base_score = recommendation.get('estimated_benefit', 0.5)
        
        # Boost score based on recommendation type and student needs
        if recommendation['type'] == 'next_topic':
            base_score *= 1.2  # Prioritize forward progress
        elif recommendation['type'] == 'review':
            urgency = recommendation.get('urgency', 0.5)
            base_score *= (0.8 + urgency * 0.4)  # Scale review importance by urgency
        elif recommendation['type'] == 'challenge':
            recent_performance = performance_analysis.get('overall_performance', {}).get('average_score', 0)
            if recent_performance > 85:
                base_score *= 1.1  # Boost challenges for high performers
            else:
                base_score *= 0.7  # Reduce challenges for others
        
        # Factor in learning style compatibility
        if 'suitability_score' in recommendation:
            base_score = base_score * 0.7 + recommendation['suitability_score'] * 0.3
        
        return min(1.0, max(0.0, base_score))
    
    def generate_content_embeddings(self, materials: List[LearningMaterial]) -> Dict[int, List[float]]:
        """
        Generate vector embeddings for learning materials to enable similarity search
        """
        if not self.sentence_model:
            return {}
        
        embeddings = {}
        
        for material in materials:
            # Create text representation of material
            text_content = f"{material.title}. {material.description or ''}. Subject: {material.subject}. Topic: {material.topic}."
            
            if material.content_text:
                text_content += f" {material.content_text[:500]}"  # Limit to first 500 chars
            
            # Generate embedding
            try:
                embedding = self.sentence_model.encode(text_content).tolist()
                embeddings[material.id] = embedding
            except Exception as e:
                print(f"Error generating embedding for material {material.id}: {e}")
                continue
        
        return embeddings
    
    def find_similar_materials(self, target_material: LearningMaterial, 
                             all_materials: List[LearningMaterial], top_k: int = 5) -> List[Tuple[LearningMaterial, float]]:
        """
        Find materials similar to target material using content embeddings
        """
        if not self.sentence_model or not target_material.content_embedding:
            # Fallback to keyword-based similarity
            return self._keyword_similarity(target_material, all_materials, top_k)
        
        target_embedding = np.array(target_material.content_embedding).reshape(1, -1)
        similarities = []
        
        for material in all_materials:
            if material.id == target_material.id or not material.content_embedding:
                continue
            
            material_embedding = np.array(material.content_embedding).reshape(1, -1)
            similarity = cosine_similarity(target_embedding, material_embedding)[0][0]
            similarities.append((material, similarity))
        
        # Sort by similarity and return top k
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]
    
    def _keyword_similarity(self, target_material: LearningMaterial, 
                          all_materials: List[LearningMaterial], top_k: int) -> List[Tuple[LearningMaterial, float]]:
        """
        Fallback similarity calculation based on keywords and metadata
        """
        target_keywords = set(target_material.keywords or [])
        target_subject = target_material.subject.lower()
        target_topic = target_material.topic.lower()
        
        similarities = []
        
        for material in all_materials:
            if material.id == target_material.id:
                continue
            
            similarity = 0.0
            
            # Subject similarity (40% weight)
            if material.subject.lower() == target_subject:
                similarity += 0.4
            
            # Topic similarity (30% weight)
            if material.topic.lower() == target_topic:
                similarity += 0.3
            
            # Keyword similarity (30% weight)
            material_keywords = set(material.keywords or [])
            if target_keywords and material_keywords:
                keyword_overlap = len(target_keywords & material_keywords) / len(target_keywords | material_keywords)
                similarity += keyword_overlap * 0.3
            
            similarities.append((material, similarity))
        
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]