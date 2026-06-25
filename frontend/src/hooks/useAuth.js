import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { authAPI } from '../services/api'
import { useNavigate, useLocation } from 'react-router-dom'

export function useAuth() {
  const queryClient = useQueryClient()
  const navigate = useNavigate()
  const location = useLocation()

  const { data: user, isLoading } = useQuery({
    queryKey: ['currentUser'],
    queryFn: () => authAPI.getMe().then(res => res.data),
    retry: false,
    enabled: location.pathname !== '/login', // Don't check auth on login page
  })

  const loginMutation = useMutation({
    mutationFn: ({ username, password }) => authAPI.login(username, password),
    onSuccess: (data) => {
      localStorage.setItem('token', data.data.access_token)
      queryClient.invalidateQueries(['currentUser'])
      navigate('/dashboard')
    },
  })

  const registerMutation = useMutation({
    mutationFn: (userData) => authAPI.register(userData),
    onSuccess: () => {
      navigate('/login')
    },
    onError: (error) => {
      console.error('Registration error:', error)
    },
  })

  const logout = () => {
    localStorage.removeItem('token')
    queryClient.clear()
    navigate('/login')
  }

  return {
    user,
    isLoading,
    login: loginMutation.mutate,
    register: registerMutation.mutate,
    logout,
    isAuthenticated: !!user,
  }
}
