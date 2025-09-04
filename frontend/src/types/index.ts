// Type definitions for the AI Personalized Learning System

export interface User {
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
  learning_style_scores?: Record<string, number>
  dominant_learning_style?: string
  difficulty_preference?: string
  performance_score: number
  learning_streak: number
  total_study_time: number
}

export interface LearningMaterial {
  id: number
  title: string
  description?: string
  content_type: 'text' | 'video' | 'interactive' | 'quiz' | 'audio' | 'simulation'
  content_url?: string
  subject: string
  topic: string
  difficulty_level: 'beginner' | 'intermediate' | 'advanced'
  estimated_duration?: number
  learning_styles: string[]
  tags: string[]
  average_rating: number
  complexity_score: number
}

export interface ProgressRecord {
  id: number
  learning_material_id: number
  material_title: string
  subject: string
  topic: string
  completion_status: 'not_started' | 'in_progress' | 'completed' | 'abandoned'
  completion_percentage: number
  time_spent: number
  score?: number
  mastery_level: number
  created_at: string
  updated_at: string
}

export interface Recommendation {
  id?: number
  material_id: number
  material_title: string
  subject: string
  topic: string
  recommendation_type: 'next_topic' | 'review' | 'challenge' | 'remedial'
  reasoning: string
  confidence_score: number
  priority_score: number
  estimated_duration?: number
  predicted_performance?: {
    predicted_score: number
    completion_probability: number
    estimated_completion_time: number
    confidence: number
  }
}

export interface LearningPath {
  path_id: string
  total_duration: number
  difficulty_progression: string[]
  recommendations: Array<{
    material_id: number
    material_title: string
    topic: string
    difficulty: string
    estimated_duration: number
    suitability_score: number
    recommended_order: number
  }>
}

export interface PerformanceAnalytics {
  overall_performance: {
    average_score: number
    score_std: number
    completion_rate: number
    total_materials_attempted: number
    materials_completed: number
    performance_trend: 'improving' | 'declining' | 'stable'
  }
  learning_velocity: {
    velocity_score: number
    acceleration: number
    mastery_consistency: number
  }
  subject_breakdown: Record<string, {
    average_score: number
    completion_rate: number
    average_time: number
    mastery_level: number
    material_count: number
    performance_category: string
  }>
  learning_patterns: {
    preferred_session_length: number
    peak_performance_time: string
    consistency_pattern: string
    challenge_response: string
  }
  strengths_weaknesses: {
    strengths: string[]
    areas_for_improvement: string[]
    improvement_suggestions: string[]
  }
  engagement_trends: {
    trend: string
    average_engagement: number
    engagement_variance?: number
    recent_engagement?: number
  }
  recommendations: string[]
}