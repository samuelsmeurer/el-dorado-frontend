import React, { useState } from 'react'
import { Calendar, ChevronDown, Search } from 'lucide-react'

const DateRangeFilter = ({ dateRange, onDateRangeChange, onSearch }) => {
  const [showPresets, setShowPresets] = useState(false)
  const [selectedPreset, setSelectedPreset] = useState('custom')

  const presets = [
    { key: 'last7', label: 'Últimos 7 dias', days: 7 },
    { key: 'last14', label: 'Últimos 14 dias', days: 14 },
    { key: 'last30', label: 'Últimos 30 dias', days: 30 },
    { key: 'last60', label: 'Últimos 60 dias', days: 60 },
    { key: 'last90', label: 'Últimos 90 dias', days: 90 },
    { key: 'thisYear', label: 'Este ano', days: null },
    { key: 'custom', label: 'Período personalizado', days: null }
  ]

  const applyPreset = (preset) => {
    if (preset.key === 'custom') {
      setSelectedPreset('custom')
      setShowPresets(false)
      return
    }

    const endDate = new Date()
    let startDate = new Date()

    if (preset.key === 'thisYear') {
      // First day of current year
      startDate = new Date(endDate.getFullYear(), 0, 1)
    } else {
      // Regular days-based preset
      startDate.setDate(endDate.getDate() - preset.days)
    }

    const newDateRange = {
      start: startDate.toISOString().split('T')[0],
      end: endDate.toISOString().split('T')[0]
    }

    onDateRangeChange(newDateRange)
    setSelectedPreset(preset.key)
    setShowPresets(false)
  }

  const getCurrentPresetLabel = () => {
    const currentPreset = presets.find(p => p.key === selectedPreset)
    return currentPreset ? currentPreset.label : 'Período personalizado'
  }

  const handleManualDateChange = (field, value) => {
    const newDateRange = {
      ...dateRange,
      [field]: value
    }
    onDateRangeChange(newDateRange)
    setSelectedPreset('custom')
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <label className="flex items-center space-x-2 text-sm font-medium text-gray-700">
          <Calendar className="h-4 w-4" />
          <span>Período</span>
        </label>
        
        <div className="relative">
          <button
            onClick={() => setShowPresets(!showPresets)}
            className="flex items-center space-x-2 px-3 py-1.5 text-sm border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          >
            <span>{getCurrentPresetLabel()}</span>
            <ChevronDown className="h-3 w-3" />
          </button>

          {showPresets && (
            <div className="absolute right-0 top-full mt-1 w-48 bg-white border border-gray-200 rounded-lg shadow-lg z-50">
              {presets.map((preset) => (
                <button
                  key={preset.key}
                  onClick={() => applyPreset(preset)}
                  className={`w-full px-4 py-2 text-left text-sm hover:bg-gray-50 border-b border-gray-100 last:border-b-0 ${
                    selectedPreset === preset.key ? 'bg-primary-50 text-primary-600' : ''
                  }`}
                >
                  {preset.label}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      <div className="flex items-center space-x-2">
        <div className="flex-1">
          <input
            type="date"
            value={dateRange.start}
            onChange={(e) => handleManualDateChange('start', e.target.value)}
            className="input-field text-sm"
            placeholder="Data início"
          />
        </div>
        <span className="text-gray-400">até</span>
        <div className="flex-1">
          <input
            type="date"
            value={dateRange.end}
            onChange={(e) => handleManualDateChange('end', e.target.value)}
            className="input-field text-sm"
            placeholder="Data fim"
          />
        </div>
        <button
          onClick={onSearch}
          className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 flex items-center space-x-2"
        >
          <Search className="h-4 w-4" />
          <span>Buscar</span>
        </button>
      </div>
    </div>
  )
}

export default DateRangeFilter