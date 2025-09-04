import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000/api'

// Create axios instance with interceptors
const apiClient = axios.create({
  baseURL: API_BASE_URL,
})

// Add auth token to requests
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Handle auth errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export const api = {
  // Authentication
  async login(username: string, password: string) {
    const response = await axios.post(`${API_BASE_URL}/auth/token`, {
      username,
      password,
    }, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      data: new URLSearchParams({ username, password })
    })
    return response.data
  },

  async register(userData: any) {
    const response = await axios.post(`${API_BASE_URL}/auth/register`, userData)
    return response.data
  },

  async getCurrentUser() {
    const response = await apiClient.get('/auth/me')
    return response.data
  },

  // Student endpoints
  async getStudentProfile() {
    const response = await apiClient.get('/students/profile')
    return response.data
  },

  async updateStudentProfile(profileData: any) {
    const response = await apiClient.put('/students/profile', profileData)
    return response.data
  },

  async getStudentAnalytics(days: number = 30) {
    const response = await apiClient.get(`/students/analytics?days=${days}`)
    return response.data
  },

  async getLearningStyleAnalysis() {
    const response = await apiClient.get('/students/learning-style')
    return response.data
  },

  async submitLearningStyleAssessment(assessment: any) {
    const response = await apiClient.post('/students/learning-style-assessment', assessment)
    return response.data
  },

  // Learning Materials
  async getLearningMaterials(params: any = {}) {
    const response = await apiClient.get('/materials/', { params })
    return response.data
  },

  async getLearningMaterial(materialId: number) {
    const response = await apiClient.get(`/materials/${materialId}`)
    return response.data
  },

  async getMaterialSuitability(materialId: number) {
    const response = await apiClient.get(`/materials/${materialId}/suitability`)
    return response.data
  },

  async getAvailableSubjects() {
    const response = await apiClient.get('/materials/subjects/list')
    return response.data
  },

  async getAvailableTopics(subject?: string) {
    const params = subject ? { subject } : {}
    const response = await apiClient.get('/materials/topics/list', { params })
    return response.data
  },

  // Progress
  async createProgress(progressData: any) {
    const response = await apiClient.post('/progress/', progressData)
    return response.data
  },

  async updateProgress(progressId: number, progressData: any) {
    const response = await apiClient.put(`/progress/${progressId}`, progressData)
    return response.data
  },

  async getProgressRecords(params: any = {}) {
    const response = await apiClient.get('/progress/', { params })
    return response.data
  },

  async getProgressSummary() {
    const response = await apiClient.get('/progress/summary')
    return response.data
  },

  // Recommendations
  async getRecommendations(params: any = {}) {
    const response = await apiClient.get('/recommendations/', { params })
    return response.data
  },

  async generateLearningPath(subject: string, topics: string[]) {
    const params = new URLSearchParams()
    params.append('subject', subject)
    topics.forEach(topic => params.append('target_topics', topic))
    
    const response = await apiClient.get(`/recommendations/learning-path?${params}`)
    return response.data
  },

  async getSimilarMaterials(materialId: number, limit: number = 5) {
    const response = await apiClient.get(`/recommendations/similar/${materialId}?limit=${limit}`)
    return response.data
  },

  async getAdaptiveSuggestions() {
    const response = await apiClient.get('/recommendations/adaptive-suggestions')
    return response.data
  },

  async submitRecommendationFeedback(feedback: any) {
    const response = await apiClient.post('/recommendations/feedback', feedback)
    return response.data
  },
}