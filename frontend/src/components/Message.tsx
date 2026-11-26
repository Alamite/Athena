import { useState } from 'react'
import type { PipelineStep, RetrievedChunk, Source } from '../api'
import { Avatar } from './Avatar'

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  sources?: Source[]
  error?: boolean
  /** Assistant: the question this answers (used for retry and the inspector). */
  question?: string
  /** Assistant: retrieval settings used, e.g. "Hybrid + rerank · k=3". */
  config?: string
  elapsed?: number
  steps?: PipelineStep[]
  chunks?: RetrievedChunk[]
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
  onInspect?: () => void
  busy?: boolean
}

export function Message({ message, onRetry, onRepeat, onInspect, busy }: MessageProps) {
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
      <Avatar />
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
          {onInspect && !!message.steps?.length && (
            <button onClick={onInspect} title="Show pipeline steps and retrieved chunks">
              Inspect
            </button>
          )}
          {!message.error && message.config && (
            <span className="meta">
              {message.config}
              {message.elapsed != null && ` · ${message.elapsed.toFixed(1)}s`}
            </span>
          )}
        </div>
      </div>
    </div>
  )
}
