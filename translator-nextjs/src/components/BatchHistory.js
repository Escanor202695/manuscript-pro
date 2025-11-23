'use client'

export default function BatchHistory({ logs }) {
  if (!logs || logs.length === 0) return null

  const batches = []
  let currentBatch = null

  logs.forEach(log => {
    const batchMatch = log.match(/\[BATCH (\d+)\/(\d+)\] Processing (\d+) paragraphs/)
    if (batchMatch) {
      if (currentBatch) {
        batches.push(currentBatch)
      }
      currentBatch = {
        batchNum: parseInt(batchMatch[1]),
        totalBatches: parseInt(batchMatch[2]),
        paragraphs: parseInt(batchMatch[3]),
        inputTokens: 0,
        outputTokens: 0,
        totalTokens: 0,
        status: 'processing'
      }
    }
    
    const tokenMatch = log.match(/\[TOKENS\] Input: (\d+), Output: (\d+), Total: (\d+)/)
    if (tokenMatch && currentBatch) {
      currentBatch.inputTokens = parseInt(tokenMatch[1])
      currentBatch.outputTokens = parseInt(tokenMatch[2])
      currentBatch.totalTokens = parseInt(tokenMatch[3])
      currentBatch.status = 'completed'
    }
  })
  
  if (currentBatch) {
    batches.push(currentBatch)
  }

  if (batches.length === 0) return null

  return (
    <div className="mt-6">
      <h4 className="font-bold text-gray-800 mb-3 flex items-center gap-2">
        <span className="text-xl">📈</span>
        Batch Processing History
      </h4>
      
      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gradient-to-r from-purple-100 to-blue-100">
              <tr>
                <th className="px-4 py-3 text-left font-bold text-gray-700">Batch</th>
                <th className="px-4 py-3 text-left font-bold text-gray-700">Paragraphs</th>
                <th className="px-4 py-3 text-right font-bold text-gray-700">Input</th>
                <th className="px-4 py-3 text-right font-bold text-gray-700">Output</th>
                <th className="px-4 py-3 text-right font-bold text-gray-700">Total</th>
                <th className="px-4 py-3 text-center font-bold text-gray-700">Status</th>
              </tr>
            </thead>
            <tbody>
              {batches.map((batch, idx) => (
                <tr 
                  key={idx}
                  className={`border-t border-gray-200 ${idx % 2 === 0 ? 'bg-gray-50' : 'bg-white'} hover:bg-blue-50 transition`}
                >
                  <td className="px-4 py-3 font-semibold text-gray-700">
                    #{batch.batchNum}
                  </td>
                  <td className="px-4 py-3 text-gray-600">
                    {batch.paragraphs}
                  </td>
                  <td className="px-4 py-3 text-right text-blue-600 font-mono">
                    {batch.inputTokens.toLocaleString()}
                  </td>
                  <td className="px-4 py-3 text-right text-green-600 font-mono">
                    {batch.outputTokens.toLocaleString()}
                  </td>
                  <td className="px-4 py-3 text-right text-purple-600 font-mono font-semibold">
                    {batch.totalTokens.toLocaleString()}
                  </td>
                  <td className="px-4 py-3 text-center">
                    {batch.status === 'completed' ? (
                      <span className="inline-block bg-green-100 text-green-700 px-2 py-1 rounded-full text-xs font-semibold">
                        ✓ Done
                      </span>
                    ) : (
                      <span className="inline-block bg-yellow-100 text-yellow-700 px-2 py-1 rounded-full text-xs font-semibold">
                        ⏳ Processing
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
            <tfoot className="bg-gradient-to-r from-purple-50 to-blue-50 border-t-2 border-purple-200">
              <tr>
                <td className="px-4 py-3 font-bold text-gray-800" colSpan="2">
                  Total ({batches.length} batches)
                </td>
                <td className="px-4 py-3 text-right font-bold text-blue-700">
                  {batches.reduce((sum, b) => sum + b.inputTokens, 0).toLocaleString()}
                </td>
                <td className="px-4 py-3 text-right font-bold text-green-700">
                  {batches.reduce((sum, b) => sum + b.outputTokens, 0).toLocaleString()}
                </td>
                <td className="px-4 py-3 text-right font-bold text-purple-700">
                  {batches.reduce((sum, b) => sum + b.totalTokens, 0).toLocaleString()}
                </td>
                <td className="px-4 py-3"></td>
              </tr>
            </tfoot>
          </table>
        </div>
      </div>
    </div>
  )
}

