import React, { useState, useEffect } from 'react'
import { BarChart3, TrendingUp, Users, Video, Filter } from 'lucide-react'
import { analyticsAPI, influencerAPI, videosAPI } from '../services/api'
import AnalyticsCharts from '../components/AnalyticsCharts'
import InfluencerSearchDropdown from '../components/InfluencerSearchDropdown'
import DateRangeFilter from '../components/DateRangeFilter'
import toast from 'react-hot-toast'

const Analytics = () => {
  // Initialize with last 30 days
  const getDefaultDateRange = () => {
    const endDate = new Date()
    const startDate = new Date()
    startDate.setDate(endDate.getDate() - 30)
    
    return {
      start: startDate.toISOString().split('T')[0],
      end: endDate.toISOString().split('T')[0]
    }
  }

  const [filters, setFilters] = useState({
    selectedInfluencers: [],
    countries: [],
    dateRange: getDefaultDateRange()
  })
  const [influencers, setInfluencers] = useState([])
  const [stats, setStats] = useState(null)
  const [videos, setVideos] = useState([])
  const [loading, setLoading] = useState(true)
  const [showAllInfluencers, setShowAllInfluencers] = useState(false)
  
  const countries = [
    'Argentina', 'Bolivia', 'Brasil', 'Colombia', 'Panama', 'Peru'
  ]

  const getCountryFlag = (country) => {
    const flags = {
      'Argentina': '🇦🇷',
      'Bolivia': '🇧🇴', 
      'Brasil': '🇧🇷',
      'Colombia': '🇨🇴',
      'Panama': '🇵🇦',
      'Peru': '🇵🇪'
    }
    return flags[country] || '🌍'
  }

  const formatNumber = (num) => {
    if (num >= 1000000) {
      return (num / 1000000).toFixed(1) + 'M'
    } else if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'K'
    }
    return num.toString()
  }

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      setLoading(true)
      const [influencersRes, statsRes, videosRes] = await Promise.all([
        influencerAPI.getAll({ limit: 1000 }),
        analyticsAPI.getDashboardStats(),
        videosAPI.getAll({ limit: 10000 })
      ])
      setInfluencers(influencersRes.data)
      setStats(statsRes.data)
      setVideos(videosRes.data)
    } catch (error) {
      console.error('Error fetching analytics data:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleInfluencerSelect = (influencers) => {
    setFilters(prev => ({
      ...prev,
      selectedInfluencers: influencers
    }))
  }

  const handleClearAllFilters = () => {
    setFilters(prev => ({
      ...prev,
      selectedInfluencers: [],
      countries: []
    }))
  }

  const handleCountryAdd = (country) => {
    if (country && !filters.countries.includes(country)) {
      setFilters(prev => ({ 
        ...prev, 
        countries: [...prev.countries, country]
      }))
    }
  }

  const handleCountryRemove = (countryToRemove) => {
    setFilters(prev => ({ 
      ...prev, 
      countries: prev.countries.filter(country => country !== countryToRemove)
    }))
  }

  const handleDateRangeChange = (dateRange) => {
    setFilters(prev => ({
      ...prev,
      dateRange
    }))
  }

  const handleSearch = () => {
    // Trigger a re-fetch of data with current filters
    fetchData()
  }

  const filteredInfluencers = influencers.filter(influencer => {
    const influencerMatch = filters.selectedInfluencers.length === 0 || 
      filters.selectedInfluencers.some(selected => selected.eldorado_username === influencer.eldorado_username)
    const countryMatch = filters.countries.length === 0 || 
      (influencer.country && filters.countries.some(country => 
        country.toLowerCase() === (influencer.country || '').toLowerCase()))
    return influencerMatch && countryMatch
  })

  // Filter videos based on current filters
  const getFilteredVideos = () => {
    if (!videos || videos.length === 0) return []
    
    return videos.filter(video => {
      // Filter by selected influencers
      if (filters.selectedInfluencers.length > 0) {
        const isFromSelectedInfluencer = filters.selectedInfluencers.some(
          selected => selected.eldorado_username === video.eldorado_username
        )
        if (!isFromSelectedInfluencer) return false
      }
      
      // Filter by countries - check if video's influencer is from selected countries
      if (filters.countries.length > 0) {
        const videoInfluencer = influencers.find(inf => inf.eldorado_username === video.eldorado_username)
        if (!videoInfluencer || 
            !filters.countries.some(country => 
              (videoInfluencer.country || '').toLowerCase() === country.toLowerCase()
            )) {
          return false
        }
      }
      
      // Filter by date range
      if (filters.dateRange.start || filters.dateRange.end) {
        const videoDate = video.published_at || video.created_at
        if (videoDate) {
          const date = new Date(videoDate)
          
          if (filters.dateRange.start) {
            const startDate = new Date(filters.dateRange.start)
            if (date < startDate) return false
          }
          
          if (filters.dateRange.end) {
            const endDate = new Date(filters.dateRange.end)
            endDate.setHours(23, 59, 59, 999)
            if (date > endDate) return false
          }
        } else if (filters.dateRange.start || filters.dateRange.end) {
          // If date range is set but video has no date, exclude it
          return false
        }
      }
      
      return true
    })
  }

  // Calculate filtered stats
  const getFilteredStats = () => {
    const filteredVideos = getFilteredVideos()
    
    // Calculate real statistics from filtered videos
    const totalVideos = filteredVideos.length
    const totalViews = filteredVideos.reduce((sum, video) => sum + (video.view_count || 0), 0)
    const totalLikes = filteredVideos.reduce((sum, video) => sum + (video.like_count || 0), 0)
    const totalComments = filteredVideos.reduce((sum, video) => sum + (video.comment_count || 0), 0)
    const totalShares = filteredVideos.reduce((sum, video) => sum + (video.share_count || 0), 0)
    
    // Calculate engagement rate
    const totalEngagement = totalLikes + totalComments + totalShares
    const avgEngagementRate = totalViews > 0 ? (totalEngagement / totalViews) * 100 : 0
    
    return {
      total_influencers: filteredInfluencers.length,
      total_videos: totalVideos,
      total_views: totalViews,
      total_likes: totalLikes,
      avg_engagement_rate: avgEngagementRate,
      videos_this_month: filteredVideos.filter(video => {
        const videoDate = new Date(video.published_at || video.created_at)
        const currentMonth = new Date().getMonth()
        const currentYear = new Date().getFullYear()
        return videoDate.getMonth() === currentMonth && videoDate.getFullYear() === currentYear
      }).length
    }
  }
  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Analytics</h1>
        <p className="text-gray-600 mt-2">
          Análises detalhadas dos seus influenciadores
        </p>
      </div>

      {/* Filters */}
      <div className="card">
        <div className="flex items-center space-x-2 mb-4">
          <Filter className="h-5 w-5 text-gray-500" />
          <h3 className="text-lg font-medium">Filtros</h3>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Influencer Search with Dropdown */}
          <div>
            <label className="flex items-center space-x-2 text-sm font-medium text-gray-700 mb-2">
              <Users className="h-4 w-4" />
              <span>Influencer</span>
            </label>
            <InfluencerSearchDropdown
              influencers={influencers}
              selectedInfluencers={filters.selectedInfluencers}
              onSelect={handleInfluencerSelect}
              onClearAll={handleClearAllFilters}
            />
          </div>

          {/* Country Filter */}
          <div>
            <label className="flex items-center space-x-2 text-sm font-medium text-gray-700 mb-2">
              <Users className="h-4 w-4" />
              <span>País</span>
            </label>
            <select
              value=""
              onChange={(e) => handleCountryAdd(e.target.value)}
              className="input-field"
            >
              <option value="">Selecionar país...</option>
              {countries
                .filter(country => !filters.countries.includes(country))
                .map(country => (
                <option key={country} value={country}>
                  {country}
                </option>
              ))}
            </select>
            {filters.countries.length > 0 && (
              <div className="mt-3 flex flex-wrap gap-2">
                {filters.countries.map(country => (
                  <div 
                    key={country}
                    className="inline-flex items-center px-3 py-1 bg-red-100 border border-red-200 rounded-md text-sm font-medium text-red-700"
                  >
                    <span className="mr-2">{getCountryFlag(country)}</span>
                    {country}
                    <button
                      onClick={() => handleCountryRemove(country)}
                      className="ml-2 hover:bg-red-200 rounded-full p-1 transition-colors"
                      aria-label={`Remover ${country}`}
                    >
                      <svg className="w-3 h-3" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
                      </svg>
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Date Range Filter with Presets */}
          <div>
            <DateRangeFilter
              dateRange={filters.dateRange}
              onDateRangeChange={handleDateRangeChange}
              onSearch={handleSearch}
            />
          </div>
        </div>
      </div>

      {/* Stats Overview - Filtered */}
      {(() => {
        const filteredStats = getFilteredStats()
        return filteredStats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="card">
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-blue-100 rounded-lg">
                  <Users className="h-6 w-6 text-blue-600" />
                </div>
                <div>
                  <p className="text-sm text-gray-600">Influencers {filters.selectedInfluencers.length > 0 || filters.countries.length > 0 ? '(Filtrado)' : ''}</p>
                  <p className="text-2xl font-bold">{filteredStats.total_influencers || 0}</p>
                </div>
              </div>
            </div>
            
            <div className="card">
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-green-100 rounded-lg">
                  <Video className="h-6 w-6 text-green-600" />
                </div>
                <div>
                  <p className="text-sm text-gray-600">Total Vídeos</p>
                  <p className="text-2xl font-bold">{filteredStats.total_videos || 0}</p>
                </div>
              </div>
            </div>
            
            <div className="card">
              <div className="flex items-center space-x-3">
                <div className="p-3 bg-blue-100 rounded-lg">
                  <div className="flex items-center justify-center">
                    <svg className="h-6 w-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                  </div>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Total Views (Filtrado)</p>
                  <p className="text-2xl font-bold text-blue-600">{formatNumber(filteredStats.total_views || 0)}</p>
                </div>
              </div>
            </div>
            
            <div className="card">
              <div className="flex items-center space-x-3">
                <div className="p-3 bg-red-100 rounded-lg">
                  <div className="flex items-center justify-center">
                    <svg className="h-6 w-6 text-red-600" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
                    </svg>
                  </div>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Total Likes (Filtrado)</p>
                  <p className="text-2xl font-bold text-red-600">{formatNumber(filteredStats.total_likes || 0)}</p>
                </div>
              </div>
            </div>
          </div>
        )
      })()}

      {/* Filtered Results */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-medium">
            {showAllInfluencers 
              ? `Influencers (${filteredInfluencers.length})` 
              : `Top 10 Influencers (${Math.min(filteredInfluencers.length, 10)} de ${filteredInfluencers.length})`
            }
          </h3>
          {(filters.selectedInfluencers.length > 0 || filters.countries.length > 0 || filters.dateRange.start || filters.dateRange.end) ? (
            <button
              onClick={() => setFilters({ selectedInfluencers: [], countries: [], dateRange: getDefaultDateRange() })}
              className="text-sm text-blue-600 hover:text-blue-800"
            >
              Limpar filtros
            </button>
          ) : null}
        </div>

        {loading ? (
          <div className="text-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-2 border-primary-600 border-t-transparent mx-auto mb-2" />
            <p className="text-gray-600">Carregando dados...</p>
          </div>
        ) : filteredInfluencers.length === 0 ? (
          <div className="text-center py-8">
            <Users className="h-12 w-12 text-gray-400 mx-auto mb-2" />
            <p className="text-gray-600">
              {(filters.selectedInfluencers.length > 0 || filters.countries.length > 0)
                ? 'Nenhum influencer encontrado com os filtros aplicados'
                : 'Nenhum influencer cadastrado'
              }
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {filteredInfluencers
              .map((influencer) => {
                const influencerVideos = getFilteredVideos().filter(
                  video => video.eldorado_username === influencer.eldorado_username
                )
                const totalViews = influencerVideos.reduce((sum, video) => sum + (video.view_count || 0), 0)
                const totalLikes = influencerVideos.reduce((sum, video) => sum + (video.like_count || 0), 0)
                
                return {
                  ...influencer,
                  influencerVideos,
                  totalViews,
                  totalLikes
                }
              })
              .sort((a, b) => b.totalViews - a.totalViews) // Sort by total views descending
              .slice(0, showAllInfluencers ? undefined : 10) // Show only top 10 initially
              .map((influencer, index) => (
                <div key={influencer.eldorado_username} className="flex items-center justify-between p-4 bg-white border border-gray-200 rounded-lg hover:shadow-md transition-shadow">
                  <div className="flex items-center space-x-3">
                    <div className="relative">
                      {index < 3 && (
                        <div className="absolute -top-1 -left-1 w-5 h-5 bg-yellow-500 text-white text-xs rounded-full flex items-center justify-center font-bold">
                          {index + 1}
                        </div>
                      )}
                      <div className="w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center">
                        <span className="text-primary-600 font-medium">
                          {influencer.first_name.charAt(0).toUpperCase()}
                        </span>
                      </div>
                    </div>
                    <div>
                      <h4 className="font-medium text-gray-900">{influencer.first_name}</h4>
                      <p className="text-sm text-gray-500">@{influencer.eldorado_username}</p>
                      {index < 3 && (
                        <span className="text-xs text-yellow-600 font-medium">Top {index + 1}</span>
                      )}
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-6 text-sm">
                    <div className="text-center">
                      <p className="font-semibold text-gray-900">{influencer.influencerVideos.length}</p>
                      <p className="text-gray-500">Vídeos</p>
                    </div>
                    <div className="text-center">
                      <p className={`font-semibold ${index === 0 ? 'text-green-600 text-lg' : 'text-blue-600'}`}>
                        {influencer.totalViews.toLocaleString()}
                      </p>
                      <p className="text-gray-500">Views</p>
                    </div>
                    <div className="text-center">
                      <p className="font-semibold text-red-600">{influencer.totalLikes.toLocaleString()}</p>
                      <p className="text-gray-500">Likes</p>
                    </div>
                    {influencer.country && (
                      <div className="text-center">
                        <p className="text-xs text-gray-500">{influencer.country}</p>
                        <p className="text-xs text-gray-400">País</p>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            
            {/* Show more button */}
            {filteredInfluencers.length > 10 && !showAllInfluencers && (
              <div className="text-center pt-4">
                <button
                  onClick={() => setShowAllInfluencers(true)}
                  className="btn-secondary"
                >
                  Ver mais ({filteredInfluencers.length - 10} restantes)
                </button>
              </div>
            )}
            
            {/* Show less button */}
            {showAllInfluencers && filteredInfluencers.length > 10 && (
              <div className="text-center pt-4">
                <button
                  onClick={() => setShowAllInfluencers(false)}
                  className="btn-secondary"
                >
                  Ver menos (mostrar apenas top 10)
                </button>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Charts and Visualizations */}
      {!loading && (
        <div>
          <h3 className="text-xl font-semibold mb-4">Análises Visuais</h3>
          <AnalyticsCharts 
            influencers={influencers} 
            filters={filters}
          />
        </div>
      )}
    </div>
  )
}

export default Analytics