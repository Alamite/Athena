import { useEffect, useRef, useState, type ReactNode } from 'react'
import { uploadDocument, type RetrievalType, type UploadResponse } from '../api'

const RETRIEVAL_OPTIONS: { value: RetrievalType; label: string; hint: string }[] = [
  { value: 'similarity', label: 'Vector', hint: 'Semantic similarity via embeddings' },
  { value: 'bm25', label: 'BM25', hint: 'Keyword matching' },
  { value: 'hybrid_search', label: 'Hybrid', hint: 'Vector + BM25 fused with RRF' },
]

type Tab = 'ingestion' | 'retrieval' | 'evaluation'

const svg = (d: ReactNode) => (
  <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="1.8"
    strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
    {d}
  </svg>
)

const ICONS: Record<Tab | 'collapse' | 'expand', ReactNode> = {
  ingestion: svg(<><path d="M12 16V4" /><path d="m7 9 5-5 5 5" /><path d="M4 16v3a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1v-3" /></>),
  retrieval: svg(<><circle cx="11" cy="11" r="6.5" /><path d="m20 20-4.2-4.2" /></>),
  evaluation: svg(<><path d="M4 20V10" /><path d="M10 20V4" /><path d="M16 20v-7" /><path d="M22 20H2" /></>),
  collapse: svg(<><rect x="3" y="4" width="18" height="16" rx="2" /><path d="M9 4v16" /><path d="m15 10-2 2 2 2" /></>),
  expand: svg(<><rect x="3" y="4" width="18" height="16" rx="2" /><path d="M9 4v16" /><path d="m13 10 2 2-2 2" /></>),
}

const TABS: { id: Tab; label: string }[] = [
  { id: 'ingestion', label: 'Ingestion' },
  { id: 'retrieval', label: 'Retrieval' },
  { id: 'evaluation', label: 'Evaluation' },
]

function loadPref<T extends string>(key: string, fallback: T, allowed: readonly T[]): T {
  try {
    const v = localStorage.getItem(key) as T | null
    return v && allowed.includes(v) ? v : fallback
  } catch {
    return fallback
  }
}
function savePref(key: string, value: string) {
  try {
    localStorage.setItem(key, value)
  } catch {
    /* storage unavailable */
  }
}

interface Props {
  retrievalType: RetrievalType
  onRetrievalTypeChange: (t: RetrievalType) => void
  k: number
  onKChange: (k: number) => void
  useReranker: boolean
  onUseRerankerChange: (v: boolean) => void
  documents: UploadResponse[]
  onUploaded: (doc: UploadResponse) => void
  /** Mobile drawer visibility. */
  open: boolean
  onClose: () => void
}

export function Sidebar(props: Props) {
  const { open, onClose } = props
  const [collapsed, setCollapsed] = useState(() => loadPref('athena.sidebar', 'open', ['open', 'collapsed'] as const) === 'collapsed')
  const [tab, setTab] = useState<Tab>(() => loadPref('athena.tab', 'ingestion', ['ingestion', 'retrieval', 'evaluation'] as const))

  useEffect(() => savePref('athena.sidebar', collapsed ? 'collapsed' : 'open'), [collapsed])
  useEffect(() => savePref('athena.tab', tab), [tab])

  const [chunkSize, setChunkSize] = useState(DEFAULT_CHUNK_SIZE)
  const [chunkOverlap, setChunkOverlap] = useState(DEFAULT_CHUNK_OVERLAP)

  return (
    <>
      <div className={`scrim ${open ? 'show' : ''}`} onClick={onClose} />
      <aside className={`sidebar ${open ? 'open' : ''} ${collapsed ? 'collapsed' : ''}`}>
        {/* Collapsed rail (desktop only) */}
        <div className="rail">
          <button className="rail-btn" onClick={() => setCollapsed(false)} title="Expand panel" aria-label="Expand panel">
            {ICONS.expand}
          </button>
          <div className="rail-sep" />
          {TABS.map((t) => (
            <button
              key={t.id}
              className={`rail-btn ${tab === t.id ? 'active' : ''}`}
              title={t.label}
              aria-label={t.label}
              onClick={() => {
                setTab(t.id)
                setCollapsed(false)
              }}
            >
              {ICONS[t.id]}
            </button>
          ))}
        </div>

        {/* Expanded panel */}
        <div className="panel">
          <div className="panel-head">
            <div className="brand">
              <span className="brand-mark">A</span>
              <span>Athena</span>
            </div>
            <button className="rail-btn collapse-btn" onClick={() => setCollapsed(true)} title="Collapse panel" aria-label="Collapse panel">
              {ICONS.collapse}
            </button>
          </div>

          <div className="tabs" role="tablist">
            {TABS.map((t) => (
              <button
                key={t.id}
                role="tab"
                aria-selected={tab === t.id}
                className={tab === t.id ? 'active' : ''}
                onClick={() => setTab(t.id)}
              >
                {ICONS[t.id]}
                <span>{t.label}</span>
              </button>
            ))}
          </div>

          <div className="tab-body" role="tabpanel">
            {tab === 'ingestion' && (
              <IngestionTab
                {...props}
                chunkSize={chunkSize}
                chunkOverlap={chunkOverlap}
                onChunkSizeChange={setChunkSize}
                onChunkOverlapChange={setChunkOverlap}
              />
            )}
            {tab === 'retrieval' && <RetrievalTab {...props} />}
            {tab === 'evaluation' && <EvaluationTab />}
          </div>
        </div>
      </aside>
    </>
  )
}

/** Documents shipped with the app and indexed in Chroma ahead of time. PDFs live in frontend/public. */
const PREINDEXED_DOCS = [
  { filename: 'iphone user guide.pdf', title: 'iPhone User Guide', pages: 217, href: '/data/iphone%20user%20guide.pdf' },
]

const DOWNLOAD_ICON = (
  <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="1.9"
    strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
    <path d="M12 4v11" /><path d="m7 10 5 5 5-5" /><path d="M5 20h14" />
  </svg>
)

const DEFAULT_CHUNK_SIZE = 1000
const DEFAULT_CHUNK_OVERLAP = 150
// Mirrors the backend's Form validation (ge=100, le=5000, ge=0).
const CHUNK_MIN = 100
const CHUNK_MAX = 5000

interface IngestionProps extends Props {
  chunkSize: number
  chunkOverlap: number
  onChunkSizeChange: (v: number) => void
  onChunkOverlapChange: (v: number) => void
}

function chunkError(size: number, overlap: number): string | null {
  if (!Number.isInteger(size) || size < CHUNK_MIN || size > CHUNK_MAX)
    return `Chunk size must be between ${CHUNK_MIN} and ${CHUNK_MAX}.`
  if (!Number.isInteger(overlap) || overlap < 0) return 'Overlap must be 0 or more.'
  if (overlap >= size) return 'Overlap must be smaller than chunk size.'
  return null
}

function IngestionTab({
  documents,
  onUploaded,
  chunkSize,
  chunkOverlap,
  onChunkSizeChange,
  onChunkOverlapChange,
}: IngestionProps) {
  const invalid = chunkError(chunkSize, chunkOverlap)
  const inputRef = useRef<HTMLInputElement>(null)
  const [uploading, setUploading] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [dragOver, setDragOver] = useState(false)

  async function handleFiles(files: FileList | null) {
    if (!files?.length) return
    if (invalid) {
      setError(invalid)
      return
    }
    setError(null)
    for (const file of Array.from(files)) {
      if (!file.name.toLowerCase().endsWith('.pdf')) {
        setError(`${file.name}: only PDF files are supported.`)
        continue
      }
      setUploading(file.name)
      try {
        onUploaded(await uploadDocument(file, chunkSize, chunkOverlap))
      } catch (e) {
        setError(`${file.name}: ${(e as Error).message}`)
      }
    }
    setUploading(null)
    if (inputRef.current) inputRef.current.value = ''
  }

  return (
    <section>
      <h2>Chunking</h2>
      <div className="field-row">
        <Stepper
          label="Chunk size"
          value={chunkSize}
          min={CHUNK_MIN}
          max={CHUNK_MAX}
          step={50}
          disabled={!!uploading}
          onChange={onChunkSizeChange}
        />
        <Stepper
          label="Overlap"
          value={chunkOverlap}
          min={0}
          max={Math.max(0, chunkSize - 1)}
          step={10}
          disabled={!!uploading}
          onChange={onChunkOverlapChange}
        />
      </div>
      {invalid ? (
        <p className="error-text">{invalid}</p>
      ) : (
        <p className="hint">Characters per chunk. Applied to the next upload.</p>
      )}
      {(chunkSize !== DEFAULT_CHUNK_SIZE || chunkOverlap !== DEFAULT_CHUNK_OVERLAP) && (
        <button
          className="link-btn"
          onClick={() => {
            onChunkSizeChange(DEFAULT_CHUNK_SIZE)
            onChunkOverlapChange(DEFAULT_CHUNK_OVERLAP)
          }}
        >
          Reset to defaults
        </button>
      )}

      <h2 className="spaced">Upload documents</h2>
      <div
        className={`dropzone ${dragOver ? 'over' : ''} ${uploading ? 'busy' : ''} ${invalid ? 'disabled' : ''}`}
        onClick={() => !uploading && !invalid && inputRef.current?.click()}
        onDragOver={(e) => {
          e.preventDefault()
          setDragOver(true)
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={(e) => {
          e.preventDefault()
          setDragOver(false)
          if (!uploading) handleFiles(e.dataTransfer.files)
        }}
      >
        {uploading ? (
          <>
            <span className="spinner" />
            <span>Indexing {uploading}…</span>
          </>
        ) : (
          <>
            <span className="dropzone-icon">{ICONS.ingestion}</span>
            <strong>Drop PDFs here</strong>
            <span>or click to browse</span>
          </>
        )}
        <input ref={inputRef} type="file" accept="application/pdf,.pdf" multiple hidden onChange={(e) => handleFiles(e.target.files)} />
      </div>
      {error && <p className="error-text">{error}</p>}

      <h2 className="spaced">Pre-indexed</h2>
      <ul className="doc-list">
        {PREINDEXED_DOCS.map((d) => (
          <li key={d.filename}>
            <span className="doc-icon">PDF</span>
            <div className="doc-info">
              <div className="doc-name" title={d.filename}>
                {d.title}
              </div>
              <div className="doc-meta">
                {d.pages} pages · <span className="tag">Default</span>
              </div>
            </div>
            <a className="doc-action" href={d.href} download={d.filename} title={`Download ${d.filename}`} aria-label={`Download ${d.title}`}>
              {DOWNLOAD_ICON}
            </a>
          </li>
        ))}
      </ul>

      {documents.length > 0 && (
        <>
          <h2 className="spaced">Indexed this session</h2>
          <ul className="doc-list">
            {documents.map((d) => (
              <li key={d.document_id}>
                <span className="doc-icon">PDF</span>
                <div>
                  <div className="doc-name" title={d.filename}>
                    {d.filename}
                  </div>
                  <div className="doc-meta">
                    {d.total_pages} pages · {d.total_chunks} chunks · {d.chunk_size}/{d.chunk_overlap}
                  </div>
                </div>
              </li>
            ))}
          </ul>
        </>
      )}
      <p className="hint">All indexed documents are searched together.</p>
    </section>
  )
}

interface StepperProps {
  label: string
  value: number
  min: number
  max: number
  step: number
  disabled?: boolean
  onChange: (v: number) => void
}

function Stepper({ label, value, min, max, step, disabled, onChange }: StepperProps) {
  const valid = Number.isFinite(value)
  const clamp = (v: number) => Math.min(max, Math.max(min, v))
  // Snap to the step grid so 1000 → 1050, 1023 → 1050 (up) / 1000 (down).
  const bump = (dir: 1 | -1) => {
    const base = valid ? value : min
    const snapped = dir > 0 ? Math.floor(base / step) * step + step : Math.ceil(base / step) * step - step
    onChange(clamp(snapped))
  }

  return (
    <div className="field">
      <span>{label}</span>
      <div className={`stepper ${disabled ? 'disabled' : ''}`}>
        <button type="button" aria-label={`Decrease ${label}`} disabled={disabled || (valid && value <= min)} onClick={() => bump(-1)}>
          −
        </button>
        <input
          type="text"
          inputMode="numeric"
          aria-label={label}
          value={valid ? value : ''}
          disabled={disabled}
          onChange={(e) => {
            const digits = e.target.value.replace(/\D/g, '')
            onChange(digits === '' ? NaN : Number(digits))
          }}
          onKeyDown={(e) => {
            if (e.key === 'ArrowUp') { e.preventDefault(); bump(1) }
            if (e.key === 'ArrowDown') { e.preventDefault(); bump(-1) }
          }}
        />
        <button type="button" aria-label={`Increase ${label}`} disabled={disabled || (valid && value >= max)} onClick={() => bump(1)}>
          +
        </button>
      </div>
    </div>
  )
}

function RetrievalTab({ retrievalType, onRetrievalTypeChange, k, onKChange, useReranker, onUseRerankerChange }: Props) {
  const rerankAvailable = retrievalType === 'hybrid_search'
  return (
    <section>
      <h2>Strategy</h2>
      <div className="option-list" role="radiogroup" aria-label="Retrieval type">
        {RETRIEVAL_OPTIONS.map((o) => (
          <button
            key={o.value}
            role="radio"
            aria-checked={retrievalType === o.value}
            className={`option ${retrievalType === o.value ? 'active' : ''}`}
            onClick={() => onRetrievalTypeChange(o.value)}
          >
            <span className="radio" />
            <span>
              <strong>{o.label}</strong>
              <small>{o.hint}</small>
            </span>
          </button>
        ))}
      </div>

      <h2 className="spaced">Top-k</h2>
      <label className="slider">
        <span>
          Chunks to retrieve <strong>{k}</strong>
        </span>
        <input type="range" min={1} max={10} value={k} onChange={(e) => onKChange(Number(e.target.value))} />
      </label>

      <h2 className="spaced">Reranking</h2>
      <label className={`checkbox ${rerankAvailable ? '' : 'disabled'}`}>
        <input
          type="checkbox"
          className="sr-only"
          checked={useReranker && rerankAvailable}
          disabled={!rerankAvailable}
          onChange={(e) => onUseRerankerChange(e.target.checked)}
        />
        <span className="checkmark" aria-hidden="true">
          <svg viewBox="0 0 16 16" width="12" height="12" fill="none" stroke="currentColor" strokeWidth="2.4"
            strokeLinecap="round" strokeLinejoin="round">
            <path d="m3.5 8.5 3 3 6-7" />
          </svg>
        </span>
        <span>
          <strong>Use cross-encoder reranker</strong>
          <small>
            {rerankAvailable
              ? 'Re-scores fused candidates with bge-reranker-base. Slower, usually more precise.'
              : 'Available with Hybrid retrieval only.'}
          </small>
        </span>
      </label>
    </section>
  )
}

function EvaluationTab() {
  return (
    <section className="coming-soon">
      <span className="coming-icon">{ICONS.evaluation}</span>
      <strong>Evaluation</strong>
      <span className="pill">Coming soon</span>
      <p className="hint">
        Compare retrieval strategies with Precision@k, Recall@k and MRR against a labelled query set.
      </p>
    </section>
  )
}
