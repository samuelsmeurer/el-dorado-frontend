import React, { useState, useEffect } from 'react'
import { Users, Video, Eye, Heart, TrendingUp } from 'lucide-react'
import { analyticsAPI } from '../services/api'
import StatsCard from '../components/StatsCard'
import toast from 'react-hot-toast'

const Dashboard = () => {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    try {
      const response = await analyticsAPI.getDashboardStats()
      setStats(response.data)
    } catch (error) {
      console.error('Error loading dashboard:', error)
      toast.error('Erro ao carregar dashboard')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-2">
          Visão geral dos seus influenciadores El Dorado
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatsCard
          title="Total Influencers"
          value={stats?.total_influencers || 0}
          icon={Users}
          color="primary"
        />
        <StatsCard
          title="Total Vídeos"
          value={stats?.total_videos || 0}
          icon={Video}
          color="blue"
        />
        <StatsCard
          title="Total Views"
          value={stats?.total_views || 0}
          icon={Eye}
          color="green"
          format="number"
        />
        <StatsCard
          title="Total Likes"
          value={stats?.total_likes || 0}
          icon={Heart}
          color="red"
          format="number"
        />
      </div>

      {/* Additional Stats */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <div className="flex items-center space-x-2 mb-4">
            <TrendingUp className="h-5 w-5 text-primary-600" />
            <h3 className="text-lg font-semibold">Engagement Rate</h3>
          </div>
          <div className="text-3xl font-bold text-primary-600">
            {stats?.avg_engagement_rate ? `${stats.avg_engagement_rate.toFixed(2)}%` : '0%'}
          </div>
          <p className="text-gray-600 text-sm mt-1">
            Taxa média de engajamento
          </p>
        </div>

        <div className="card">
          <div className="flex items-center space-x-2 mb-4">
            <Video className="h-5 w-5 text-blue-600" />
            <h3 className="text-lg font-semibold">Vídeos Este Mês</h3>
          </div>
          <div className="text-3xl font-bold text-blue-600">
            {stats?.videos_this_month || 0}
          </div>
          <p className="text-gray-600 text-sm mt-1">
            Novos vídeos publicados
          </p>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="card">
        <h3 className="text-lg font-semibold mb-4">Ações Rápidas</h3>
        <div className="flex flex-wrap gap-3">
          <button className="btn-primary">
            Adicionar Influencer
          </button>
          <button className="btn-secondary">
            Sincronizar Vídeos
          </button>
          <button className="btn-secondary">
            Ver Relatório
          </button>
        </div>
      </div>
    </div>
  )
}

export default Dashboard