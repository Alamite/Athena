export type RetrievalType = 'similarity' | 'bm25' | 'hybrid_search'

export interface Source {
  source: string | null
  page: number | null
}

export interface ChatResponse {
  response: string
  sources: Source[]
  /** Client-measured round-trip time in seconds. */
  elapsed: number
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

export async function sendMessage(
  message: string,
  retrieval_type: RetrievalType,
  k: number,
  use_reranker: boolean,
  signal?: AbortSignal,
): Promise<ChatResponse> {
  const started = performance.now()
  const res = await fetch(`${BASE}/chat/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, retrieval_type, k, use_reranker }),
    signal,
  })
  const data = await handle<Omit<ChatResponse, 'elapsed'>>(res)
  return { ...data, elapsed: (performance.now() - started) / 1000 }
}

export async function uploadDocument(file: File, chunkSize: number, chunkOverlap: number): Promise<UploadResponse> {
  const form = new FormData()
  form.append('file', file)
  form.append('chunk_size', String(chunkSize))
  form.append('chunk_overlap', String(chunkOverlap))
  const res = await fetch(`${BASE}/documents/upload`, { method: 'POST', body: form })
  return handle<UploadResponse>(res)
}
