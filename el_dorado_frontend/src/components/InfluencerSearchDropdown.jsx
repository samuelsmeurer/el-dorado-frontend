import React, { useState, useRef, useEffect } from 'react'
import { Search, X } from 'lucide-react'

const InfluencerSearchDropdown = ({ influencers, selectedInfluencers = [], onSelect, onClearAll }) => {
  const [searchTerm, setSearchTerm] = useState('')
  const [showDropdown, setShowDropdown] = useState(false)
  const [filteredInfluencers, setFilteredInfluencers] = useState([])
  const dropdownRef = useRef(null)

  useEffect(() => {
    if (searchTerm.length > 0) {
      const filtered = influencers.filter(influencer => {
        const matchesSearch = influencer.first_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
          influencer.eldorado_username.toLowerCase().includes(searchTerm.toLowerCase())
        const isAlreadySelected = selectedInfluencers.some(selected => 
          selected.eldorado_username === influencer.eldorado_username
        )
        return matchesSearch && !isAlreadySelected
      })
      setFilteredInfluencers(filtered)
      setShowDropdown(true)
    } else {
      setFilteredInfluencers([])
      setShowDropdown(false)
    }
  }, [searchTerm, influencers, selectedInfluencers])

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setShowDropdown(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const handleSelectInfluencer = (influencer) => {
    onSelect([...selectedInfluencers, influencer])
    setSearchTerm('')
    setShowDropdown(false)
  }

  const handleRemoveInfluencer = (influencerToRemove) => {
    const newSelected = selectedInfluencers.filter(
      inf => inf.eldorado_username !== influencerToRemove.eldorado_username
    )
    onSelect(newSelected)
  }

  const handleClearAll = () => {
    if (onClearAll) {
      onClearAll()
    } else {
      onSelect([])
    }
    setSearchTerm('')
    setShowDropdown(false)
  }

  return (
    <div className="relative" ref={dropdownRef}>
      <div className="relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
        <input
          type="text"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          onFocus={() => {
            if (searchTerm && filteredInfluencers.length > 0) {
              setShowDropdown(true)
            }
          }}
          placeholder={selectedInfluencers.length > 0 ? "Adicionar mais influencers..." : "Buscar influencer..."}
          className="input-field pl-10"
        />
      </div>

      {/* Dropdown with suggestions */}
      {showDropdown && filteredInfluencers.length > 0 && (
        <div className="absolute z-50 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg max-h-60 overflow-y-auto">
          {filteredInfluencers.map((influencer) => (
            <button
              key={influencer.eldorado_username}
              onClick={() => handleSelectInfluencer(influencer)}
              className="w-full px-4 py-3 text-left hover:bg-gray-50 flex items-center space-x-3 border-b border-gray-100 last:border-b-0"
            >
              <div className="flex-shrink-0 w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
                <span className="text-primary-600 font-medium text-sm">
                  {influencer.first_name.charAt(0).toUpperCase()}
                </span>
              </div>
              <div className="flex-1">
                <p className="font-medium text-gray-900">{influencer.first_name}</p>
                <p className="text-sm text-gray-500">@{influencer.eldorado_username}</p>
              </div>
              {influencer.country && (
                <span className="text-xs text-gray-400">{influencer.country}</span>
              )}
            </button>
          ))}
        </div>
      )}

      {/* Selected count indicator */}
      {selectedInfluencers.length > 0 && (
        <div className="mt-3 p-2 bg-blue-50 border border-blue-200 rounded-lg">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2 flex-wrap">
              <span className="text-sm font-medium text-blue-700">
                {selectedInfluencers.length} influencer(s) selecionado(s)
              </span>
            </div>
            <button
              onClick={handleClearAll}
              className="text-xs text-red-600 hover:text-red-800"
            >
              Limpar todos
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

export default InfluencerSearchDropdown