import { useState, useEffect } from 'react'
import { api } from '../services/api'

interface User {
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
  learning_style_scores?: Record<string, number>
  dominant_learning_style?: string
  performance_score: number
  learning_streak: number
}

export function useAuth() {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('access_token')
    if (token) {
      fetchUser()
    } else {
      setLoading(false)
    }
  }, [])

  const fetchUser = async () => {
    try {
      const userData = await api.getCurrentUser()
      setUser(userData)
    } catch (error) {
      localStorage.removeItem('access_token')
    } finally {
      setLoading(false)
    }
  }

  const login = async (username: string, password: string) => {
    const response = await api.login(username, password)
    localStorage.setItem('access_token', response.access_token)
    await fetchUser()
    return response
  }

  const logout = () => {
    localStorage.removeItem('access_token')
    setUser(null)
  }

  const register = async (userData: any) => {
    return await api.register(userData)
  }

  return {
    user,
    loading,
    login,
    logout,
    register,
    refetchUser: fetchUser
  }
}