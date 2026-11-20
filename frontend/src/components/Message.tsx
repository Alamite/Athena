import { useState } from 'react'
import type { Source } from '../api'

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  sources?: Source[]
  error?: boolean
  meta?: string
}

function dedupeSources(sources: Source[]) {
  const seen = new Set<string>()
  return sources.filter((s) => {
    const key = `${s.source}|${s.page}`
    if (seen.has(key)) return false
    seen.add(key)
    return true
  })
}

function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false)
  return (
    <button
      title="Copy"
      onClick={() => {
        navigator.clipboard.writeText(text)
        setCopied(true)
        setTimeout(() => setCopied(false), 1500)
      }}
    >
      {copied ? 'Copied' : 'Copy'}
    </button>
  )
}

interface MessageProps {
  message: ChatMessage
  onRetry?: () => void
  /** User messages: resend the same question. */
  onRepeat?: () => void
  busy?: boolean
}

export function Message({ message, onRetry, onRepeat, busy }: MessageProps) {
  const sources = message.sources ? dedupeSources(message.sources) : []

  if (message.role === 'user') {
    return (
      <div className="msg user">
        <div className="bubble">{message.content}</div>
        <div className="actions user-actions">
          {onRepeat && (
            <button onClick={onRepeat} disabled={busy} title="Ask this question again">
              Ask again
            </button>
          )}
          <CopyButton text={message.content} />
        </div>
      </div>
    )
  }

  return (
    <div className={`msg assistant ${message.error ? 'error' : ''}`}>
      <div className="avatar">A</div>
      <div className="body">
        <div className="content">{message.content}</div>

        {sources.length > 0 && (
          <div className="sources">
            <span className="sources-label">Sources</span>
            {sources.map((s, i) => (
              <span key={i} className="chip" title={s.source ?? undefined}>
                {s.source ?? 'Unknown'}
                {s.page != null && <span className="chip-page">p. {s.page}</span>}
              </span>
            ))}
          </div>
        )}

        <div className="actions">
          {message.error && onRetry ? (
            <button onClick={onRetry}>Retry</button>
          ) : (
            <CopyButton text={message.content} />
          )}
          {message.meta && <span className="meta">{message.meta}</span>}
        </div>
      </div>
    </div>
  )
}

export function Thinking() {
  return (
    <div className="msg assistant">
      <div className="avatar">A</div>
      <div className="body">
        <div className="typing">
          <span />
          <span />
          <span />
        </div>
      </div>
    </div>
  )
}
