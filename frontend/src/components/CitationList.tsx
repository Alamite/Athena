import type { Citation } from '../services/api'

interface Props {
  citations: Citation[]
}

export default function CitationList({ citations }: Props) {
  if (citations.length === 0) return null

  return (
    <div className="mt-3 pt-3 border-t border-gray-700">
      <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">
        Sources
      </p>
      <ul className="space-y-1">
        {citations.map((c, i) => (
          <li key={i} className="flex items-center gap-2 text-xs text-gray-400">
            <span className="flex-shrink-0 w-5 h-5 rounded-full bg-blue-900 text-blue-300 flex items-center justify-center font-mono font-bold text-[10px]">
              {i + 1}
            </span>
            <span>
              <span className="text-gray-200 font-medium">{c.document}</span>
              <span className="text-gray-500"> · chunk {c.chunk}</span>
            </span>
          </li>
        ))}
      </ul>
    </div>
  )
}
