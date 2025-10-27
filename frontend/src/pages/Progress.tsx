import React, { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { api } from '../services/api'
import {
  ChartBarIcon,
  ClockIcon,
  TrophyIcon,
  AcademicCapIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline'
import LoadingSpinner from '../components/LoadingSpinner'

const Progress: React.FC = () => {
  const [selectedSubject, setSelectedSubject] = useState('')

  const { data: progressRecords, isLoading } = useQuery({
    queryKey: ['progress-records', selectedSubject],
    queryFn: () => api.getProgressRecords({ subject: selectedSubject || undefined })
  })

  const { data: analytics } = useQuery({
    queryKey: ['student-analytics'],
    queryFn: () => api.getStudentAnalytics(30)
  })

  const { data: summary } = useQuery({
    queryKey: ['progress-summary'],
    queryFn: api.getProgressSummary
  })

  if (isLoading) {
    return <LoadingSpinner />
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />
      case 'in_progress':
        return <ClockIcon className="h-5 w-5 text-blue-500" />
      default:
        return <ExclamationTriangleIcon className="h-5 w-5 text-gray-400" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'text-green-600 bg-green-100'
      case 'in_progress':
        return 'text-blue-600 bg-blue-100'
      default:
        return 'text-gray-600 bg-gray-100'
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Learning Progress</h1>
        <p className="text-gray-600 mt-1">Track your learning journey and performance analytics</p>
      </div>

      {/* Summary Cards */}
      {summary && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="card">
            <div className="flex items-center">
              <div className="p-2 bg-blue-100 rounded-lg">
                <ChartBarIcon className="h-6 w-6 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Average Score</p>
                <p className="text-2xl font-bold text-gray-900">{summary.average_score}%</p>
              </div>
            </div>
          </div>

          <div className="card">
            <div className="flex items-center">
              <div className="p-2 bg-green-100 rounded-lg">
                <TrophyIcon className="h-6 w-6 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Completion Rate</p>
                <p className="text-2xl font-bold text-gray-900">{summary.completion_rate}%</p>
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
                <p className="text-2xl font-bold text-gray-900">{Math.round(summary.total_study_time / 60)}h</p>
              </div>
            </div>
          </div>

          <div className="card">
            <div className="flex items-center">
              <div className="p-2 bg-orange-100 rounded-lg">
                <AcademicCapIcon className="h-6 w-6 text-orange-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Materials</p>
                <p className="text-2xl font-bold text-gray-900">{summary.completed_materials}/{summary.total_materials}</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Analytics Section */}
      {analytics && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Performance Trends */}
          <div className="card">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Performance Analysis</h2>
            
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="text-center p-3 bg-gray-50 rounded-lg">
                  <p className="text-sm text-gray-600">Learning Velocity</p>
                  <p className="text-lg font-bold text-blue-600">
                    {Math.round((analytics.learning_velocity?.velocity_score || 0) * 100)}%
                  </p>
                </div>
                <div className="text-center p-3 bg-gray-50 rounded-lg">
                  <p className="text-sm text-gray-600">Consistency</p>
                  <p className="text-lg font-bold text-green-600 capitalize">
                    {analytics.learning_patterns?.consistency_pattern || 'Unknown'}
                  </p>
                </div>
              </div>

              {analytics.strengths_weaknesses && (
                <div>
                  <h3 className="text-sm font-medium text-gray-700 mb-2">Strengths</h3>
                  <ul className="space-y-1">
                    {analytics.strengths_weaknesses.strengths?.map((strength: string, index: number) => (
                      <li key={index} className="text-sm text-green-600 flex items-center">
                        <CheckCircleIcon className="h-4 w-4 mr-2" />
                        {strength}
                      </li>
                    ))}
                  </ul>

                  {analytics.strengths_weaknesses.areas_for_improvement?.length > 0 && (
                    <>
                      <h3 className="text-sm font-medium text-gray-700 mb-2 mt-4">Areas for Improvement</h3>
                      <ul className="space-y-1">
                        {analytics.strengths_weaknesses.areas_for_improvement.map((area: string, index: number) => (
                          <li key={index} className="text-sm text-orange-600 flex items-center">
                            <ExclamationTriangleIcon className="h-4 w-4 mr-2" />
                            {area}
                          </li>
                        ))}
                      </ul>
                    </>
                  )}
                </div>
              )}
            </div>
          </div>

          {/* Subject Breakdown */}
          <div className="card">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Subject Performance</h2>
            
            {analytics.subject_breakdown && Object.keys(analytics.subject_breakdown).length > 0 ? (
              <div className="space-y-4">
                {Object.entries(analytics.subject_breakdown).map(([subject, data]: [string, any]) => (
                  <div key={subject} className="border-b border-gray-100 pb-3 last:border-b-0">
                    <div className="flex justify-between items-center mb-2">
                      <h3 className="text-sm font-medium text-gray-900">{subject}</h3>
                      <span className="text-sm font-semibold text-gray-900">
                        {Math.round(data.average_score)}%
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-primary-600 h-2 rounded-full"
                        style={{ width: `${Math.min(100, data.average_score)}%` }}
                      ></div>
                    </div>
                    <div className="flex justify-between text-xs text-gray-500 mt-1">
                      <span>{data.material_count} materials</span>
                      <span>{Math.round(data.completion_rate * 100)}% completed</span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500">No subject data available yet.</p>
            )}
          </div>
        </div>
      )}

      {/* Recent Progress */}
      <div className="card">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-semibold text-gray-900">Recent Activity</h2>
          <select
            value={selectedSubject}
            onChange={(e) => setSelectedSubject(e.target.value)}
            className="text-sm border border-gray-300 rounded-md px-3 py-1"
          >
            <option value="">All Subjects</option>
            {summary?.subjects_studied?.map((subject: string) => (
              <option key={subject} value={subject}>{subject}</option>
            ))}
          </select>
        </div>

        <div className="overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Material
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Score
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Time Spent
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Mastery
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {progressRecords?.map((record: any) => (
                <tr key={record.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div>
                      <div className="text-sm font-medium text-gray-900">{record.material_title}</div>
                      <div className="text-sm text-gray-500">{record.subject} • {record.topic}</div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      {getStatusIcon(record.completion_status)}
                      <span className={`ml-2 px-2 py-1 text-xs rounded-full ${getStatusColor(record.completion_status)}`}>
                        {record.completion_status.replace('_', ' ')}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {record.score ? `${Math.round(record.score)}%` : '-'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {record.time_spent} min
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="w-16 bg-gray-200 rounded-full h-2 mr-2">
                        <div
                          className="bg-green-500 h-2 rounded-full"
                          style={{ width: `${Math.round((record.mastery_level || 0) * 100)}%` }}
                        ></div>
                      </div>
                      <span className="text-sm text-gray-600">
                        {Math.round((record.mastery_level || 0) * 100)}%
                      </span>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {progressRecords?.length === 0 && (
            <div className="text-center py-8">
              <ChartBarIcon className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">No progress data</h3>
              <p className="mt-1 text-sm text-gray-500">
                Start learning to see your progress here!
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default Progress