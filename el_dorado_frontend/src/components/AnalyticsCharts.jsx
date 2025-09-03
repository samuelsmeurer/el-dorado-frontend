import React, { useState, useEffect } from 'react'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  PointElement,
  LineElement,
} from 'chart.js'
import { Bar, Doughnut, Line } from 'react-chartjs-2'
import { videosAPI, analyticsAPI } from '../services/api'
import { Eye, Heart, TrendingUp, ExternalLink, BarChart3 } from 'lucide-react'

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  PointElement,
  LineElement,
)

const AnalyticsCharts = ({ influencers, filters }) => {
  const [videos, setVideos] = useState([])
  const [topVideos, setTopVideos] = useState([])
  const [dashboardStats, setDashboardStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [viewsChartMode, setViewsChartMode] = useState('country') // 'country' or 'influencer'

  useEffect(() => {
    fetchRealData()
  }, [influencers])

  // Filter videos based on applied filters
  const getFilteredVideos = () => {
    if (!videos) return []
    
    console.log('Filtering videos with filters:', filters)
    console.log('Total videos before filtering:', videos.length)
    
    const filteredResults = videos.filter(video => {
      // Filter by selected influencers
      if (filters?.selectedInfluencers && filters.selectedInfluencers.length > 0) {
        const isFromSelectedInfluencer = filters.selectedInfluencers.some(
          selected => selected.eldorado_username === video.eldorado_username
        )
        if (!isFromSelectedInfluencer) {
          return false
        }
      }

      // Filter by countries - always apply if countries filter is set
      if (filters?.countries && filters.countries.length > 0) {
        // Find the influencer for this video and check their country
        const videoInfluencer = influencers.find(inf => inf.eldorado_username === video.eldorado_username)
        if (!videoInfluencer || 
            !filters.countries.some(country => 
              (videoInfluencer.country || '').toLowerCase() === country.toLowerCase()
            )) {
          return false
        }
      }
      
      // Filter by date range
      if (filters?.dateRange?.start || filters?.dateRange?.end) {
        const videoDate = video.published_at || video.created_at
        if (videoDate) {
          const date = new Date(videoDate)
          
          if (filters.dateRange.start) {
            const startDate = new Date(filters.dateRange.start)
            if (date < startDate) return false
          }
          
          if (filters.dateRange.end) {
            const endDate = new Date(filters.dateRange.end)
            endDate.setHours(23, 59, 59, 999) // Include the entire end day
            if (date > endDate) return false
          }
        }
      }
      
      return true
    })
    
    console.log('Filtered videos result:', filteredResults.length)
    return filteredResults
  }

  const filteredVideos = getFilteredVideos()

  // Get filtered influencers based on applied filters
  const getFilteredInfluencers = () => {
    if (!influencers) return []
    
    return influencers.filter(influencer => {
      // Filter by selected influencers
      if (filters?.selectedInfluencers && filters.selectedInfluencers.length > 0) {
        const isSelected = filters.selectedInfluencers.some(
          selected => selected.eldorado_username === influencer.eldorado_username
        )
        if (!isSelected) return false
      }
      
      // Filter by countries
      if (filters?.countries && filters.countries.length > 0) {
        if (!filters.countries.some(country => 
            (influencer.country || '').toLowerCase() === country.toLowerCase()
        )) return false
      }
      
      // Filter by date range - include only influencers who have videos in the date range
      if (filters?.dateRange?.start || filters?.dateRange?.end) {
        const influencerHasVideosInRange = filteredVideos.some(
          video => video.eldorado_username === influencer.eldorado_username
        )
        if (!influencerHasVideosInRange) return false
      }
      
      return true
    })
  }

  const filteredInfluencers = getFilteredInfluencers()

  // Calculate filtered stats
  const getFilteredStats = () => {
    const totalViews = filteredVideos.reduce((sum, video) => sum + (video.view_count || video.views || 0), 0)
    const totalLikes = filteredVideos.reduce((sum, video) => sum + (video.like_count || video.likes || 0), 0)
    const topVideo = filteredVideos.sort((a, b) => (b.view_count || b.views || 0) - (a.view_count || a.views || 0))[0]
    
    return {
      totalViews,
      totalLikes,
      topVideo,
      totalVideos: filteredVideos.length
    }
  }

  const fetchRealData = async () => {
    try {
      setLoading(true)
      const [videosRes, topVideosRes, dashboardRes] = await Promise.all([
        videosAPI.getAll(),
        analyticsAPI.getTopVideos('views', 1),
        analyticsAPI.getDashboardStats()
      ])
      
      const allVideos = videosRes.data
      const topVideosList = topVideosRes.data
      const stats = dashboardRes.data
      
      console.log('All videos data:', allVideos)
      console.log('Top videos data:', topVideosList)
      console.log('Dashboard stats:', stats)
      
      setVideos(allVideos)
      setTopVideos(topVideosList)
      setDashboardStats(stats)
    } catch (error) {
      console.error('Error fetching analytics data:', error)
    } finally {
      setLoading(false)
    }
  }

  const formatNumber = (num) => {
    if (num >= 1000000) {
      return (num / 1000000).toFixed(1) + 'M'
    } else if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'K'
    }
    return num.toString()
  }

  const generateMonthlyData = () => {
    const months = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun']
    const monthlyViews = new Array(6).fill(0)
    const monthlyLikes = new Array(6).fill(0)
    const monthlyVideos = new Array(6).fill(0)

    filteredVideos.forEach(video => {
      const videoDate = video.published_at || video.created_at
      if (videoDate) {
        const month = new Date(videoDate).getMonth()
        if (month < 6) {
          monthlyViews[month] += video.view_count || video.views || 0
          monthlyLikes[month] += video.like_count || video.likes || 0
          monthlyVideos[month] += 1
        }
      }
    })

    return {
      labels: months,
      datasets: [
        {
          label: 'Views (M)',
          data: monthlyViews.map(v => (v / 1000000).toFixed(1)),
          borderColor: 'rgb(75, 192, 192)',
          backgroundColor: 'rgba(75, 192, 192, 0.2)',
          tension: 0.4,
        },
        {
          label: 'Likes (K)',
          data: monthlyLikes.map(l => (l / 1000).toFixed(1)),
          borderColor: 'rgb(255, 99, 132)',
          backgroundColor: 'rgba(255, 99, 132, 0.2)',
          tension: 0.4,
        },
      ],
    }
  }
  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
    },
    scales: {
      y: {
        beginAtZero: true,
      },
    },
  }

  // Views per day distribution with country or influencer grouping
  const generateViewsByDayChartData = () => {
    if (viewsChartMode === 'country') {
      // Group by country
      const countryViewsData = {}
      const countryColors = {
        'Argentina': 'rgba(75, 192, 192, 0.8)',
        'Bolivia': 'rgba(255, 159, 64, 0.8)', 
        'Brasil': 'rgba(54, 162, 235, 0.8)',
        'Colombia': 'rgba(255, 205, 86, 0.8)',
        'Panama': 'rgba(153, 102, 255, 0.8)',
        'Peru': 'rgba(255, 99, 132, 0.8)',
        'Outros': 'rgba(128, 128, 128, 0.8)',
      }
      
      const countryBorderColors = {
        'Argentina': 'rgba(75, 192, 192, 1)',
        'Bolivia': 'rgba(255, 159, 64, 1)', 
        'Brasil': 'rgba(54, 162, 235, 1)',
        'Colombia': 'rgba(255, 205, 86, 1)',
        'Panama': 'rgba(153, 102, 255, 1)',
        'Peru': 'rgba(255, 99, 132, 1)',
        'Outros': 'rgba(128, 128, 128, 1)',
      }
      
      filteredVideos.forEach(video => {
        const date = new Date(video.published_at)
        const dayKey = date.toISOString().split('T')[0]
        const influencer = influencers.find(inf => inf.eldorado_username === video.eldorado_username)
        const country = influencer?.country ? 
          influencer.country.charAt(0).toUpperCase() + influencer.country.slice(1).toLowerCase() : 
          'Outros'
        
        if (!countryViewsData[country]) {
          countryViewsData[country] = {}
        }
        countryViewsData[country][dayKey] = (countryViewsData[country][dayKey] || 0) + (video.view_count || video.views || 0)
      })
      
      const allDates = [...new Set(filteredVideos.map(video => new Date(video.published_at).toISOString().split('T')[0]))].sort()
      
      const datasets = Object.keys(countryViewsData).map(country => ({
        label: country,
        data: allDates.map(date => countryViewsData[country][date] || 0),
        backgroundColor: countryColors[country] || countryColors['Outros'],
        borderColor: countryBorderColors[country] || countryBorderColors['Outros'],
        borderWidth: 2,
      }))
      
      return {
        labels: allDates.map(date => {
          const d = new Date(date)
          return d.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' })
        }),
        datasets
      }
    } else {
      // Group by influencer
      const influencerViewsData = {}
      const influencerColors = [
        'rgba(255, 99, 132, 0.8)',
        'rgba(54, 162, 235, 0.8)', 
        'rgba(255, 205, 86, 0.8)',
        'rgba(75, 192, 192, 0.8)',
        'rgba(153, 102, 255, 0.8)',
        'rgba(255, 159, 64, 0.8)',
        'rgba(199, 199, 199, 0.8)',
        'rgba(83, 102, 255, 0.8)',
      ]
      
      const influencerBorderColors = [
        'rgba(255, 99, 132, 1)',
        'rgba(54, 162, 235, 1)', 
        'rgba(255, 205, 86, 1)',
        'rgba(75, 192, 192, 1)',
        'rgba(153, 102, 255, 1)',
        'rgba(255, 159, 64, 1)',
        'rgba(199, 199, 199, 1)',
        'rgba(83, 102, 255, 1)',
      ]
      
      filteredVideos.forEach(video => {
        const date = new Date(video.published_at)
        const dayKey = date.toISOString().split('T')[0]
        const influencer = influencers.find(inf => inf.eldorado_username === video.eldorado_username)
        const name = influencer?.first_name || video.eldorado_username
        
        if (!influencerViewsData[name]) {
          influencerViewsData[name] = {}
        }
        influencerViewsData[name][dayKey] = (influencerViewsData[name][dayKey] || 0) + (video.view_count || video.views || 0)
      })
      
      const allDates = [...new Set(filteredVideos.map(video => new Date(video.published_at).toISOString().split('T')[0]))].sort()
      
      const datasets = Object.keys(influencerViewsData).map((name, index) => ({
        label: name,
        data: allDates.map(date => influencerViewsData[name][date] || 0),
        backgroundColor: influencerColors[index % influencerColors.length],
        borderColor: influencerBorderColors[index % influencerBorderColors.length],
        borderWidth: 2,
      }))
      
      return {
        labels: allDates.map(date => {
          const d = new Date(date)
          return d.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' })
        }),
        datasets
      }
    }
  }

  const viewsByDayChartData = generateViewsByDayChartData()

  const ownerDistribution = filteredInfluencers.reduce((acc, influencer) => {
    const owner = influencer.owner || 'Não informado'
    acc[owner] = (acc[owner] || 0) + 1
    return acc
  }, {})

  // Generate comparison chart when multiple influencers are selected
  const generateInfluencerComparisonData = () => {
    if (!filters?.selectedInfluencers || filters.selectedInfluencers.length <= 1) {
      return ownerChartData
    }

    const influencerStats = filters.selectedInfluencers.map((influencer, index) => {
      const influencerVideos = filteredVideos.filter(
        video => video.eldorado_username === influencer.eldorado_username
      )
      const totalViews = influencerVideos.reduce((sum, video) => sum + (video.view_count || video.views || 0), 0)
      const totalLikes = influencerVideos.reduce((sum, video) => sum + (video.like_count || video.likes || 0), 0)
      
      return {
        name: influencer.first_name,
        views: totalViews,
        likes: totalLikes,
        videos: influencerVideos.length,
        color: [
          'rgba(255, 99, 132, 0.8)',
          'rgba(54, 162, 235, 0.8)', 
          'rgba(255, 205, 86, 0.8)',
          'rgba(75, 192, 192, 0.8)',
          'rgba(153, 102, 255, 0.8)',
          'rgba(255, 159, 64, 0.8)',
        ][index % 6]
      }
    })

    return {
      labels: influencerStats.map(stat => stat.name),
      datasets: [
        {
          label: 'Views (M)',
          data: influencerStats.map(stat => (stat.views / 1000000).toFixed(1)),
          backgroundColor: influencerStats.map(stat => stat.color),
          borderColor: influencerStats.map(stat => stat.color.replace('0.8', '1')),
          borderWidth: 1,
        },
      ],
    }
  }

  const ownerChartData = {
    labels: Object.keys(ownerDistribution).map(owner => 
      owner.charAt(0).toUpperCase() + owner.slice(1)
    ),
    datasets: [
      {
        data: Object.values(ownerDistribution),
        backgroundColor: [
          'rgba(255, 99, 132, 0.8)',
          'rgba(54, 162, 235, 0.8)',
          'rgba(255, 205, 86, 0.8)',
          'rgba(75, 192, 192, 0.8)',
          'rgba(153, 102, 255, 0.8)',
          'rgba(255, 159, 64, 0.8)',
        ],
        borderColor: [
          'rgba(255, 99, 132, 1)',
          'rgba(54, 162, 235, 1)',
          'rgba(255, 205, 86, 1)',
          'rgba(75, 192, 192, 1)',
          'rgba(153, 102, 255, 1)',
          'rgba(255, 159, 64, 1)',
        ],
        borderWidth: 2,
      },
    ],
  }

  if (loading) {
    return (
      <div className="text-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-2 border-primary-600 border-t-transparent mx-auto mb-2" />
        <p className="text-gray-600">Carregando dados reais...</p>
      </div>
    )
  }

  if (influencers.length === 0) {
    return (
      <div className="text-center py-8">
        <p className="text-gray-600">
          Adicione influencers para ver as análises visuais
        </p>
      </div>
    )
  }

  const filteredStats = getFilteredStats()
  const hasFilters = (filters?.selectedInfluencers && filters.selectedInfluencers.length > 0) || 
                     (filters?.countries && filters.countries.length > 0) || 
                     filters?.dateRange?.start || 
                     filters?.dateRange?.end

  return (
    <div className="space-y-6">
      {/* Real Stats Cards - Filtered */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Total Views */}
        <div className="card">
          <div className="flex items-center space-x-3">
            <div className="p-3 bg-blue-100 rounded-lg">
              <Eye className="h-6 w-6 text-blue-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Total Views {hasFilters ? '(Filtrado)' : ''}</p>
              <p className="text-2xl font-bold text-blue-600">
                {formatNumber(hasFilters ? filteredStats.totalViews : (dashboardStats?.total_views || 0))}
              </p>
            </div>
          </div>
        </div>

        {/* Total Likes */}
        <div className="card">
          <div className="flex items-center space-x-3">
            <div className="p-3 bg-red-100 rounded-lg">
              <Heart className="h-6 w-6 text-red-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Total Likes {hasFilters ? '(Filtrado)' : ''}</p>
              <p className="text-2xl font-bold text-red-600">
                {formatNumber(hasFilters ? filteredStats.totalLikes : (dashboardStats?.total_likes || 0))}
              </p>
            </div>
          </div>
        </div>

        {/* Top Video - Filtered or Global */}
        {(hasFilters ? filteredStats.topVideo : topVideos[0]) && (
          <div className="card">
            <div className="flex items-center space-x-3">
              <div className="p-3 bg-green-100 rounded-lg">
                <TrendingUp className="h-6 w-6 text-green-600" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm text-gray-600">Top Vídeo {hasFilters ? '(Filtrado)' : ''}</p>
                <p className="text-lg font-bold text-green-600">
                  {formatNumber(hasFilters 
                    ? (filteredStats.topVideo?.view_count || filteredStats.topVideo?.views || 0)
                    : topVideos[0].metric_value
                  )} views
                </p>
                <div className="flex items-center justify-between mt-1">
                  <div className="flex-1 min-w-0 mr-3">
                    <p className="text-sm text-gray-800 truncate">
                      {(hasFilters ? filteredStats.topVideo?.description : topVideos[0].description) || 'Sem descrição'}
                    </p>
                    <p className="text-xs text-gray-500">
                      @{hasFilters ? filteredStats.topVideo?.eldorado_username : topVideos[0].eldorado_username}
                    </p>
                  </div>
                  <a
                    href={hasFilters 
                      ? `https://www.tiktok.com/@${filteredStats.topVideo?.tiktok_username || filteredStats.topVideo?.eldorado_username}/video/${filteredStats.topVideo?.tiktok_video_id}`
                      : `https://www.tiktok.com/@${topVideos[0].tiktok_username}/video/${topVideos[0].tiktok_video_id}`
                    }
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center space-x-1 text-xs text-blue-600 hover:text-blue-800 whitespace-nowrap"
                  >
                    <ExternalLink className="h-3 w-3" />
                    <span>Ver TikTok</span>
                  </a>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Views by Day with toggle */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium">Views por Dia</h3>
            <div className="flex items-center bg-gray-100 rounded-lg p-1">
              <button
                onClick={() => setViewsChartMode('country')}
                className={`px-3 py-1.5 text-sm rounded-md transition-colors ${
                  viewsChartMode === 'country'
                    ? 'bg-white text-primary-600 shadow-sm font-medium'
                    : 'text-gray-600 hover:text-gray-800'
                }`}
              >
                Por País
              </button>
              <button
                onClick={() => setViewsChartMode('influencer')}
                className={`px-3 py-1.5 text-sm rounded-md transition-colors ${
                  viewsChartMode === 'influencer'
                    ? 'bg-white text-primary-600 shadow-sm font-medium'
                    : 'text-gray-600 hover:text-gray-800'
                }`}
              >
                Por Influencer
              </button>
            </div>
          </div>
          <div className="h-64">
            <Bar 
              data={viewsByDayChartData} 
              options={{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                  legend: {
                    position: 'top',
                    display: true,
                  },
                },
                scales: {
                  x: {
                    stacked: true,
                  },
                  y: {
                    stacked: true,
                    beginAtZero: true,
                  },
                },
              }} 
            />
          </div>
        </div>

        {/* Comparison Chart or Owner Distribution */}
        <div className="card">
          <h3 className="text-lg font-medium mb-4">
            {filters?.selectedInfluencers && filters.selectedInfluencers.length > 1 
              ? `Comparação de Influencers (${filters.selectedInfluencers.length})` 
              : 'Distribuição por Responsável'
            }
          </h3>
          <div className="h-64 flex items-center justify-center">
            {filters?.selectedInfluencers && filters.selectedInfluencers.length > 1 ? (
              <Bar 
                data={generateInfluencerComparisonData()} 
                options={{
                  responsive: true,
                  maintainAspectRatio: false,
                  plugins: {
                    legend: {
                      position: 'top',
                    },
                  },
                  scales: {
                    y: {
                      beginAtZero: true,
                    },
                  },
                }}
              />
            ) : (
              <Doughnut 
                data={ownerChartData} 
                options={{
                  responsive: true,
                  maintainAspectRatio: false,
                  plugins: {
                    legend: {
                      position: 'bottom',
                    },
                  },
                }}
              />
            )}
          </div>
        </div>
      </div>

      {/* Performance Trends - Real Data */}
      <div className="card">
        <h3 className="text-lg font-medium mb-4">Performance Real por Mês</h3>
        <div className="h-64">
          <Line 
            data={generateMonthlyData()} 
            options={{
              responsive: true,
              maintainAspectRatio: false,
              plugins: {
                legend: {
                  position: 'top',
                },
              },
              scales: {
                y: {
                  beginAtZero: true,
                },
              },
            }} 
          />
        </div>
      </div>
    </div>
  )
}

export default AnalyticsCharts