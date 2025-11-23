'use client'

export default function Analytics({ stats }) {
  if (!stats) return null

  const efficiency = stats.totalInputTokens > 0 
    ? (stats.totalOutputTokens / stats.totalInputTokens).toFixed(2)
    : '0.00'

  return (
    <div className="bg-gradient-to-br from-purple-50 to-blue-50 rounded-xl p-6 shadow-lg border border-purple-200">
      <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
        <span className="text-2xl">📊</span>
        Translation Analytics
      </h3>
      
      {/* Main Metrics Grid */}
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-white rounded-lg p-4 shadow-sm border border-gray-100">
          <div className="text-sm text-gray-500 mb-1">Input Tokens</div>
          <div className="text-2xl font-bold text-blue-600">
            {stats.totalInputTokens?.toLocaleString() || 0}
          </div>
          <div className="text-xs text-gray-400 mt-1">Prompt</div>
        </div>
        
        <div className="bg-white rounded-lg p-4 shadow-sm border border-gray-100">
          <div className="text-sm text-gray-500 mb-1">Output Tokens</div>
          <div className="text-2xl font-bold text-green-600">
            {stats.totalOutputTokens?.toLocaleString() || 0}
          </div>
          <div className="text-xs text-gray-400 mt-1">Generated</div>
        </div>
        
        <div className="bg-white rounded-lg p-4 shadow-sm border border-gray-100">
          <div className="text-sm text-gray-500 mb-1">Total Tokens</div>
          <div className="text-2xl font-bold text-purple-600">
            {stats.totalTokens?.toLocaleString() || 0}
          </div>
          <div className="text-xs text-gray-400 mt-1">Combined</div>
        </div>
      </div>

      {/* Secondary Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        <div className="bg-white rounded-lg p-3 shadow-sm border border-gray-100">
          <div className="text-xs text-gray-500 mb-1">Paragraphs</div>
          <div className="text-lg font-semibold text-gray-700">
            {stats.paragraphCount || 0}
          </div>
        </div>
        
        <div className="bg-white rounded-lg p-3 shadow-sm border border-gray-100">
          <div className="text-xs text-gray-500 mb-1">Efficiency Ratio</div>
          <div className="text-lg font-semibold text-gray-700">
            {efficiency}x
          </div>
        </div>
        
        <div className="bg-white rounded-lg p-3 shadow-sm border border-gray-100">
          <div className="text-xs text-gray-500 mb-1">Words</div>
          <div className="text-lg font-semibold text-gray-700">
            {stats.translatedText ? stats.translatedText.split(' ').filter(w => w).length.toLocaleString() : 0}
          </div>
        </div>
      </div>
    </div>
  )
}

