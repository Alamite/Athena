export type RetrievalType = 'similarity' | 'bm25' | 'hybrid_search'

export interface Source {
  source: string | null
  page: number | null
}

export interface PipelineStep {
  id: string
  label: string
  status: 'running' | 'done' | 'error'
  duration_ms?: number
  detail?: string | null
}

export interface RetrievedChunk {
  rank: number
  content: string
  metadata: Record<string, unknown>
}

export interface ChatResult {
  response: string
  sources: Source[]
  chunks: RetrievedChunk[]
  steps: PipelineStep[]
  /** Client-measured round-trip time in seconds. */
  elapsed: number
}

/** Thrown when the pipeline fails mid-stream; carries the steps completed so far. */
export class PipelineError extends Error {
  steps: PipelineStep[]
  constructor(message: string, steps: PipelineStep[]) {
    super(message)
    this.steps = steps
  }
}

export interface UploadResponse {
  message: string
  document_id: string
  filename: string
  total_pages: number
  total_chunks: number
  chunk_size: number
  chunk_overlap: number
}

const BASE = import.meta.env.VITE_API_URL ?? '/api'

async function handle<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let detail = `${res.status} ${res.statusText}`
    try {
      const body = await res.json()
      if (typeof body.detail === 'string') detail = body.detail
      else if (Array.isArray(body.detail)) detail = body.detail.map((d: { msg: string }) => d.msg).join(', ')
    } catch {
      /* non-JSON error body */
    }
    throw new Error(detail)
  }
  return res.json() as Promise<T>
}

function upsertStep(steps: PipelineStep[], step: PipelineStep): PipelineStep[] {
  const i = steps.findIndex((s) => s.id === step.id)
  if (i === -1) return [...steps, step]
  const next = steps.slice()
  next[i] = step
  return next
}

type StreamEvent =
  | ({ type: 'step' } & PipelineStep)
  | { type: 'result'; response: string; sources: Source[]; chunks: RetrievedChunk[] }
  | { type: 'error'; detail: string }

/**
 * POST /chat/stream — reads newline-delimited JSON events, reporting pipeline
 * progress through `onSteps` and resolving with the final answer.
 */
export async function streamChat(
  req: { message: string; retrieval_type: RetrievalType; k: number; use_reranker: boolean },
  onSteps: (steps: PipelineStep[]) => void,
  signal?: AbortSignal,
): Promise<ChatResult> {
  const started = performance.now()
  const res = await fetch(`${BASE}/chat/stream`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req),
    signal,
  })
  if (!res.ok || !res.body) await handle(res)

  let steps: PipelineStep[] = []
  const reader = res.body!.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  for (;;) {
    const { value, done } = await reader.read()
    if (value) buffer += decoder.decode(value, { stream: true })
    const lines = buffer.split('\n')
    buffer = done ? '' : lines.pop()!

    for (const line of lines) {
      if (!line.trim()) continue
      const event = JSON.parse(line) as StreamEvent
      if (event.type === 'step') {
        const { type: _type, ...step } = event
        void _type
        steps = upsertStep(steps, step)
        onSteps(steps)
      } else if (event.type === 'result') {
        return {
          response: event.response,
          sources: event.sources,
          chunks: event.chunks,
          steps,
          elapsed: (performance.now() - started) / 1000,
        }
      } else if (event.type === 'error') {
        throw new PipelineError(event.detail, steps)
      }
    }
    if (done) break
  }
  throw new PipelineError('Stream ended without a result.', steps)
}

export async function uploadDocument(file: File, chunkSize: number, chunkOverlap: number): Promise<UploadResponse> {
  const form = new FormData()
  form.append('file', file)
  form.append('chunk_size', String(chunkSize))
  form.append('chunk_overlap', String(chunkOverlap))
  const res = await fetch(`${BASE}/documents/upload`, { method: 'POST', body: form })
  return handle<UploadResponse>(res)
}
