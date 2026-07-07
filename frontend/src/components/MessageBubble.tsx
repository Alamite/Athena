import type { Citation, PipelineEvent } from '../services/api'
import CitationList from './CitationList'
import PipelineTrace from './PipelineTrace'

interface Props {
  role: 'user' | 'assistant'
  content: string
  citations?: Citation[]
  trace?: PipelineEvent[]
}

export default function MessageBubble({ role, content, citations, trace }: Props) {
  const isUser = role === 'user'

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${
          isUser
            ? 'bg-blue-600 text-white rounded-br-sm'
            : 'bg-gray-800 text-gray-100 rounded-bl-sm'
        }`}
      >
        {!isUser && (
          <p className="text-[10px] font-semibold text-gray-500 uppercase tracking-widest mb-1">
            Athena
          </p>
        )}
        {!isUser && trace && trace.length > 0 && <PipelineTrace events={trace} />}
        {content && <p className="whitespace-pre-wrap">{content}</p>}
        {!isUser && citations && <CitationList citations={citations} />}
      </div>
    </div>
  )
}
