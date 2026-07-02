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
