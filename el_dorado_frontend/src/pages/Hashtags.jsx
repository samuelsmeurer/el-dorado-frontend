import React, { useState, useEffect } from 'react'
import { Plus, Search, Edit, Trash2, Hash, TrendingUp, Eye, Video } from 'lucide-react'
import toast from 'react-hot-toast'

const Hashtags = () => {
  const [hashtags, setHashtags] = useState([])
  const [loading, setLoading] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [showModal, setShowModal] = useState(false)
  const [selectedHashtag, setSelectedHashtag] = useState(null)

  // Mock data for now - will be replaced with API calls later
  const mockHashtags = [
    {
      id: 1,
      tag: '@El Dorado P2P',
      description: 'Hashtag principal do El Dorado',
      videos_count: 47,
      total_views: 2850000,
      total_likes: 156000,
      created_at: '2024-01-15',
      status: 'active'
    }
  ]

  useEffect(() => {
    // For now, use mock data
    setHashtags(mockHashtags)
  }, [])

  const filteredHashtags = hashtags.filter(hashtag =>
    hashtag.tag.toLowerCase().includes(searchTerm.toLowerCase()) ||
    hashtag.description.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const formatNumber = (num) => {
    if (num >= 1000000) {
      return (num / 1000000).toFixed(1) + 'M'
    } else if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'K'
    }
    return num.toString()
  }

  const handleDelete = (id) => {
    if (!confirm('Tem certeza que deseja deletar esta hashtag?')) return
    
    // Mock delete - will be replaced with API call
    setHashtags(prev => prev.filter(tag => tag.id !== id))
    toast.success('Hashtag deletada com sucesso!')
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Hashtags</h1>
          <p className="text-gray-600 mt-2">
            Gerencie as hashtags que você deseja trackear nos vídeos dos influenciadores
          </p>
        </div>
        <button
          onClick={() => {
            setSelectedHashtag(null)
            setShowModal(true)
          }}
          className="btn-primary flex items-center space-x-2"
        >
          <Plus className="h-4 w-4" />
          <span>Adicionar Hashtag</span>
        </button>
      </div>

      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
        <input
          type="text"
          placeholder="Buscar hashtag..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="input-field pl-10"
        />
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="card">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-purple-100 rounded-lg">
              <Hash className="h-6 w-6 text-purple-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Total Hashtags</p>
              <p className="text-2xl font-bold">{hashtags.length}</p>
            </div>
          </div>
        </div>
        
        <div className="card">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Video className="h-6 w-6 text-blue-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Vídeos Trackeados</p>
              <p className="text-2xl font-bold">
                {hashtags.reduce((sum, tag) => sum + tag.videos_count, 0)}
              </p>
            </div>
          </div>
        </div>
        
        <div className="card">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-green-100 rounded-lg">
              <Eye className="h-6 w-6 text-green-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Total Views</p>
              <p className="text-2xl font-bold">
                {formatNumber(hashtags.reduce((sum, tag) => sum + tag.total_views, 0))}
              </p>
            </div>
          </div>
        </div>
        
        <div className="card">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-red-100 rounded-lg">
              <TrendingUp className="h-6 w-6 text-red-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Hashtags Ativas</p>
              <p className="text-2xl font-bold">
                {hashtags.filter(tag => tag.status === 'active').length}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Hashtags Table */}
      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Hashtag
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Vídeos
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Views
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Likes
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
              {filteredHashtags.map((hashtag) => (
                <tr key={hashtag.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div>
                      <div className="flex items-center space-x-2">
                        <Hash className="h-4 w-4 text-gray-400" />
                        <div className="text-sm font-medium text-gray-900">
                          {hashtag.tag}
                        </div>
                      </div>
                      <div className="text-sm text-gray-500">
                        {hashtag.description}
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    <div className="flex items-center">
                      <Video className="h-4 w-4 text-blue-500 mr-2" />
                      {hashtag.videos_count}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    <div className="flex items-center">
                      <Eye className="h-4 w-4 text-green-500 mr-2" />
                      {formatNumber(hashtag.total_views)}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    <div className="flex items-center">
                      <TrendingUp className="h-4 w-4 text-red-500 mr-2" />
                      {formatNumber(hashtag.total_likes)}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      hashtag.status === 'active' 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-gray-100 text-gray-800'
                    }`}>
                      {hashtag.status === 'active' ? 'Ativa' : 'Inativa'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <div className="flex items-center justify-end space-x-2">
                      <button
                        onClick={() => {
                          setSelectedHashtag(hashtag)
                          setShowModal(true)
                        }}
                        className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                        title="Editar"
                      >
                        <Edit className="h-4 w-4" />
                      </button>
                      <button
                        onClick={() => handleDelete(hashtag.id)}
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

      {/* Empty State */}
      {filteredHashtags.length === 0 && (
        <div className="text-center py-12">
          <Hash className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-500 text-lg">
            {searchTerm ? 'Nenhuma hashtag encontrada' : 'Nenhuma hashtag configurada'}
          </p>
          <p className="text-gray-400 text-sm mt-2">
            {!searchTerm && 'Adicione sua primeira hashtag para começar o tracking'}
          </p>
        </div>
      )}

      {/* Modal placeholder - will be implemented later */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-medium mb-4">
              {selectedHashtag ? 'Editar Hashtag' : 'Adicionar Hashtag'}
            </h3>
            <p className="text-gray-500 mb-4">
              Modal de hashtag será implementado em breve...
            </p>
            <div className="flex justify-end space-x-3">
              <button
                onClick={() => setShowModal(false)}
                className="btn-secondary"
              >
                Cancelar
              </button>
              <button
                onClick={() => {
                  setShowModal(false)
                  toast.success('Funcionalidade será implementada em breve!')
                }}
                className="btn-primary"
              >
                {selectedHashtag ? 'Salvar' : 'Adicionar'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default Hashtags