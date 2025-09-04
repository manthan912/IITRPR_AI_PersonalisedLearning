import React, { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { api } from '../services/api'
import {
  BookOpenIcon,
  VideoCameraIcon,
  PlayIcon,
  DocumentTextIcon,
  PuzzlePieceIcon,
  StarIcon,
  ClockIcon
} from '@heroicons/react/24/outline'
import LoadingSpinner from '../components/LoadingSpinner'

const LearningMaterials: React.FC = () => {
  const [filters, setFilters] = useState({
    subject: '',
    topic: '',
    difficulty: '',
    content_type: '',
    personalized: true
  })

  const { data: materials, isLoading } = useQuery({
    queryKey: ['learning-materials', filters],
    queryFn: () => api.getLearningMaterials(filters)
  })

  const { data: subjects } = useQuery({
    queryKey: ['subjects'],
    queryFn: api.getAvailableSubjects
  })

  const { data: topics } = useQuery({
    queryKey: ['topics', filters.subject],
    queryFn: () => api.getAvailableTopics(filters.subject || undefined),
    enabled: !!filters.subject
  })

  const getContentTypeIcon = (contentType: string) => {
    switch (contentType) {
      case 'video':
        return VideoCameraIcon
      case 'interactive':
        return PlayIcon
      case 'quiz':
        return PuzzlePieceIcon
      case 'audio':
        return VideoCameraIcon
      default:
        return DocumentTextIcon
    }
  }

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'beginner':
        return 'bg-green-100 text-green-800'
      case 'intermediate':
        return 'bg-yellow-100 text-yellow-800'
      case 'advanced':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const startMaterial = async (materialId: number) => {
    try {
      await api.createProgress({
        learning_material_id: materialId,
        completion_percentage: 0,
        time_spent: 0
      })
      // In a real app, navigate to the learning material
      alert('Material started! (In a full implementation, this would open the learning content)')
    } catch (error) {
      console.error('Error starting material:', error)
    }
  }

  if (isLoading) {
    return <LoadingSpinner />
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Learning Materials</h1>
        <p className="text-gray-600 mt-1">Discover personalized content adapted to your learning style</p>
      </div>

      {/* Filters */}
      <div className="card">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Filter Materials</h2>
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Subject</label>
            <select
              value={filters.subject}
              onChange={(e) => setFilters({ ...filters, subject: e.target.value, topic: '' })}
              className="input-field"
            >
              <option value="">All Subjects</option>
              {subjects?.subjects?.map((subject: string) => (
                <option key={subject} value={subject}>{subject}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Topic</label>
            <select
              value={filters.topic}
              onChange={(e) => setFilters({ ...filters, topic: e.target.value })}
              className="input-field"
              disabled={!filters.subject}
            >
              <option value="">All Topics</option>
              {topics?.topics?.map((topic: string) => (
                <option key={topic} value={topic}>{topic}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Difficulty</label>
            <select
              value={filters.difficulty}
              onChange={(e) => setFilters({ ...filters, difficulty: e.target.value })}
              className="input-field"
            >
              <option value="">All Levels</option>
              <option value="beginner">Beginner</option>
              <option value="intermediate">Intermediate</option>
              <option value="advanced">Advanced</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Content Type</label>
            <select
              value={filters.content_type}
              onChange={(e) => setFilters({ ...filters, content_type: e.target.value })}
              className="input-field"
            >
              <option value="">All Types</option>
              <option value="text">Text</option>
              <option value="video">Video</option>
              <option value="interactive">Interactive</option>
              <option value="quiz">Quiz</option>
              <option value="audio">Audio</option>
            </select>
          </div>

          <div className="flex items-end">
            <label className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={filters.personalized}
                onChange={(e) => setFilters({ ...filters, personalized: e.target.checked })}
                className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
              />
              <span className="text-sm text-gray-700">Personalized</span>
            </label>
          </div>
        </div>
      </div>

      {/* Materials Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {materials?.map((material: any) => {
          const ContentIcon = getContentTypeIcon(material.content_type)
          
          return (
            <div key={material.id} className="card hover:shadow-lg transition-shadow duration-200">
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center space-x-2">
                  <div className="p-2 bg-primary-100 rounded-lg">
                    <ContentIcon className="h-5 w-5 text-primary-600" />
                  </div>
                  <div>
                    <span className={`px-2 py-1 text-xs rounded-full ${getDifficultyColor(material.difficulty_level)}`}>
                      {material.difficulty_level}
                    </span>
                  </div>
                </div>
                <div className="flex items-center space-x-1">
                  <StarIcon className="h-4 w-4 text-yellow-400" />
                  <span className="text-sm text-gray-600">{material.average_rating.toFixed(1)}</span>
                </div>
              </div>

              <h3 className="text-lg font-semibold text-gray-900 mb-2">{material.title}</h3>
              <p className="text-sm text-gray-600 mb-3 line-clamp-2">{material.description}</p>

              <div className="flex items-center justify-between text-sm text-gray-500 mb-4">
                <span className="font-medium">{material.subject}</span>
                <div className="flex items-center space-x-1">
                  <ClockIcon className="h-4 w-4" />
                  <span>{material.estimated_duration || 30} min</span>
                </div>
              </div>

              <div className="mb-4">
                <p className="text-xs text-gray-500 mb-1">Learning Styles:</p>
                <div className="flex flex-wrap gap-1">
                  {material.learning_styles?.map((style: string) => (
                    <span
                      key={style}
                      className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full"
                    >
                      {style.replace('_', ' ')}
                    </span>
                  ))}
                </div>
              </div>

              <button
                onClick={() => startMaterial(material.id)}
                className="w-full btn-primary"
              >
                Start Learning
              </button>
            </div>
          )
        })}
      </div>

      {materials?.length === 0 && (
        <div className="text-center py-12">
          <BookOpenIcon className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No materials found</h3>
          <p className="mt-1 text-sm text-gray-500">
            Try adjusting your filters or check back later for new content.
          </p>
        </div>
      )}
    </div>
  )
}

export default LearningMaterials