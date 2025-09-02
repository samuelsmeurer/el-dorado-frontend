import React, { useState, useEffect } from 'react'
import { Plus, Search, Edit, Trash2, ExternalLink, Grid, List } from 'lucide-react'
import { influencerAPI, videosAPI } from '../services/api'
import InfluencerModal from '../components/InfluencerModal'
import toast from 'react-hot-toast'

const Influencers = () => {
  const [influencers, setInfluencers] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [showModal, setShowModal] = useState(false)
  const [selectedInfluencer, setSelectedInfluencer] = useState(null)
  const [viewMode, setViewMode] = useState('cards') // 'cards' or 'list'

  useEffect(() => {
    loadInfluencers()
  }, [])

  const loadInfluencers = async () => {
    try {
      const response = await influencerAPI.getAll({ limit: 1000 })
      setInfluencers(response.data)
    } catch (error) {
      console.error('Error loading influencers:', error)
      toast.error('Erro ao carregar influencers')
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (username) => {
    if (!confirm(`Tem certeza que deseja deletar o influencer ${username}?`)) return

    try {
      await influencerAPI.delete(username)
      setInfluencers(prev => prev.filter(inf => inf.eldorado_username !== username))
      toast.success('Influencer deletado com sucesso!')
    } catch (error) {
      console.error('Error deleting influencer:', error)
      toast.error('Erro ao deletar influencer')
    }
  }

  const handleSave = async (data) => {
    try {
      console.log('Saving influencer with data:', data)
      if (selectedInfluencer) {
        // Update
        const response = await influencerAPI.update(selectedInfluencer.eldorado_username, data)
        console.log('Update response:', response)
        toast.success('Influencer atualizado!')
      } else {
        // Create new influencer
        const response = await influencerAPI.create(data)
        console.log('Create response:', response)
        const newInfluencer = response.data
        
        toast.success('Influencer criado!')
        
        // Auto-sync TikTok ID if tiktok_username exists
        if (data.tiktok_username && data.tiktok_username.trim()) {
          try {
            console.log('Syncing TikTok ID for:', newInfluencer.eldorado_username)
            await influencerAPI.syncTikTokId(newInfluencer.eldorado_username)
            toast.success('TikTok ID sincronizado!')
            
            // Auto-sync videos after getting TikTok ID
            try {
              console.log('Syncing videos for:', newInfluencer.eldorado_username)
              await videosAPI.syncVideos(newInfluencer.eldorado_username)
              toast.success('Vídeos sincronizados!')
            } catch (videoError) {
              console.error('Error syncing videos:', videoError)
              toast.error('Erro ao sincronizar vídeos (TikTok ID pode não ter sido encontrado)')
            }
          } catch (tiktokError) {
            console.error('Error syncing TikTok ID:', tiktokError)
            toast.error('Erro ao sincronizar TikTok ID')
          }
        }
      }
      
      loadInfluencers()
      setShowModal(false)
      setSelectedInfluencer(null)
    } catch (error) {
      console.error('Full error object:', error)
      console.error('Error response:', error.response)
      console.error('Error message:', error.message)
      
      if (error.response?.data?.detail) {
        toast.error(`Erro: ${error.response.data.detail}`)
      } else if (error.response?.status === 422) {
        toast.error('Dados inválidos. Verifique os campos obrigatórios.')
      } else {
        toast.error(`Erro ao salvar influencer: ${error.message}`)
      }
    }
  }

  const filteredInfluencers = influencers.filter(influencer =>
    influencer.first_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    influencer.eldorado_username.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const ownerColors = {
    alejandra: 'bg-pink-100 text-pink-800',
    alessandro: 'bg-blue-100 text-blue-800',
    bianca: 'bg-purple-100 text-purple-800',
    camilo: 'bg-teal-100 text-teal-800',
    jesus: 'bg-green-100 text-green-800',
    julia: 'bg-yellow-100 text-yellow-800',
    samuel: 'bg-red-100 text-red-800',
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Influencers</h1>
          <p className="text-gray-600 mt-2">
            Gerencie todos os seus influenciadores El Dorado
          </p>
        </div>
        <div className="flex items-center space-x-3">
          {/* View Mode Toggle */}
          <div className="flex items-center bg-gray-100 rounded-lg p-1">
            <button
              onClick={() => setViewMode('cards')}
              className={`p-2 rounded-md transition-colors ${
                viewMode === 'cards'
                  ? 'bg-white text-primary-600 shadow-sm'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
              title="Visualizar em cards"
            >
              <Grid className="h-4 w-4" />
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`p-2 rounded-md transition-colors ${
                viewMode === 'list'
                  ? 'bg-white text-primary-600 shadow-sm'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
              title="Visualizar em lista"
            >
              <List className="h-4 w-4" />
            </button>
          </div>
          
          <button
            onClick={() => {
              setSelectedInfluencer(null)
              setShowModal(true)
            }}
            className="btn-primary flex items-center space-x-2"
          >
            <Plus className="h-4 w-4" />
            <span>Adicionar Influencer</span>
          </button>
        </div>
      </div>

      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
        <input
          type="text"
          placeholder="Buscar por nome ou username..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="input-field pl-10"
        />
      </div>

      {/* Influencers Content */}
      {viewMode === 'cards' ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredInfluencers.map((influencer) => (
            <div key={influencer.id} className="card hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">
                    {influencer.first_name}
                  </h3>
                  <p className="text-gray-600 text-sm">
                    @{influencer.eldorado_username}
                  </p>
                </div>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                  ownerColors[influencer.owner] || 'bg-gray-100 text-gray-800'
                }`}>
                  {influencer.owner.charAt(0).toUpperCase() + influencer.owner.slice(1)}
                </span>
              </div>

              <div className="space-y-2 mb-4">
                {influencer.phone && (
                  <p className="text-sm text-gray-600">
                    📞 {influencer.phone}
                  </p>
                )}
                {influencer.country && (
                  <p className="text-sm text-gray-600">
                    🌍 {influencer.country}
                  </p>
                )}
                <p className="text-sm text-gray-600">
                  Status: <span className="font-medium capitalize">{influencer.status}</span>
                </p>
              </div>

              <div className="flex space-x-2">
                <button
                  onClick={() => {
                    setSelectedInfluencer(influencer)
                    setShowModal(true)
                  }}
                  className="flex-1 btn-secondary flex items-center justify-center space-x-1"
                >
                  <Edit className="h-4 w-4" />
                  <span>Editar</span>
                </button>
                <button
                  onClick={() => handleDelete(influencer.eldorado_username)}
                  className="px-3 py-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="card overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Influencer
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Contato
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    País
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Responsável
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Ações
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredInfluencers.map((influencer) => (
                  <tr key={influencer.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div>
                        <div className="text-sm font-medium text-gray-900">
                          {influencer.first_name}
                        </div>
                        <div className="text-sm text-gray-500">
                          @{influencer.eldorado_username}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {influencer.phone || '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {influencer.country || '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        ownerColors[influencer.owner] || 'bg-gray-100 text-gray-800'
                      }`}>
                        {influencer.owner.charAt(0).toUpperCase() + influencer.owner.slice(1)}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 capitalize">
                      {influencer.status}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <div className="flex items-center justify-end space-x-2">
                        <button
                          onClick={() => {
                            setSelectedInfluencer(influencer)
                            setShowModal(true)
                          }}
                          className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                          title="Editar"
                        >
                          <Edit className="h-4 w-4" />
                        </button>
                        <button
                          onClick={() => handleDelete(influencer.eldorado_username)}
                          className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                          title="Deletar"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Empty State */}
      {filteredInfluencers.length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-500 text-lg">
            {searchTerm ? 'Nenhum influencer encontrado' : 'Nenhum influencer cadastrado'}
          </p>
        </div>
      )}

      {/* Modal */}
      {showModal && (
        <InfluencerModal
          influencer={selectedInfluencer}
          onClose={() => {
            setShowModal(false)
            setSelectedInfluencer(null)
          }}
          onSave={handleSave}
        />
      )}
    </div>
  )
}

export default Influencers