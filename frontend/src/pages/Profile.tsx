import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import { api } from '../services/api'
import { useAuth } from '../hooks/useAuth'
import {
  UserIcon,
  CogIcon,
  ChartBarIcon,
  EyeIcon,
  SpeakerWaveIcon,
  HandRaisedIcon,
  DocumentTextIcon
} from '@heroicons/react/24/outline'
import LoadingSpinner from '../components/LoadingSpinner'
import toast from 'react-hot-toast'

interface ProfileUpdateForm {
  first_name: string
  last_name: string
  difficulty_preference: string
}

interface LearningStyleForm {
  visual_score: number
  auditory_score: number
  kinesthetic_score: number
  reading_writing_score: number
}

const Profile: React.FC = () => {
  const [activeTab, setActiveTab] = useState('profile')
  const { user, refetchUser } = useAuth()
  const queryClient = useQueryClient()

  const { data: profile } = useQuery({
    queryKey: ['student-profile'],
    queryFn: api.getStudentProfile
  })

  const { data: learningStyleAnalysis } = useQuery({
    queryKey: ['learning-style-analysis'],
    queryFn: api.getLearningStyleAnalysis
  })

  const profileForm = useForm<ProfileUpdateForm>({
    defaultValues: {
      first_name: profile?.first_name || '',
      last_name: profile?.last_name || '',
      difficulty_preference: profile?.difficulty_preference || 'intermediate'
    }
  })

  const styleForm = useForm<LearningStyleForm>({
    defaultValues: {
      visual_score: 0.25,
      auditory_score: 0.25,
      kinesthetic_score: 0.25,
      reading_writing_score: 0.25
    }
  })

  const updateProfileMutation = useMutation({
    mutationFn: api.updateStudentProfile,
    onSuccess: () => {
      toast.success('Profile updated successfully!')
      refetchUser()
      queryClient.invalidateQueries({ queryKey: ['student-profile'] })
    },
    onError: () => {
      toast.error('Failed to update profile')
    }
  })

  const updateLearningStyleMutation = useMutation({
    mutationFn: api.submitLearningStyleAssessment,
    onSuccess: () => {
      toast.success('Learning style updated!')
      refetchUser()
      queryClient.invalidateQueries({ queryKey: ['learning-style-analysis'] })
    },
    onError: () => {
      toast.error('Failed to update learning style')
    }
  })

  const onUpdateProfile = (data: ProfileUpdateForm) => {
    updateProfileMutation.mutate(data)
  }

  const onUpdateLearningStyle = (data: LearningStyleForm) => {
    // Normalize scores to sum to 1
    const total = data.visual_score + data.auditory_score + data.kinesthetic_score + data.reading_writing_score
    if (total > 0) {
      updateLearningStyleMutation.mutate({
        visual_score: data.visual_score / total,
        auditory_score: data.auditory_score / total,
        kinesthetic_score: data.kinesthetic_score / total,
        reading_writing_score: data.reading_writing_score / total
      })
    }
  }

  const tabs = [
    { id: 'profile', name: 'Profile Settings', icon: UserIcon },
    { id: 'learning-style', name: 'Learning Style', icon: ChartBarIcon },
    { id: 'preferences', name: 'Preferences', icon: CogIcon }
  ]

  const getLearningStyleIcon = (style: string) => {
    switch (style) {
      case 'visual':
        return EyeIcon
      case 'auditory':
        return SpeakerWaveIcon
      case 'kinesthetic':
        return HandRaisedIcon
      case 'reading_writing':
        return DocumentTextIcon
      default:
        return ChartBarIcon
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Profile & Settings</h1>
        <p className="text-gray-600 mt-1">Manage your learning profile and preferences</p>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`group inline-flex items-center py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.id
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <tab.icon className={`mr-2 h-5 w-5 ${
                activeTab === tab.id ? 'text-primary-500' : 'text-gray-400'
              }`} />
              {tab.name}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      {activeTab === 'profile' && (
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Personal Information</h2>
          
          <form onSubmit={profileForm.handleSubmit(onUpdateProfile)} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">First Name</label>
                <input
                  {...profileForm.register('first_name', { required: 'First name is required' })}
                  type="text"
                  className="input-field mt-1"
                  placeholder={user?.first_name}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Last Name</label>
                <input
                  {...profileForm.register('last_name', { required: 'Last name is required' })}
                  type="text"
                  className="input-field mt-1"
                  placeholder={user?.last_name}
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Preferred Difficulty</label>
              <select
                {...profileForm.register('difficulty_preference')}
                className="input-field mt-1"
              >
                <option value="beginner">Beginner</option>
                <option value="intermediate">Intermediate</option>
                <option value="advanced">Advanced</option>
              </select>
            </div>

            <button
              type="submit"
              disabled={updateProfileMutation.isPending}
              className="btn-primary"
            >
              {updateProfileMutation.isPending ? 'Updating...' : 'Update Profile'}
            </button>
          </form>
        </div>
      )}

      {activeTab === 'learning-style' && (
        <div className="space-y-6">
          {/* Current Learning Style */}
          <div className="card">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Current Learning Style Profile</h2>
            
            {learningStyleAnalysis ? (
              <div>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                  {Object.entries(learningStyleAnalysis.detected_styles || {}).map(([style, score]: [string, any]) => {
                    const StyleIcon = getLearningStyleIcon(style)
                    return (
                      <div key={style} className="text-center p-4 border border-gray-200 rounded-lg">
                        <StyleIcon className="h-8 w-8 mx-auto text-primary-600 mb-2" />
                        <h3 className="text-sm font-medium text-gray-900 capitalize mb-1">
                          {style.replace('_', ' ')}
                        </h3>
                        <div className="w-full bg-gray-200 rounded-full h-2 mb-1">
                          <div
                            className="bg-primary-600 h-2 rounded-full"
                            style={{ width: `${Math.round(score * 100)}%` }}
                          ></div>
                        </div>
                        <span className="text-xs text-gray-600">{Math.round(score * 100)}%</span>
                      </div>
                    )
                  })}
                </div>
                
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <p className="text-sm text-blue-800">
                    <strong>AI Analysis:</strong> Your dominant learning style is{' '}
                    <span className="font-semibold">{learningStyleAnalysis.dominant_style?.replace('_', ' ')}</span>{' '}
                    with {Math.round((learningStyleAnalysis.confidence || 0) * 100)}% confidence.
                  </p>
                </div>
              </div>
            ) : (
              <p className="text-gray-500">Complete some learning materials for AI-powered style detection.</p>
            )}
          </div>

          {/* Manual Assessment */}
          <div className="card">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Manual Learning Style Assessment</h2>
            <p className="text-sm text-gray-600 mb-6">
              Rate how much each learning approach appeals to you (0-10 scale). The system will normalize these scores.
            </p>
            
            <form onSubmit={styleForm.handleSubmit(onUpdateLearningStyle)} className="space-y-6">
              <div className="space-y-4">
                <div className="flex items-center space-x-4">
                  <EyeIcon className="h-6 w-6 text-primary-600" />
                  <div className="flex-1">
                    <label className="block text-sm font-medium text-gray-700">Visual (Charts, Diagrams, Images)</label>
                    <input
                      {...styleForm.register('visual_score', { min: 0, max: 10 })}
                      type="range"
                      min="0"
                      max="10"
                      step="0.5"
                      className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer mt-2"
                    />
                    <div className="flex justify-between text-xs text-gray-500 mt-1">
                      <span>Not at all</span>
                      <span>Extremely appealing</span>
                    </div>
                  </div>
                  <span className="text-sm font-medium w-8">{styleForm.watch('visual_score')}</span>
                </div>

                <div className="flex items-center space-x-4">
                  <SpeakerWaveIcon className="h-6 w-6 text-primary-600" />
                  <div className="flex-1">
                    <label className="block text-sm font-medium text-gray-700">Auditory (Lectures, Discussions, Audio)</label>
                    <input
                      {...styleForm.register('auditory_score', { min: 0, max: 10 })}
                      type="range"
                      min="0"
                      max="10"
                      step="0.5"
                      className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer mt-2"
                    />
                    <div className="flex justify-between text-xs text-gray-500 mt-1">
                      <span>Not at all</span>
                      <span>Extremely appealing</span>
                    </div>
                  </div>
                  <span className="text-sm font-medium w-8">{styleForm.watch('auditory_score')}</span>
                </div>

                <div className="flex items-center space-x-4">
                  <HandRaisedIcon className="h-6 w-6 text-primary-600" />
                  <div className="flex-1">
                    <label className="block text-sm font-medium text-gray-700">Kinesthetic (Hands-on, Practice, Movement)</label>
                    <input
                      {...styleForm.register('kinesthetic_score', { min: 0, max: 10 })}
                      type="range"
                      min="0"
                      max="10"
                      step="0.5"
                      className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer mt-2"
                    />
                    <div className="flex justify-between text-xs text-gray-500 mt-1">
                      <span>Not at all</span>
                      <span>Extremely appealing</span>
                    </div>
                  </div>
                  <span className="text-sm font-medium w-8">{styleForm.watch('kinesthetic_score')}</span>
                </div>

                <div className="flex items-center space-x-4">
                  <DocumentTextIcon className="h-6 w-6 text-primary-600" />
                  <div className="flex-1">
                    <label className="block text-sm font-medium text-gray-700">Reading/Writing (Text, Articles, Notes)</label>
                    <input
                      {...styleForm.register('reading_writing_score', { min: 0, max: 10 })}
                      type="range"
                      min="0"
                      max="10"
                      step="0.5"
                      className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer mt-2"
                    />
                    <div className="flex justify-between text-xs text-gray-500 mt-1">
                      <span>Not at all</span>
                      <span>Extremely appealing</span>
                    </div>
                  </div>
                  <span className="text-sm font-medium w-8">{styleForm.watch('reading_writing_score')}</span>
                </div>
              </div>

              <button
                type="submit"
                disabled={updateLearningStyleMutation.isPending}
                className="btn-primary"
              >
                {updateLearningStyleMutation.isPending ? 'Updating...' : 'Update Learning Style'}
              </button>
            </form>
          </div>
        </div>
      )}

      {activeTab === 'preferences' && (
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Learning Preferences</h2>
          
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 className="text-sm font-medium text-gray-700 mb-3">Performance Overview</h3>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Overall Performance</span>
                    <span className="text-sm font-medium">{user?.performance_score || 0}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Learning Streak</span>
                    <span className="text-sm font-medium">{user?.learning_streak || 0} days</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Dominant Style</span>
                    <span className="text-sm font-medium capitalize">
                      {user?.dominant_learning_style?.replace('_', ' ') || 'Not determined'}
                    </span>
                  </div>
                </div>
              </div>

              <div>
                <h3 className="text-sm font-medium text-gray-700 mb-3">Learning Statistics</h3>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Account Created</span>
                    <span className="text-sm font-medium">
                      {new Date().toLocaleDateString()}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Last Login</span>
                    <span className="text-sm font-medium">Today</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Total Study Time</span>
                    <span className="text-sm font-medium">
                      {Math.round((user?.total_study_time || 0) / 60)} hours
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {learningStyleAnalysis && learningStyleAnalysis.current_styles && (
              <div>
                <h3 className="text-sm font-medium text-gray-700 mb-3">Current Learning Style Distribution</h3>
                <div className="space-y-3">
                  {Object.entries(learningStyleAnalysis.current_styles).map(([style, score]: [string, any]) => (
                    <div key={style} className="flex items-center justify-between">
                      <span className="text-sm text-gray-700 capitalize">{style.replace('_', ' ')}</span>
                      <div className="flex items-center space-x-3">
                        <div className="w-32 bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-primary-600 h-2 rounded-full"
                            style={{ width: `${Math.round(score * 100)}%` }}
                          ></div>
                        </div>
                        <span className="text-sm font-medium w-8">{Math.round(score * 100)}%</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default Profile