import React, { useState, useEffect } from 'react'
import { X, User, AtSign, Phone, Globe, Crown, Video } from 'lucide-react'

const InfluencerModal = ({ influencer, onClose, onSave }) => {
  const [formData, setFormData] = useState({
    first_name: '',
    eldorado_username: '',
    phone: '',
    country: '',
    owner: 'samuel',
    tiktok_username: ''
  })
  const [errors, setErrors] = useState({})
  const [loading, setLoading] = useState(false)

  const owners = [
    'alejandra',
    'alessandro', 
    'bianca',
    'camilo',
    'jesus',
    'julia',
    'samuel'
  ]

  useEffect(() => {
    if (influencer) {
      setFormData({
        first_name: influencer.first_name || '',
        eldorado_username: influencer.eldorado_username || '',
        phone: influencer.phone || '',
        country: influencer.country || '',
        owner: influencer.owner || 'samuel',
        tiktok_username: influencer.tiktok_username || ''
      })
    }
  }, [influencer])

  const validateForm = () => {
    const newErrors = {}
    
    if (!formData.first_name.trim()) {
      newErrors.first_name = 'Nome é obrigatório'
    } else if (formData.first_name.trim().length < 2) {
      newErrors.first_name = 'Nome deve ter pelo menos 2 caracteres'
    } else if (!/^[a-zA-ZÀ-ÿ\s]+$/.test(formData.first_name.trim())) {
      newErrors.first_name = 'Nome deve conter apenas letras e espaços'
    }
    
    if (!formData.eldorado_username.trim()) {
      newErrors.eldorado_username = 'Username El Dorado é obrigatório'
    } else if (formData.eldorado_username.trim().length < 3) {
      newErrors.eldorado_username = 'Username deve ter pelo menos 3 caracteres'
    } else if (!/^[a-zA-Z0-9_]+$/.test(formData.eldorado_username)) {
      newErrors.eldorado_username = 'Username deve conter apenas letras, números e _'
    } else if (formData.eldorado_username.includes('__')) {
      newErrors.eldorado_username = 'Username não pode ter underscores consecutivos'
    }
    
    if (formData.phone && formData.phone.trim()) {
      const cleanPhone = formData.phone.replace(/[\s\-\(\)]/g, '')
      if (!/^[\+]?[1-9][\d]{8,15}$/.test(cleanPhone)) {
        newErrors.phone = 'Formato de telefone inválido (mínimo 9 dígitos)'
      }
    }
    
    if (formData.tiktok_username && formData.tiktok_username.trim()) {
      const tiktokUsername = formData.tiktok_username.trim()
      if (!tiktokUsername.startsWith('@')) {
        setFormData(prev => ({ ...prev, tiktok_username: '@' + tiktokUsername.replace('@', '') }))
      } else if (tiktokUsername.length < 2) {
        newErrors.tiktok_username = 'Username TikTok deve ter pelo menos 1 caractere após @'
      } else if (!/^@[a-zA-Z0-9_.]+$/.test(tiktokUsername)) {
        newErrors.tiktok_username = 'Username TikTok deve conter apenas letras, números, _ e .'
      }
    }
    
    if (!formData.owner) {
      newErrors.owner = 'Responsável é obrigatório'
    }
    
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!validateForm()) return
    
    setLoading(true)
    try {
      await onSave(formData)
    } finally {
      setLoading(false)
    }
  }

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
    
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }))
    }
  }

  const countries = [
    'Argentina', 'Bolivia', 'Brasil', 'Colombia', 'Panama', 'Peru'
  ]

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-lg mx-4 max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-2">
            <div className="p-2 bg-primary-100 rounded-lg">
              <Crown className="h-5 w-5 text-primary-600" />
            </div>
            <h2 className="text-xl font-semibold">
              {influencer ? 'Editar Influencer' : 'Novo Influencer'}
            </h2>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 p-1"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5">
          {/* Nome */}
          <div>
            <label className="flex items-center space-x-2 text-sm font-medium text-gray-700 mb-2">
              <User className="h-4 w-4" />
              <span>Nome Completo *</span>
            </label>
            <input
              type="text"
              name="first_name"
              value={formData.first_name}
              onChange={handleChange}
              className={`input-field ${errors.first_name ? 'border-red-300' : ''}`}
              placeholder="Nome do influencer"
            />
            {errors.first_name && (
              <p className="text-red-500 text-xs mt-1">{errors.first_name}</p>
            )}
          </div>

          {/* Username El Dorado */}
          <div>
            <label className="flex items-center space-x-2 text-sm font-medium text-gray-700 mb-2">
              <AtSign className="h-4 w-4" />
              <span>Username El Dorado *</span>
            </label>
            <input
              type="text"
              name="eldorado_username"
              value={formData.eldorado_username}
              onChange={handleChange}
              disabled={!!influencer}
              className={`input-field ${errors.eldorado_username ? 'border-red-300' : ''} ${!!influencer ? 'bg-gray-100' : ''}`}
              placeholder="username_eldorado"
            />
            {errors.eldorado_username && (
              <p className="text-red-500 text-xs mt-1">{errors.eldorado_username}</p>
            )}
            {influencer && (
              <p className="text-gray-500 text-xs mt-1">Username não pode ser alterado</p>
            )}
          </div>

          {/* Grid de 2 colunas */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Telefone */}
            <div>
              <label className="flex items-center space-x-2 text-sm font-medium text-gray-700 mb-2">
                <Phone className="h-4 w-4" />
                <span>Telefone</span>
              </label>
              <input
                type="tel"
                name="phone"
                value={formData.phone}
                onChange={handleChange}
                className={`input-field ${errors.phone ? 'border-red-300' : ''}`}
                placeholder="+55 11 99999-9999"
              />
              {errors.phone && (
                <p className="text-red-500 text-xs mt-1">{errors.phone}</p>
              )}
            </div>

            {/* País */}
            <div>
              <label className="flex items-center space-x-2 text-sm font-medium text-gray-700 mb-2">
                <Globe className="h-4 w-4" />
                <span>País</span>
              </label>
              <select
                name="country"
                value={formData.country}
                onChange={handleChange}
                className="input-field"
              >
                <option value="">Selecione o país</option>
                {countries.map(country => (
                  <option key={country} value={country}>
                    {country}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Owner */}
          <div>
            <label className="flex items-center space-x-2 text-sm font-medium text-gray-700 mb-2">
              <Crown className="h-4 w-4" />
              <span>Responsável *</span>
            </label>
            <select
              name="owner"
              value={formData.owner}
              onChange={handleChange}
              required
              className="input-field"
            >
              {owners.map(owner => (
                <option key={owner} value={owner}>
                  {owner.charAt(0).toUpperCase() + owner.slice(1)}
                </option>
              ))}
            </select>
          </div>

          {/* TikTok Username */}
          <div>
            <label className="flex items-center space-x-2 text-sm font-medium text-gray-700 mb-2">
              <Video className="h-4 w-4" />
              <span>TikTok Username</span>
            </label>
            <input
              type="text"
              name="tiktok_username"
              value={formData.tiktok_username}
              onChange={handleChange}
              className={`input-field ${errors.tiktok_username ? 'border-red-300' : ''}`}
              placeholder="@usuario_tiktok"
            />
            {errors.tiktok_username && (
              <p className="text-red-500 text-xs mt-1">{errors.tiktok_username}</p>
            )}
            {!errors.tiktok_username && (
              <p className="text-gray-500 text-xs mt-1">
                Opcional: Adicione o @ se não tiver
              </p>
            )}
          </div>

          <div className="flex space-x-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 btn-secondary"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex-1 btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <div className="flex items-center justify-center space-x-2">
                  <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent" />
                  <span>{influencer ? 'Atualizando...' : 'Criando...'}</span>
                </div>
              ) : (
                influencer ? 'Atualizar' : 'Criar'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default InfluencerModal