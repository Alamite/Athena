import type { RetrievedChunk } from '../services/api'

interface Props {
  chunks: RetrievedChunk[]
}

export default function RetrievalPanel({ chunks }: Props) {
  return (
    <div className="flex flex-col h-full">
      <div className="px-4 py-3 border-b border-gray-700">
        <h2 className="text-sm font-semibold text-gray-200">Retrieval Inspector</h2>
        <p className="text-xs text-gray-500 mt-0.5">
          {chunks.length > 0
            ? `${chunks.length} chunk${chunks.length !== 1 ? 's' : ''} retrieved`
            : 'Ask a question to see retrieved chunks'}
        </p>
      </div>

      <div className="flex-1 overflow-y-auto p-3 space-y-3">
        {chunks.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center py-16">
            <div className="w-12 h-12 rounded-full bg-gray-800 flex items-center justify-center mb-3">
              <svg
                className="w-6 h-6 text-gray-600"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={1.5}
                  d="M21 21l-4.35-4.35M17 11A6 6 0 111 11a6 6 0 0116 0z"
                />
              </svg>
            </div>
            <p className="text-sm text-gray-500">No results yet</p>
            <p className="text-xs text-gray-600 mt-1">
              Retrieved chunks will appear here
            </p>
          </div>
        ) : (
          chunks.map((chunk, i) => (
            <div
              key={i}
              className="bg-gray-800 rounded-xl p-3 border border-gray-700 space-y-2"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="text-[10px] font-bold text-gray-400 uppercase tracking-wider">
                    #{i + 1}
                  </span>
                  <span className="inline-flex items-center px-2 py-0.5 rounded-md bg-violet-900/60 text-violet-300 text-[11px] font-medium">
                    {chunk.document}
                  </span>
                  <span className="inline-flex items-center px-2 py-0.5 rounded-md bg-gray-700 text-gray-300 text-[11px]">
                    chunk {chunk.chunk}
                  </span>
                </div>
                <span className="inline-flex items-center px-2 py-0.5 rounded-md bg-emerald-900/60 text-emerald-300 text-[11px] font-mono font-semibold flex-shrink-0">
                  {chunk.score.toFixed(2)}
                </span>
              </div>
              <p className="text-xs text-gray-300 leading-relaxed font-mono bg-gray-900 rounded-lg p-2 border border-gray-700/50 whitespace-pre-wrap break-words">
                {chunk.content}
              </p>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
