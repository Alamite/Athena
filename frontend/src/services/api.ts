import axios from 'axios'

const client = axios.create({ baseURL: '/api' })

export interface ChatRequest {
  question: string
}

export interface Citation {
  document: string
  chunk: number
}

export interface RetrievedChunk {
  document: string
  chunk: number
  score: number
  content: string
}

export interface ChatResponse {
  answer: string
  citations: Citation[]
  retrieved_chunks: RetrievedChunk[]
}

export interface DocumentInfo {
  name: string
  chunks: number
}

export interface UploadResponse {
  message: string
  filename: string
  chunks_created: number
}

export const askQuestion = (question: string): Promise<ChatResponse> =>
  client.post<ChatResponse>('/chat', { question }).then((r) => r.data)

export interface PipelineEvent {
  step: string
  status: 'start' | 'done' | 'error'
  message?: string
  data?: unknown
}

export const askQuestionStream = async (
  question: string,
  onEvent: (event: PipelineEvent) => void,
): Promise<ChatResponse> => {
  const response = await fetch('/api/chat/stream', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question }),
  })

  if (!response.ok || !response.body) {
    let detail = `Request failed with status ${response.status}`
    try {
      const body = await response.json()
      detail = body.detail ?? detail
    } catch {
      // response wasn't JSON; keep default detail
    }
    throw new Error(detail)
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''
  let finalResult: ChatResponse | null = null

  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })

    const messages = buffer.split('\n\n')
    buffer = messages.pop() ?? ''

    for (const message of messages) {
      const line = message.trim()
      if (!line.startsWith('data:')) continue

      const jsonStr = line.slice('data:'.length).trim()
      if (!jsonStr) continue

      const event = JSON.parse(jsonStr) as PipelineEvent & { data?: ChatResponse }

      if (event.step === 'error') {
        throw new Error(event.message ?? 'RAG pipeline failed')
      }
      if (event.step === 'final') {
        finalResult = event.data as ChatResponse
      } else {
        onEvent(event)
      }
    }
  }

  if (!finalResult) {
    throw new Error('Stream ended without a final response')
  }

  return finalResult
}

export const uploadDocument = (file: File): Promise<UploadResponse> => {
  const form = new FormData()
  form.append('file', file)
  return client
    .post<UploadResponse>('/documents/upload', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    .then((r) => r.data)
}

export const listDocuments = (): Promise<DocumentInfo[]> =>
  client.get<DocumentInfo[]>('/documents').then((r) => r.data)
