import React from 'react'

const StatsCard = ({ title, value, icon: Icon, color = 'primary', format = 'default' }) => {
  const colorClasses = {
    primary: 'text-primary-600 bg-primary-50',
    blue: 'text-blue-600 bg-blue-50',
    green: 'text-green-600 bg-green-50',
    red: 'text-red-600 bg-red-50',
    yellow: 'text-yellow-600 bg-yellow-50',
  }

  const formatValue = (val) => {
    if (format === 'number' && val >= 1000) {
      if (val >= 1000000) {
        return `${(val / 1000000).toFixed(1)}M`
      }
      return `${(val / 1000).toFixed(1)}K`
    }
    return val.toLocaleString()
  }

  return (
    <div className="card">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-600 mb-1">{title}</p>
          <p className="text-2xl font-bold text-gray-900">
            {formatValue(value)}
          </p>
        </div>
        <div className={`p-3 rounded-lg ${colorClasses[color]}`}>
          <Icon className="h-6 w-6" />
        </div>
      </div>
    </div>
  )
}

export default StatsCard