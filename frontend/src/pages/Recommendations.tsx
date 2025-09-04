import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '../services/api'
import {
  LightBulbIcon,
  ArrowPathIcon,
  FireIcon,
  BookOpenIcon,
  ClockIcon,
  StarIcon,
  SparklesIcon
} from '@heroicons/react/24/outline'
import LoadingSpinner from '../components/LoadingSpinner'
import toast from 'react-hot-toast'

const Recommendations: React.FC = () => {
  const [selectedType, setSelectedType] = useState('')
  const [learningPathSubject, setLearningPathSubject] = useState('')
  const [learningPathTopics, setLearningPathTopics] = useState<string[]>([])
  const queryClient = useQueryClient()

  const { data: recommendations, isLoading } = useQuery({
    queryKey: ['recommendations', selectedType],
    queryFn: () => api.getRecommendations({ recommendation_type: selectedType || undefined })
  })

  const { data: subjects } = useQuery({
    queryKey: ['subjects'],
    queryFn: api.getAvailableSubjects
  })

  const { data: topics } = useQuery({
    queryKey: ['topics', learningPathSubject],
    queryFn: () => api.getAvailableTopics(learningPathSubject),
    enabled: !!learningPathSubject
  })

  const { data: adaptiveSuggestions } = useQuery({
    queryKey: ['adaptive-suggestions'],
    queryFn: api.getAdaptiveSuggestions
  })

  const generatePathMutation = useMutation({
    mutationFn: ({ subject, topics }: { subject: string, topics: string[] }) =>
      api.generateLearningPath(subject, topics),
    onSuccess: () => {
      toast.success('Learning path generated successfully!')
    },
    onError: () => {
      toast.error('Failed to generate learning path')
    }
  })

  const [generatedPath, setGeneratedPath] = useState<any>(null)

  const handleGeneratePath = () => {
    if (!learningPathSubject || learningPathTopics.length === 0) {
      toast.error('Please select a subject and at least one topic')
      return
    }

    generatePathMutation.mutate(
      { subject: learningPathSubject, topics: learningPathTopics },
      {
        onSuccess: (data) => {
          setGeneratedPath(data)
        }
      }
    )
  }

  const getRecommendationIcon = (type: string) => {
    switch (type) {
      case 'next_topic':
        return ArrowPathIcon
      case 'review':
        return ArrowPathIcon
      case 'challenge':
        return FireIcon
      default:
        return LightBulbIcon
    }
  }

  const getRecommendationColor = (type: string) => {
    switch (type) {
      case 'next_topic':
        return 'bg-blue-100 text-blue-800'
      case 'review':
        return 'bg-yellow-100 text-yellow-800'
      case 'challenge':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  if (isLoading) {
    return <LoadingSpinner />
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">AI Recommendations</h1>
        <p className="text-gray-600 mt-1">Personalized learning suggestions powered by AI</p>
      </div>

      {/* Adaptive Suggestions Banner */}
      {adaptiveSuggestions && (
        <div className="card bg-gradient-to-r from-primary-50 to-blue-50 border-primary-200">
          <div className="flex items-start">
            <SparklesIcon className="h-6 w-6 text-primary-600 mt-1" />
            <div className="ml-3">
              <h3 className="text-lg font-semibold text-gray-900">Adaptive Learning Insights</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-3">
                <div>
                  <p className="text-sm text-gray-600">Optimal Session</p>
                  <p className="font-medium">{adaptiveSuggestions.suggestions?.session_length || 30} minutes</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Difficulty Level</p>
                  <p className="font-medium capitalize">{adaptiveSuggestions.optimal_difficulty}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Break Frequency</p>
                  <p className="font-medium">Every {adaptiveSuggestions.suggestions?.break_frequency || 15} min</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Trend</p>
                  <p className={`font-medium capitalize ${
                    adaptiveSuggestions.performance_trend === 'improving' 
                      ? 'text-green-600' 
                      : 'text-gray-600'
                  }`}>
                    {adaptiveSuggestions.performance_trend}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Learning Path Generator */}
      <div className="card">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Generate Learning Path</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Subject</label>
            <select
              value={learningPathSubject}
              onChange={(e) => setLearningPathSubject(e.target.value)}
              className="input-field"
            >
              <option value="">Select Subject</option>
              {subjects?.subjects?.map((subject: string) => (
                <option key={subject} value={subject}>{subject}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Topics</label>
            <select
              multiple
              value={learningPathTopics}
              onChange={(e) => setLearningPathTopics(Array.from(e.target.selectedOptions, option => option.value))}
              className="input-field"
              disabled={!learningPathSubject}
              size={3}
            >
              {topics?.topics?.map((topic: string) => (
                <option key={topic} value={topic}>{topic}</option>
              ))}
            </select>
            <p className="text-xs text-gray-500 mt-1">Hold Ctrl/Cmd to select multiple</p>
          </div>

          <div className="flex items-end">
            <button
              onClick={handleGeneratePath}
              disabled={generatePathMutation.isPending}
              className="w-full btn-primary"
            >
              {generatePathMutation.isPending ? 'Generating...' : 'Generate Path'}
            </button>
          </div>
        </div>

        {/* Generated Path Display */}
        {generatedPath && (
          <div className="mt-6 p-4 bg-gray-50 rounded-lg">
            <h3 className="font-semibold text-gray-900 mb-3">Generated Learning Path</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-2 mb-4 text-sm">
              <div>
                <span className="text-gray-600">Total Duration: </span>
                <span className="font-medium">{generatedPath.total_duration} minutes</span>
              </div>
              <div>
                <span className="text-gray-600">Path ID: </span>
                <span className="font-mono text-xs">{generatedPath.path_id}</span>
              </div>
              <div>
                <span className="text-gray-600">Difficulty: </span>
                <span className="font-medium">{generatedPath.difficulty_progression?.join(' → ')}</span>
              </div>
            </div>
            
            <div className="space-y-2">
              {generatedPath.recommendations?.map((item: any, index: number) => (
                <div key={index} className="flex items-center p-3 bg-white rounded border">
                  <div className="flex-shrink-0 w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center text-sm font-medium text-primary-600">
                    {index + 1}
                  </div>
                  <div className="ml-3 flex-1">
                    <p className="font-medium text-gray-900">{item.material_title}</p>
                    <p className="text-sm text-gray-600">{item.topic} • {item.estimated_duration} min</p>
                  </div>
                  <div className="text-right">
                    <div className="text-sm text-gray-500">Suitability</div>
                    <div className="text-sm font-medium">
                      {Math.round((item.suitability_score || 0) * 100)}%
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Recommendations List */}
      <div className="card">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-semibold text-gray-900">Personalized Recommendations</h2>
          <select
            value={selectedType}
            onChange={(e) => setSelectedType(e.target.value)}
            className="text-sm border border-gray-300 rounded-md px-3 py-1"
          >
            <option value="">All Types</option>
            <option value="next_topic">Next Topic</option>
            <option value="review">Review</option>
            <option value="challenge">Challenge</option>
          </select>
        </div>

        {recommendations?.length > 0 ? (
          <div className="space-y-4">
            {recommendations.map((rec: any, index: number) => {
              const RecommendationIcon = getRecommendationIcon(rec.recommendation_type)
              
              return (
                <div key={index} className="border border-gray-200 rounded-lg p-4 hover:border-primary-300 transition-colors">
                  <div className="flex items-start justify-between">
                    <div className="flex items-start space-x-3">
                      <div className="p-2 bg-gray-100 rounded-lg">
                        <RecommendationIcon className="h-5 w-5 text-gray-600" />
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-1">
                          <h3 className="font-semibold text-gray-900">{rec.material_title}</h3>
                          <span className={`px-2 py-1 text-xs rounded-full ${getRecommendationColor(rec.recommendation_type)}`}>
                            {rec.recommendation_type.replace('_', ' ')}
                          </span>
                        </div>
                        <p className="text-sm text-gray-600 mb-2">{rec.reasoning}</p>
                        <div className="flex items-center space-x-4 text-sm text-gray-500">
                          <span>{rec.subject} • {rec.topic}</span>
                          {rec.estimated_duration && (
                            <>
                              <ClockIcon className="h-4 w-4" />
                              <span>{rec.estimated_duration} min</span>
                            </>
                          )}
                        </div>
                      </div>
                    </div>
                    
                    <div className="text-right">
                      <div className="text-xs text-gray-500">Confidence</div>
                      <div className="flex items-center space-x-1">
                        <StarIcon className="h-4 w-4 text-yellow-400" />
                        <span className="text-sm font-medium">
                          {Math.round(rec.confidence_score * 100)}%
                        </span>
                      </div>
                    </div>
                  </div>

                  {rec.predicted_performance && (
                    <div className="mt-3 p-3 bg-gray-50 rounded-md">
                      <h4 className="text-sm font-medium text-gray-700 mb-2">AI Prediction</h4>
                      <div className="grid grid-cols-3 gap-4 text-sm">
                        <div>
                          <span className="text-gray-600">Expected Score: </span>
                          <span className="font-medium">{Math.round(rec.predicted_performance.predicted_score)}%</span>
                        </div>
                        <div>
                          <span className="text-gray-600">Completion Probability: </span>
                          <span className="font-medium">{Math.round(rec.predicted_performance.completion_probability * 100)}%</span>
                        </div>
                        <div>
                          <span className="text-gray-600">Est. Time: </span>
                          <span className="font-medium">{rec.predicted_performance.estimated_completion_time} min</span>
                        </div>
                      </div>
                    </div>
                  )}

                  <div className="mt-3 flex space-x-2">
                    <button
                      onClick={async () => {
                        try {
                          await api.createProgress({
                            learning_material_id: rec.material_id,
                            completion_percentage: 0,
                            time_spent: 0
                          })
                          toast.success('Started learning!')
                        } catch (error) {
                          console.error('Error starting material:', error)
                        }
                      }}
                      className="btn-primary text-sm py-1 px-3"
                    >
                      Start Learning
                    </button>
                    <button
                      onClick={async () => {
                        try {
                          await api.submitRecommendationFeedback({
                            recommendation_id: rec.id || 0,
                            was_helpful: true,
                            was_completed: false
                          })
                          toast.success('Feedback recorded!')
                        } catch (error) {
                          console.error('Error submitting feedback:', error)
                        }
                      }}
                      className="btn-secondary text-sm py-1 px-3"
                    >
                      Helpful
                    </button>
                  </div>
                </div>
              )
            })}
          </div>
        ) : (
          <div className="text-center py-8">
            <LightBulbIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No recommendations available</h3>
            <p className="mt-1 text-sm text-gray-500">
              Complete more learning materials to get personalized recommendations!
            </p>
          </div>
        )}
      </div>
    </div>
  )
}

export default Recommendations