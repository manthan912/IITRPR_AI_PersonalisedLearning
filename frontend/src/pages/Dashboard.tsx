import React from 'react'
import { useQuery } from '@tanstack/react-query'
import { api } from '../services/api'
import {
  ChartBarIcon,
  BookOpenIcon,
  ClockIcon,
  TrophyIcon,
  LightBulbIcon,
  FireIcon
} from '@heroicons/react/24/outline'
import LoadingSpinner from '../components/LoadingSpinner'

const Dashboard: React.FC = () => {
  const { data: analytics, isLoading: analyticsLoading } = useQuery({
    queryKey: ['student-analytics'],
    queryFn: () => api.getStudentAnalytics(30)
  })

  const { data: progressSummary, isLoading: progressLoading } = useQuery({
    queryKey: ['progress-summary'],
    queryFn: api.getProgressSummary
  })

  const { data: recommendations, isLoading: recLoading } = useQuery({
    queryKey: ['recommendations'],
    queryFn: () => api.getRecommendations({ limit: 3 })
  })

  const { data: adaptiveSuggestions } = useQuery({
    queryKey: ['adaptive-suggestions'],
    queryFn: api.getAdaptiveSuggestions
  })

  if (analyticsLoading || progressLoading) {
    return <LoadingSpinner />
  }

  const overallPerformance = analytics?.overall_performance || {}
  const summary = progressSummary || {}

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Learning Dashboard</h1>
        <p className="text-gray-600 mt-1">Track your personalized learning journey</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="card">
          <div className="flex items-center">
            <div className="p-2 bg-blue-100 rounded-lg">
              <ChartBarIcon className="h-6 w-6 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Average Score</p>
              <p className="text-2xl font-bold text-gray-900">{summary.average_score || 0}%</p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="p-2 bg-green-100 rounded-lg">
              <BookOpenIcon className="h-6 w-6 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Completed</p>
              <p className="text-2xl font-bold text-gray-900">{summary.completed_materials || 0}</p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="p-2 bg-purple-100 rounded-lg">
              <ClockIcon className="h-6 w-6 text-purple-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Study Time</p>
              <p className="text-2xl font-bold text-gray-900">{Math.round((summary.total_study_time || 0) / 60)}h</p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="p-2 bg-orange-100 rounded-lg">
              <FireIcon className="h-6 w-6 text-orange-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Learning Streak</p>
              <p className="text-2xl font-bold text-gray-900">{summary.learning_streak || 0} days</p>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Performance Trends */}
        <div className="lg:col-span-2">
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900">Performance Overview</h2>
              <TrophyIcon className="h-5 w-5 text-gray-400" />
            </div>
            
            {analytics ? (
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="text-center p-4 bg-gray-50 rounded-lg">
                    <p className="text-sm text-gray-600">Completion Rate</p>
                    <p className="text-xl font-bold text-green-600">
                      {Math.round((overallPerformance.completion_rate || 0) * 100)}%
                    </p>
                  </div>
                  <div className="text-center p-4 bg-gray-50 rounded-lg">
                    <p className="text-sm text-gray-600">Performance Trend</p>
                    <p className="text-xl font-bold text-blue-600 capitalize">
                      {overallPerformance.performance_trend || 'Stable'}
                    </p>
                  </div>
                </div>
                
                {analytics.subject_breakdown && (
                  <div className="mt-4">
                    <h3 className="text-sm font-medium text-gray-700 mb-2">Subject Performance</h3>
                    <div className="space-y-2">
                      {Object.entries(analytics.subject_breakdown).map(([subject, data]: [string, any]) => (
                        <div key={subject} className="flex justify-between items-center">
                          <span className="text-sm text-gray-600">{subject}</span>
                          <div className="flex items-center space-x-2">
                            <div className="w-24 bg-gray-200 rounded-full h-2">
                              <div 
                                className="bg-primary-600 h-2 rounded-full" 
                                style={{ width: `${Math.min(100, data.average_score || 0)}%` }}
                              ></div>
                            </div>
                            <span className="text-sm font-medium text-gray-900">
                              {Math.round(data.average_score || 0)}%
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <p className="text-gray-500">No performance data available yet. Start learning to see your progress!</p>
            )}
          </div>
        </div>

        {/* AI Recommendations */}
        <div className="space-y-6">
          {/* Current Recommendations */}
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900">AI Recommendations</h2>
              <LightBulbIcon className="h-5 w-5 text-yellow-500" />
            </div>
            
            {recLoading ? (
              <div className="animate-pulse space-y-3">
                <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                <div className="h-4 bg-gray-200 rounded w-1/2"></div>
              </div>
            ) : recommendations?.length > 0 ? (
              <div className="space-y-3">
                {recommendations.slice(0, 3).map((rec: any, index: number) => (
                  <div key={index} className="p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <p className="text-sm font-medium text-gray-900">{rec.material_title}</p>
                        <p className="text-xs text-gray-600 mt-1">{rec.reasoning}</p>
                        <div className="flex items-center mt-2 space-x-2">
                          <span className={`px-2 py-1 text-xs rounded-full ${
                            rec.recommendation_type === 'next_topic' 
                              ? 'bg-blue-100 text-blue-800'
                              : rec.recommendation_type === 'review'
                              ? 'bg-yellow-100 text-yellow-800'
                              : 'bg-purple-100 text-purple-800'
                          }`}>
                            {rec.recommendation_type.replace('_', ' ')}
                          </span>
                          <span className="text-xs text-gray-500">
                            {rec.estimated_duration || 30} min
                          </span>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-xs text-gray-500">Confidence</div>
                        <div className="text-sm font-medium text-gray-900">
                          {Math.round((rec.confidence_score || 0) * 100)}%
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-sm">
                Complete some learning materials to get personalized recommendations!
              </p>
            )}
          </div>

          {/* Adaptive Suggestions */}
          {adaptiveSuggestions && (
            <div className="card">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Learning Optimization</h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Recommended Session Length</span>
                  <span className="text-sm font-medium text-gray-900">
                    {adaptiveSuggestions.suggestions?.session_length || 30} min
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Optimal Difficulty</span>
                  <span className="text-sm font-medium text-gray-900 capitalize">
                    {adaptiveSuggestions.optimal_difficulty || 'Intermediate'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Break Frequency</span>
                  <span className="text-sm font-medium text-gray-900">
                    Every {adaptiveSuggestions.suggestions?.break_frequency || 15} min
                  </span>
                </div>
                {adaptiveSuggestions.performance_trend && (
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Performance Trend</span>
                    <span className={`text-sm font-medium capitalize ${
                      adaptiveSuggestions.performance_trend === 'improving' 
                        ? 'text-green-600' 
                        : adaptiveSuggestions.performance_trend === 'declining'
                        ? 'text-red-600'
                        : 'text-gray-900'
                    }`}>
                      {adaptiveSuggestions.performance_trend}
                    </span>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default Dashboard