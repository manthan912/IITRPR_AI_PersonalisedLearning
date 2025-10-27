import React, { useState } from 'react'
import { useForm } from 'react-hook-form'
import { useAuth } from '../hooks/useAuth'
import toast from 'react-hot-toast'

interface LoginForm {
  username: string
  password: string
}

interface RegisterForm {
  username: string
  email: string
  password: string
  confirmPassword: string
  first_name: string
  last_name: string
  age?: number
}

const LoginPage: React.FC = () => {
  const [isLogin, setIsLogin] = useState(true)
  const { login, register } = useAuth()

  const loginForm = useForm<LoginForm>()
  const registerForm = useForm<RegisterForm>()

  const onLogin = async (data: LoginForm) => {
    try {
      await login(data.username, data.password)
      toast.success('Welcome back!')
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Login failed')
    }
  }

  const onRegister = async (data: RegisterForm) => {
    if (data.password !== data.confirmPassword) {
      toast.error('Passwords do not match')
      return
    }

    try {
      await register({
        username: data.username,
        email: data.email,
        password: data.password,
        first_name: data.first_name,
        last_name: data.last_name,
        age: data.age
      })
      toast.success('Registration successful! Please log in.')
      setIsLogin(true)
      registerForm.reset()
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Registration failed')
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-blue-100 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            AI Personalized Learning
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Adaptive learning platform tailored to your style
          </p>
        </div>

        <div className="bg-white shadow-xl rounded-lg p-8">
          {/* Toggle buttons */}
          <div className="flex mb-6">
            <button
              onClick={() => setIsLogin(true)}
              className={`flex-1 py-2 text-sm font-medium rounded-l-md ${
                isLogin
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              Sign In
            </button>
            <button
              onClick={() => setIsLogin(false)}
              className={`flex-1 py-2 text-sm font-medium rounded-r-md ${
                !isLogin
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              Sign Up
            </button>
          </div>

          {isLogin ? (
            /* Login Form */
            <form onSubmit={loginForm.handleSubmit(onLogin)} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Username</label>
                <input
                  {...loginForm.register('username', { required: 'Username is required' })}
                  type="text"
                  className="input-field mt-1"
                  placeholder="Enter your username"
                />
                {loginForm.formState.errors.username && (
                  <p className="text-red-500 text-xs mt-1">{loginForm.formState.errors.username.message}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">Password</label>
                <input
                  {...loginForm.register('password', { required: 'Password is required' })}
                  type="password"
                  className="input-field mt-1"
                  placeholder="Enter your password"
                />
                {loginForm.formState.errors.password && (
                  <p className="text-red-500 text-xs mt-1">{loginForm.formState.errors.password.message}</p>
                )}
              </div>

              <button
                type="submit"
                disabled={loginForm.formState.isSubmitting}
                className="w-full btn-primary"
              >
                {loginForm.formState.isSubmitting ? 'Signing in...' : 'Sign In'}
              </button>

              <div className="mt-4 p-3 bg-blue-50 rounded-md">
                <p className="text-sm text-blue-800 font-medium">Demo Accounts:</p>
                <p className="text-xs text-blue-600 mt-1">
                  Username: alice_chen, bob_garcia, or carol_smith<br />
                  Password: password123
                </p>
              </div>
            </form>
          ) : (
            /* Register Form */
            <form onSubmit={registerForm.handleSubmit(onRegister)} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">First Name</label>
                  <input
                    {...registerForm.register('first_name', { required: 'First name is required' })}
                    type="text"
                    className="input-field mt-1"
                    placeholder="First name"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Last Name</label>
                  <input
                    {...registerForm.register('last_name', { required: 'Last name is required' })}
                    type="text"
                    className="input-field mt-1"
                    placeholder="Last name"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">Username</label>
                <input
                  {...registerForm.register('username', { required: 'Username is required' })}
                  type="text"
                  className="input-field mt-1"
                  placeholder="Choose a username"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">Email</label>
                <input
                  {...registerForm.register('email', { required: 'Email is required' })}
                  type="email"
                  className="input-field mt-1"
                  placeholder="Enter your email"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">Age (optional)</label>
                <input
                  {...registerForm.register('age')}
                  type="number"
                  className="input-field mt-1"
                  placeholder="Your age"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">Password</label>
                <input
                  {...registerForm.register('password', { required: 'Password is required', minLength: 6 })}
                  type="password"
                  className="input-field mt-1"
                  placeholder="Choose a password"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">Confirm Password</label>
                <input
                  {...registerForm.register('confirmPassword', { required: 'Please confirm your password' })}
                  type="password"
                  className="input-field mt-1"
                  placeholder="Confirm your password"
                />
              </div>

              <button
                type="submit"
                disabled={registerForm.formState.isSubmitting}
                className="w-full btn-primary"
              >
                {registerForm.formState.isSubmitting ? 'Creating account...' : 'Create Account'}
              </button>
            </form>
          )}
        </div>
      </div>
    </div>
  )
}

export default LoginPage