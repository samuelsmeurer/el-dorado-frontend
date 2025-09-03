import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000/api/v1'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// API Methods
export const influencerAPI = {
  // Get all influencers
  getAll: (params = {}) => api.get('/influencers/', { params }),
  
  // Get influencer by username
  getByUsername: (username) => api.get(`/influencers/${username}`),
  
  // Create new influencer
  create: (data) => api.post('/influencers/', data),
  
  // Update influencer
  update: (username, data) => api.put(`/influencers/${username}`, data),
  
  // Delete influencer
  delete: (username) => api.delete(`/influencers/${username}`),
  
  // Get social IDs
  getSocialIds: (username) => api.get(`/influencers/${username}/social-ids`),
  
  // Sync TikTok ID
  syncTikTokId: (username) => api.post(`/influencers/${username}/sync-tiktok-id`),
}

export const videosAPI = {
  // Get all videos
  getAll: (params = {}) => api.get('/videos/', { params }),
  
  // Get videos by influencer
  getByInfluencer: (username, params = {}) => api.get(`/videos/influencer/${username}`, { params }),
  
  // Sync videos from TikTok for specific influencer
  syncVideos: (username) => api.post(`/videos/sync/${username}`),
  
  // Sync videos for all influencers
  syncAllVideos: () => api.post('/videos/sync/all'),
}

export const analyticsAPI = {
  // Get dashboard stats
  getDashboardStats: () => api.get('/analytics/dashboard'),
  
  // Get top videos
  getTopVideos: (metric = 'views', limit = 10) => 
    api.get(`/analytics/top-videos/${metric}`, { params: { limit } }),
  
  // Get influencer stats
  getInfluencerStats: (limit = 10) => 
    api.get('/analytics/influencer-stats', { params: { limit } }),
}

export default api