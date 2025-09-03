import React, { useState, useEffect } from 'react'
import { Users, Video, Eye, Heart, TrendingUp, Hash, Plus, ExternalLink, Crown, Calendar, Zap, Award, Target, ArrowUpRight, ArrowDownRight, Clock } from 'lucide-react'
import { analyticsAPI, influencerAPI, videosAPI } from '../services/api'
import StatsCard from '../components/StatsCard'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'

const Dashboard = () => {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [syncLoading, setSyncLoading] = useState(false)
  const [influencers, setInfluencers] = useState([])
  const [videos, setVideos] = useState([])
  const [lastSync, setLastSync] = useState(null)
  const navigate = useNavigate()

  // Get current month name in Portuguese
  const getCurrentMonthName = () => {
    const months = [
      'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
      'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
    ]
    return months[new Date().getMonth()]
  }

  useEffect(() => {
    loadDashboardData()
    // Load last sync time from localStorage
    const stored = localStorage.getItem('lastVideoSync')
    if (stored) {
      setLastSync(new Date(stored))
    }
  }, [])

  const loadDashboardData = async () => {
    try {
      const [statsRes, influencersRes, videosRes] = await Promise.all([
        analyticsAPI.getDashboardStats(),
        influencerAPI.getAll({ limit: 1000 }),
        videosAPI.getAll({ limit: 10000 })
      ])
      setStats(statsRes.data)
      setInfluencers(influencersRes.data)
      setVideos(videosRes.data)
    } catch (error) {
      console.error('Error loading dashboard:', error)
      toast.error('Erro ao carregar dashboard')
    } finally {
      setLoading(false)
    }
  }

  // Get top 5 influencers by total views
  const getTopInfluencers = () => {
    return influencers
      .map(influencer => {
        const influencerVideos = videos.filter(
          video => video.eldorado_username === influencer.eldorado_username
        )
        const totalViews = influencerVideos.reduce((sum, video) => sum + (video.view_count || 0), 0)
        const totalLikes = influencerVideos.reduce((sum, video) => sum + (video.like_count || 0), 0)
        const totalVideos = influencerVideos.length
        
        return {
          ...influencer,
          totalViews,
          totalLikes,
          totalVideos
        }
      })
      .sort((a, b) => b.totalViews - a.totalViews)
      .slice(0, 5)
  }

  const formatNumber = (num) => {
    if (num >= 1000000) {
      return (num / 1000000).toFixed(1) + 'M'
    } else if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'K'
    }
    return num.toString()
  }

  // Get trending videos (published in last 7 days with high engagement)
  const getTrendingVideos = () => {
    const sevenDaysAgo = new Date()
    sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7)
    
    return videos
      .filter(video => {
        const publishDate = new Date(video.published_at || video.created_at)
        return publishDate >= sevenDaysAgo
      })
      .map(video => ({
        ...video,
        engagementRate: video.view_count > 0 ? ((video.like_count + video.comment_count + video.share_count) / video.view_count) * 100 : 0
      }))
      .sort((a, b) => b.engagementRate - a.engagementRate)
      .slice(0, 3)
  }

  // Get country performance
  const getCountryStats = () => {
    const countryStats = {}
    
    influencers.forEach(influencer => {
      const country = influencer.country || 'Não informado'
      if (!countryStats[country]) {
        countryStats[country] = { 
          count: 0, 
          totalViews: 0, 
          totalVideos: 0,
          influencers: []
        }
      }
      
      const influencerVideos = videos.filter(v => v.eldorado_username === influencer.eldorado_username)
      const totalViews = influencerVideos.reduce((sum, v) => sum + (v.view_count || 0), 0)
      
      countryStats[country].count++
      countryStats[country].totalViews += totalViews
      countryStats[country].totalVideos += influencerVideos.length
      countryStats[country].influencers.push(influencer.first_name)
    })

    return Object.entries(countryStats)
      .map(([country, stats]) => ({ country, ...stats }))
      .sort((a, b) => b.totalViews - a.totalViews)
      .slice(0, 3)
  }

  // Get monthly growth
  const getMonthlyGrowth = () => {
    const currentMonth = new Date().getMonth()
    const lastMonth = currentMonth === 0 ? 11 : currentMonth - 1
    
    const currentMonthVideos = videos.filter(video => {
      const videoDate = new Date(video.published_at || video.created_at)
      return videoDate.getMonth() === currentMonth
    })
    
    const lastMonthVideos = videos.filter(video => {
      const videoDate = new Date(video.published_at || video.created_at)
      return videoDate.getMonth() === lastMonth
    })

    const currentViews = currentMonthVideos.reduce((sum, v) => sum + (v.view_count || 0), 0)
    const lastViews = lastMonthVideos.reduce((sum, v) => sum + (v.view_count || 0), 0)
    
    const growth = lastViews > 0 ? ((currentViews - lastViews) / lastViews) * 100 : 0

    return {
      videosGrowth: ((currentMonthVideos.length - lastMonthVideos.length) / (lastMonthVideos.length || 1)) * 100,
      viewsGrowth: growth,
      currentVideos: currentMonthVideos.length,
      lastVideos: lastMonthVideos.length
    }
  }

  // Get best performing hashtag content
  const getHashtagInsights = () => {
    const hashtagVideos = videos.filter(video => 
      video.description && video.description.toLowerCase().includes('@el dorado p2p')
    )
    
    const totalHashtagViews = hashtagVideos.reduce((sum, v) => sum + (v.view_count || 0), 0)
    const totalViews = videos.reduce((sum, v) => sum + (v.view_count || 0), 0)
    
    const conversionRate = totalViews > 0 ? (totalHashtagViews / totalViews) * 100 : 0

    return {
      hashtagVideos: hashtagVideos.length,
      totalVideos: videos.length,
      conversionRate,
      avgViewsWithHashtag: hashtagVideos.length > 0 ? totalHashtagViews / hashtagVideos.length : 0,
      avgViewsWithout: (videos.length - hashtagVideos.length) > 0 ? 
        (totalViews - totalHashtagViews) / (videos.length - hashtagVideos.length) : 0
    }
  }

  const handleSyncVideos = async () => {
    if (syncLoading) return
    
    setSyncLoading(true)
    const syncStartTime = new Date()
    
    try {
      toast.loading('Sincronizando vídeos de todos os influenciadores...', { id: 'sync' })
      
      const response = await videosAPI.syncAllVideos()
      
      // Store sync time
      localStorage.setItem('lastVideoSync', syncStartTime.toISOString())
      setLastSync(syncStartTime)
      
      // Reload dashboard data
      await loadDashboardData()
      
      // Show success message with details
      const results = response.data
      const totalProcessed = results.reduce((sum, r) => sum + r.videos_processed, 0)
      const totalNew = results.reduce((sum, r) => sum + r.new_videos, 0)
      const totalUpdated = results.reduce((sum, r) => sum + r.updated_videos, 0)
      
      toast.success(
        `Sincronização concluída! ${totalProcessed} vídeos processados, ${totalNew} novos, ${totalUpdated} atualizados.`,
        { id: 'sync', duration: 5000 }
      )
    } catch (error) {
      console.error('Erro na sincronização:', error)
      toast.error('Erro ao sincronizar vídeos. Tente novamente.', { id: 'sync' })
    } finally {
      setSyncLoading(false)
    }
  }

  const formatLastSyncTime = () => {
    if (!lastSync) return 'Nunca sincronizado'
    
    const now = new Date()
    const diffMs = now - lastSync
    const diffMinutes = Math.floor(diffMs / (1000 * 60))
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))
    
    if (diffMinutes < 1) return 'Há poucos segundos'
    if (diffMinutes < 60) return `Há ${diffMinutes} minutos`
    if (diffHours < 24) return `Há ${diffHours} horas`
    if (diffDays === 1) return 'Há 1 dia'
    if (diffDays < 7) return `Há ${diffDays} dias`
    
    return lastSync.toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
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
        <h1 className="text-3xl font-bold text-gray-900">Dashboard do mês de {getCurrentMonthName()}</h1>
        <p className="text-gray-600 mt-2">
          Visão geral dos seus influenciadores El Dorado
        </p>
      </div>

      {/* Hashtags Section */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <Hash className="h-5 w-5 text-gray-600" />
            <h3 className="text-lg font-semibold text-gray-900">Hashtags Trackeadas</h3>
          </div>
          <button
            onClick={() => navigate('/hashtags')}
            className="btn-primary flex items-center space-x-2"
          >
            <Plus className="h-4 w-4" />
            <span>Adicionar Hashtag</span>
          </button>
        </div>
        
        {/* Empty state for now */}
        <div className="text-center py-8 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
          <Hash className="h-12 w-12 text-gray-400 mx-auto mb-3" />
          <p className="text-gray-600 text-lg font-medium">Nenhuma hashtag configurada</p>
          <p className="text-gray-500 text-sm mt-1">
            Adicione hashtags para começar a trackear o desempenho dos seus influenciadores
          </p>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
        <StatsCard
          title="Total Influencers"
          value={stats?.total_influencers || 0}
          icon={Users}
          color="primary"
        />
        <StatsCard
          title={`Influencers que postaram em ${getCurrentMonthName()}`}
          value={stats?.active_influencers_this_month || 0}
          icon={Users}
          color="purple"
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
            <h3 className="text-lg font-semibold">Vídeos em {getCurrentMonthName()}</h3>
          </div>
          <div className="text-3xl font-bold text-blue-600">
            {stats?.videos_this_month || 0}
          </div>
          <p className="text-gray-600 text-sm mt-1">
            Novos vídeos publicados
          </p>
        </div>
      </div>

      {/* Top 5 Influencers */}
      <div className="card">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-2">
            <Users className="h-5 w-5 text-gray-600" />
            <h3 className="text-lg font-semibold text-gray-900">Top 5 Influencers</h3>
          </div>
          <button
            onClick={() => navigate('/influencers')}
            className="btn-secondary flex items-center space-x-2"
          >
            <ExternalLink className="h-4 w-4" />
            <span>Ver todos os influencers</span>
          </button>
        </div>

        {getTopInfluencers().length > 0 ? (
          <div className="space-y-4">
            {getTopInfluencers().map((influencer, index) => (
              <div key={influencer.eldorado_username} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                <div className="flex items-center space-x-4">
                  <div className="relative">
                    {index === 0 && (
                      <div className="absolute -top-1 -left-1 w-6 h-6 bg-yellow-500 rounded-full flex items-center justify-center">
                        <Crown className="h-3 w-3 text-white" />
                      </div>
                    )}
                    {index < 3 && index > 0 && (
                      <div className="absolute -top-1 -left-1 w-5 h-5 bg-gray-500 text-white text-xs rounded-full flex items-center justify-center font-bold">
                        {index + 1}
                      </div>
                    )}
                    <div className="w-12 h-12 bg-primary-100 rounded-full flex items-center justify-center">
                      <span className="text-primary-600 font-medium text-lg">
                        {influencer.first_name.charAt(0).toUpperCase()}
                      </span>
                    </div>
                  </div>
                  <div>
                    <h4 className="font-semibold text-gray-900 text-lg">
                      {influencer.first_name}
                    </h4>
                    <p className="text-gray-500 text-sm">@{influencer.eldorado_username}</p>
                    {index === 0 && (
                      <span className="text-xs text-yellow-600 font-medium bg-yellow-100 px-2 py-1 rounded-full">
                        🏆 Top Performer
                      </span>
                    )}
                  </div>
                </div>
                
                <div className="flex items-center space-x-8">
                  <div className="text-center">
                    <p className="text-sm text-gray-500">Vídeos</p>
                    <p className="font-semibold text-gray-900">{influencer.totalVideos}</p>
                  </div>
                  <div className="text-center">
                    <p className="text-sm text-gray-500">Views</p>
                    <p className={`font-bold ${index === 0 ? 'text-green-600 text-lg' : 'text-blue-600'}`}>
                      {formatNumber(influencer.totalViews)}
                    </p>
                  </div>
                  <div className="text-center">
                    <p className="text-sm text-gray-500">Likes</p>
                    <p className="font-semibold text-red-600">{formatNumber(influencer.totalLikes)}</p>
                  </div>
                  {influencer.country && (
                    <div className="text-center">
                      <p className="text-sm text-gray-500">País</p>
                      <p className="text-xs text-gray-600">{influencer.country}</p>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8">
            <Users className="h-12 w-12 text-gray-400 mx-auto mb-3" />
            <p className="text-gray-600">Nenhum influencer encontrado</p>
            <p className="text-gray-500 text-sm mt-1">
              Adicione influencers para ver o ranking aqui
            </p>
          </div>
        )}
      </div>

      {/* Quick Actions */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold">Ações Rápidas</h3>
          <div className="text-sm text-gray-500 flex items-center space-x-1">
            <Clock className="h-4 w-4" />
            <span>Última sync: {formatLastSyncTime()}</span>
          </div>
        </div>
        <div className="flex flex-wrap gap-3">
          <button 
            onClick={() => navigate('/influencers')}
            className="btn-primary"
          >
            Adicionar Influencer
          </button>
          <button 
            onClick={handleSyncVideos}
            disabled={syncLoading}
            className={`btn-secondary flex items-center space-x-2 ${
              syncLoading ? 'opacity-50 cursor-not-allowed' : ''
            }`}
          >
            {syncLoading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-current"></div>
                <span>Sincronizando...</span>
              </>
            ) : (
              <>
                <Zap className="h-4 w-4" />
                <span>Sincronizar Vídeos</span>
              </>
            )}
          </button>
          <button 
            onClick={() => navigate('/analytics')}
            className="btn-secondary"
          >
            Ver Relatório
          </button>
        </div>
      </div>

      {/* Insights Grid - The surprise sections! */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Monthly Growth Analysis */}
        <div className="card">
          <div className="flex items-center space-x-2 mb-4">
            <TrendingUp className="h-5 w-5 text-green-600" />
            <h3 className="text-lg font-semibold">Crescimento Mensal</h3>
          </div>
          
          {(() => {
            const growth = getMonthlyGrowth()
            return (
              <div className="space-y-4">
                <div className="flex items-center justify-between p-3 bg-gradient-to-r from-green-50 to-blue-50 rounded-lg">
                  <div>
                    <p className="text-sm text-gray-600">Vídeos este mês</p>
                    <p className="text-xl font-bold">{growth.currentVideos}</p>
                  </div>
                  <div className="flex items-center space-x-1">
                    {growth.videosGrowth >= 0 ? (
                      <ArrowUpRight className="h-4 w-4 text-green-600" />
                    ) : (
                      <ArrowDownRight className="h-4 w-4 text-red-600" />
                    )}
                    <span className={`text-sm font-medium ${growth.videosGrowth >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {Math.abs(growth.videosGrowth).toFixed(1)}%
                    </span>
                  </div>
                </div>
                
                <div className="flex items-center justify-between p-3 bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg">
                  <div>
                    <p className="text-sm text-gray-600">Crescimento de views</p>
                    <p className="text-sm text-gray-500">vs mês anterior</p>
                  </div>
                  <div className="flex items-center space-x-1">
                    {growth.viewsGrowth >= 0 ? (
                      <ArrowUpRight className="h-4 w-4 text-green-600" />
                    ) : (
                      <ArrowDownRight className="h-4 w-4 text-red-600" />
                    )}
                    <span className={`text-lg font-bold ${growth.viewsGrowth >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {Math.abs(growth.viewsGrowth).toFixed(1)}%
                    </span>
                  </div>
                </div>
              </div>
            )
          })()}
        </div>

        {/* Country Performance */}
        <div className="card">
          <div className="flex items-center space-x-2 mb-4">
            <Target className="h-5 w-5 text-blue-600" />
            <h3 className="text-lg font-semibold">Top Países por Performance</h3>
          </div>
          
          <div className="space-y-3">
            {getCountryStats().map((countryData, index) => {
              const flag = {
                'brasil': '🇧🇷',
                'bolivia': '🇧🇴', 
                'peru': '🇵🇪',
                'colombia': '🇨🇴',
                'argentina': '🇦🇷'
              }[countryData.country.toLowerCase()] || '🌍'
              
              return (
                <div key={countryData.country} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <span className="text-2xl">{flag}</span>
                    <div>
                      <p className="font-medium">{countryData.country}</p>
                      <p className="text-sm text-gray-500">{countryData.count} influencers</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="font-bold text-blue-600">{formatNumber(countryData.totalViews)}</p>
                    <p className="text-xs text-gray-500">{countryData.totalVideos} vídeos</p>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      </div>

      {/* Hashtag Performance Insights */}
      <div className="card">
        <div className="flex items-center space-x-2 mb-4">
          <Zap className="h-5 w-5 text-yellow-600" />
          <h3 className="text-lg font-semibold">Análise de Hashtag "@El Dorado P2P"</h3>
        </div>
        
        {(() => {
          const hashtagData = getHashtagInsights()
          const performanceDiff = hashtagData.avgViewsWithHashtag - hashtagData.avgViewsWithout
          
          return (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-4 bg-gradient-to-br from-yellow-50 to-orange-50 rounded-lg border border-yellow-200">
                <div className="flex items-center space-x-2 mb-2">
                  <Hash className="h-4 w-4 text-yellow-600" />
                  <span className="text-sm font-medium text-yellow-800">Taxa de Uso</span>
                </div>
                <p className="text-2xl font-bold text-yellow-900">
                  {((hashtagData.hashtagVideos / hashtagData.totalVideos) * 100).toFixed(1)}%
                </p>
                <p className="text-xs text-yellow-700">
                  {hashtagData.hashtagVideos} de {hashtagData.totalVideos} vídeos
                </p>
              </div>
              
              <div className="p-4 bg-gradient-to-br from-green-50 to-emerald-50 rounded-lg border border-green-200">
                <div className="flex items-center space-x-2 mb-2">
                  <Eye className="h-4 w-4 text-green-600" />
                  <span className="text-sm font-medium text-green-800">Média com Hashtag</span>
                </div>
                <p className="text-2xl font-bold text-green-900">
                  {formatNumber(hashtagData.avgViewsWithHashtag)}
                </p>
                <p className="text-xs text-green-700">views por vídeo</p>
              </div>
              
              <div className={`p-4 bg-gradient-to-br rounded-lg border ${
                performanceDiff >= 0 
                  ? 'from-blue-50 to-cyan-50 border-blue-200' 
                  : 'from-red-50 to-pink-50 border-red-200'
              }`}>
                <div className="flex items-center space-x-2 mb-2">
                  {performanceDiff >= 0 ? (
                    <ArrowUpRight className="h-4 w-4 text-blue-600" />
                  ) : (
                    <ArrowDownRight className="h-4 w-4 text-red-600" />
                  )}
                  <span className={`text-sm font-medium ${performanceDiff >= 0 ? 'text-blue-800' : 'text-red-800'}`}>
                    Diferença de Performance
                  </span>
                </div>
                <p className={`text-2xl font-bold ${performanceDiff >= 0 ? 'text-blue-900' : 'text-red-900'}`}>
                  {performanceDiff >= 0 ? '+' : ''}{formatNumber(performanceDiff)}
                </p>
                <p className={`text-xs ${performanceDiff >= 0 ? 'text-blue-700' : 'text-red-700'}`}>
                  vs sem hashtag
                </p>
              </div>
            </div>
          )
        })()}
      </div>

      {/* Trending Content */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <Award className="h-5 w-5 text-purple-600" />
            <h3 className="text-lg font-semibold">🔥 Conteúdo em Alta (Últimos 7 dias)</h3>
          </div>
          <span className="text-xs text-gray-500 flex items-center space-x-1">
            <Clock className="h-3 w-3" />
            <span>Por taxa de engajamento</span>
          </span>
        </div>
        
        <div className="space-y-3">
          {getTrendingVideos().length > 0 ? (
            getTrendingVideos().map((video, index) => (
              <div key={video.id} className="flex items-center justify-between p-4 bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg border border-purple-100">
                <div className="flex items-center space-x-3">
                  <div className="flex items-center justify-center w-8 h-8 bg-purple-100 rounded-full">
                    <span className="text-purple-600 font-bold text-sm">#{index + 1}</span>
                  </div>
                  <div>
                    <p className="font-medium text-gray-900 truncate max-w-xs">
                      {video.description ? video.description.substring(0, 50) + '...' : 'Sem descrição'}
                    </p>
                    <p className="text-sm text-gray-500">@{video.eldorado_username}</p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-6 text-sm">
                  <div className="text-center">
                    <p className="font-bold text-purple-600">{video.engagementRate.toFixed(1)}%</p>
                    <p className="text-xs text-gray-500">engajamento</p>
                  </div>
                  <div className="text-center">
                    <p className="font-semibold text-blue-600">{formatNumber(video.view_count || 0)}</p>
                    <p className="text-xs text-gray-500">views</p>
                  </div>
                  <div className="text-center">
                    <p className="font-semibold text-red-600">{formatNumber(video.like_count || 0)}</p>
                    <p className="text-xs text-gray-500">likes</p>
                  </div>
                </div>
              </div>
            ))
          ) : (
            <div className="text-center py-8">
              <Calendar className="h-12 w-12 text-gray-400 mx-auto mb-3" />
              <p className="text-gray-600">Nenhum vídeo publicado nos últimos 7 dias</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default Dashboard