import { useEffect, useState } from 'react'
import type { RetrievedChunk } from '../api'
import type { ChatMessage } from './Message'
import { formatMs } from '../format'
import { StepList } from './PipelineSteps'

const HIDDEN_FROM_BADGES = new Set(['vector_rank', 'vector_distance', 'bm25_rank', 'rrf_score', 'reranker_score'])

function num(v: unknown, digits: number) {
  return typeof v === 'number' ? v.toFixed(digits) : null
}

function ScoreBadges({ meta }: { meta: Record<string, unknown> }) {
  const badges: { label: string; value: string; title: string }[] = []
  if (meta.vector_rank != null)
    badges.push({
      label: 'Vector',
      value: `#${meta.vector_rank}${meta.vector_distance != null ? ` · d ${num(meta.vector_distance, 3)}` : ''}`,
      title: 'Rank in vector search · embedding distance (lower is closer)',
    })
  if (meta.bm25_rank != null) badges.push({ label: 'BM25', value: `#${meta.bm25_rank}`, title: 'Rank in BM25 keyword search' })
  if (meta.rrf_score != null) badges.push({ label: 'RRF', value: num(meta.rrf_score, 4)!, title: 'Reciprocal rank fusion score' })
  if (meta.reranker_score != null)
    badges.push({ label: 'Rerank', value: num(meta.reranker_score, 4)!, title: 'Cross-encoder relevance score (higher is better)' })
  if (!badges.length) return null
  return (
    <div className="badges">
      {badges.map((b) => (
        <span key={b.label} className="score" title={b.title}>
          <span>{b.label}</span>
          {b.value}
        </span>
      ))}
    </div>
  )
}

function ChunkCard({ chunk }: { chunk: RetrievedChunk }) {
  const [expanded, setExpanded] = useState(false)
  const [showMeta, setShowMeta] = useState(false)
  const m = chunk.metadata
  const file = (m.filename as string) ?? (m.source as string) ?? 'Unknown source'
  const page = typeof m.page === 'number' ? m.page + 1 : null
  const long = chunk.content.length > 420

  return (
    <article className="chunk">
      <header>
        <span className="chunk-rank">#{chunk.rank}</span>
        <span className="chunk-src" title={file}>
          {file}
        </span>
        {page != null && <span className="chunk-page">p. {page}</span>}
      </header>
      <ScoreBadges meta={m} />
      <p className={`chunk-text ${expanded || !long ? '' : 'clamped'}`}>{chunk.content}</p>
      <div className="chunk-actions">
        {long && <button onClick={() => setExpanded((v) => !v)}>{expanded ? 'Show less' : 'Show full chunk'}</button>}
        <button onClick={() => setShowMeta((v) => !v)}>{showMeta ? 'Hide metadata' : 'Metadata'}</button>
        <span className="meta">{chunk.content.length.toLocaleString()} chars</span>
      </div>
      {showMeta && (
        <dl className="meta-table">
          {Object.entries(m)
            .sort(([a], [b]) => Number(HIDDEN_FROM_BADGES.has(a)) - Number(HIDDEN_FROM_BADGES.has(b)) || a.localeCompare(b))
            .map(([key, value]) => (
              <div key={key}>
                <dt>{key}</dt>
                <dd title={String(value)}>{typeof value === 'object' ? JSON.stringify(value) : String(value)}</dd>
              </div>
            ))}
        </dl>
      )}
    </article>
  )
}

export function Inspector({ message, onClose }: { message: ChatMessage | null; onClose: () => void }) {
  useEffect(() => {
    if (!message) return
    const onKey = (e: KeyboardEvent) => e.key === 'Escape' && onClose()
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [message, onClose])

  const steps = message?.steps ?? []
  const chunks = message?.chunks ?? []
  const total = steps.reduce((t, s) => t + (s.duration_ms ?? 0), 0)

  return (
    <>
      <div className={`scrim inspector-scrim ${message ? 'show' : ''}`} onClick={onClose} />
      <aside className={`inspector ${message ? 'open' : ''}`} aria-hidden={!message} aria-label="Answer inspector">
        {message && (
          <>
            <header className="inspector-head">
              <div>
                <h2>Inspector</h2>
                {message.question && <p className="inspector-q">“{message.question}”</p>}
              </div>
              <button className="rail-btn" onClick={onClose} aria-label="Close inspector" title="Close (Esc)">
                ✕
              </button>
            </header>

            <div className="inspector-body">
              {message.config && (
                <div className="inspector-summary">
                  <span>{message.config}</span>
                  {total > 0 && <span>Backend {formatMs(total)}</span>}
                </div>
              )}

              <section>
                <h3>Pipeline</h3>
                {steps.length ? <StepList steps={steps} showBars /> : <p className="hint">No steps recorded.</p>}
              </section>

              <section>
                <h3>
                  Retrieved chunks <span className="count">{chunks.length}</span>
                </h3>
                {chunks.length ? (
                  <div className="chunks">
                    {chunks.map((c) => (
                      <ChunkCard key={c.rank} chunk={c} />
                    ))}
                  </div>
                ) : (
                  <p className="hint">No chunks were returned.</p>
                )}
              </section>
            </div>
          </>
        )}
      </aside>
    </>
  )
}
