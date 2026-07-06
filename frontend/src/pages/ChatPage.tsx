import { useCallback, useEffect, useState } from 'react'
import ChatWindow, { type Message } from '../components/ChatWindow'
import FileUploader from '../components/FileUploader'
import RetrievalPanel from '../components/RetrievalPanel'
import {
  askQuestionStream,
  listDocuments,
  type DocumentInfo,
  type PipelineEvent,
  type RetrievedChunk,
} from '../services/api'

let messageIdCounter = 0
const nextId = () => String(++messageIdCounter)

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [documents, setDocuments] = useState<DocumentInfo[]>([])
  const [retrievedChunks, setRetrievedChunks] = useState<RetrievedChunk[]>([])
  const [error, setError] = useState<string | null>(null)
  const [liveTrace, setLiveTrace] = useState<PipelineEvent[]>([])

  const fetchDocuments = useCallback(async () => {
    try {
      const docs = await listDocuments()
      setDocuments(docs)
    } catch {
      // Non-critical; silent fail
    }
  }, [])

  useEffect(() => {
    fetchDocuments()
  }, [fetchDocuments])

  const handleSubmit = useCallback(async () => {
    const question = input.trim()
    if (!question || isLoading) return

    setInput('')
    setError(null)
    setIsLoading(true)
    setLiveTrace([])

    setMessages((prev) => [
      ...prev,
      { id: nextId(), role: 'user', content: question },
    ])

    const trace: PipelineEvent[] = []

    try {
      const result = await askQuestionStream(question, (event) => {
        trace.push(event)
        setLiveTrace([...trace])
      })

      setMessages((prev) => [
        ...prev,
        {
          id: nextId(),
          role: 'assistant',
          content: result.answer,
          citations: result.citations,
          trace,
        },
      ])

      setRetrievedChunks(result.retrieved_chunks)
    } catch (err: unknown) {
      const detail =
        err instanceof Error ? err.message : 'An unexpected error occurred'
      setError(detail)
      setMessages((prev) => [
        ...prev,
        {
          id: nextId(),
          role: 'assistant',
          content: 'Sorry, something went wrong. Please try again.',
          trace,
        },
      ])
    } finally {
      setIsLoading(false)
      setLiveTrace([])
    }
  }, [input, isLoading])

  return (
    <div className="flex flex-col h-screen bg-gray-950 text-gray-100">
      {/* Header */}
      <header className="flex-shrink-0 flex items-center justify-between px-5 py-3 border-b border-gray-800 bg-gray-900/80 backdrop-blur-sm">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-xl bg-blue-600 flex items-center justify-center">
            {/* Minimal owl */}
            <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none">
              {/* Head */}
              <path d="M12 4C8.5 4 6 7 6 10.5V15a6 6 0 0012 0v-4.5C18 7 15.5 4 12 4z" fill="white" fillOpacity="0.15"/>
              {/* Ear tufts */}
              <path d="M9.5 4L8 1.5" stroke="white" strokeWidth="1.5" strokeLinecap="round"/>
              <path d="M14.5 4L16 1.5" stroke="white" strokeWidth="1.5" strokeLinecap="round"/>
              {/* Left eye */}
              <circle cx="9.5" cy="11" r="2.6" fill="white"/>
              {/* Right eye */}
              <circle cx="14.5" cy="11" r="2.6" fill="white"/>
              {/* Pupils */}
              <circle cx="9.5" cy="11" r="1.2" fill="#1e40af"/>
              <circle cx="14.5" cy="11" r="1.2" fill="#1e40af"/>
              {/* Beak */}
              <path d="M11 14.5L12 16.5L13 14.5H11Z" fill="white" fillOpacity="0.85"/>
            </svg>
          </div>
          <span className="font-semibold text-gray-100 tracking-tight">Athena</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          <span className="text-xs text-gray-400">RAG · Hybrid Retrieval · Reranking</span>
        </div>
      </header>

      {/* Upload bar */}
      <div className="flex-shrink-0 bg-gray-900/50 border-b border-gray-800 px-5 py-4">
        <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">
          Upload Markdown Files
        </p>
        <FileUploader documents={documents} onUploadSuccess={fetchDocuments} />
      </div>

      {error && (
        <div className="flex-shrink-0 mx-5 mt-3 px-4 py-2.5 rounded-lg bg-red-950/50 border border-red-800 text-sm text-red-300">
          {error}
        </div>
      )}

      {/* Main two-column area */}
      <div className="flex flex-1 min-h-0">
        {/* Left — Chat */}
        <div className="flex flex-col flex-1 min-w-0 border-r border-gray-800">
          <ChatWindow
            messages={messages}
            isLoading={isLoading}
            liveTrace={liveTrace}
            input={input}
            onInputChange={setInput}
            onSubmit={handleSubmit}
          />
        </div>

        {/* Right — Retrieval Inspector */}
        <div className="w-[380px] flex-shrink-0 bg-gray-900/30">
          <RetrievalPanel chunks={retrievedChunks} />
        </div>
      </div>
    </div>
  )
}
