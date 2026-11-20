import { useEffect, useRef, useState } from 'react'
import { sendMessage, type RetrievalType, type UploadResponse } from './api'
import { Message, Thinking, type ChatMessage } from './components/Message'
import { Sidebar } from './components/Sidebar'
import './App.css'

const LABELS: Record<RetrievalType, string> = {
  similarity: 'Vector',
  bm25: 'BM25',
  hybrid_search: 'Hybrid',
}

const SUGGESTIONS = [
  'Summarize the main points of the document',
  'What are the key definitions introduced?',
  'List any numbers or statistics mentioned',
]

const uid = () => Math.random().toString(36).slice(2)

export default function App() {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [retrievalType, setRetrievalType] = useState<RetrievalType>('hybrid_search')
  const [k, setK] = useState(3)
  const [useReranker, setUseReranker] = useState(false)
  const [documents, setDocuments] = useState<UploadResponse[]>([])
  const [sidebarOpen, setSidebarOpen] = useState(false)

  const scrollRef = useRef<HTMLDivElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const abortRef = useRef<AbortController | null>(null)

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' })
  }, [messages, loading])

  useEffect(() => {
    const el = textareaRef.current
    if (!el) return
    el.style.height = 'auto'
    el.style.height = `${Math.min(el.scrollHeight, 200)}px`
  }, [input])

  async function ask(question: string, replaceId?: string) {
    const q = question.trim()
    if (!q || loading) return

    if (!replaceId) {
      setMessages((m) => [...m, { id: uid(), role: 'user', content: q }])
      setInput('')
    } else {
      setMessages((m) => m.filter((x) => x.id !== replaceId))
    }

    setLoading(true)
    const controller = new AbortController()
    abortRef.current = controller
    const mode = retrievalType
    // The backend only applies the reranker to hybrid search.
    const rerank = useReranker && mode === 'hybrid_search'

    try {
      const res = await sendMessage(q, mode, k, rerank, controller.signal)
      setMessages((m) => [
        ...m,
        {
          id: uid(),
          role: 'assistant',
          content: res.response,
          sources: res.sources,
          meta: `${LABELS[mode]}${rerank ? ' + rerank' : ''} · k=${k} · ${res.elapsed.toFixed(1)}s`,
        },
      ])
    } catch (e) {
      const err = e as Error
      const aborted = err.name === 'AbortError'
      setMessages((m) => [
        ...m,
        {
          id: uid(),
          role: 'assistant',
          content: aborted ? 'Request cancelled.' : `Something went wrong: ${err.message}`,
          error: true,
          meta: q, // stash question for retry
        },
      ])
    } finally {
      setLoading(false)
      abortRef.current = null
      textareaRef.current?.focus()
    }
  }

  return (
    <div className="app">
      <Sidebar
        retrievalType={retrievalType}
        onRetrievalTypeChange={setRetrievalType}
        k={k}
        onKChange={setK}
        useReranker={useReranker}
        onUseRerankerChange={setUseReranker}
        documents={documents}
        onUploaded={(d) => setDocuments((docs) => [d, ...docs.filter((x) => x.document_id !== d.document_id)])}
        open={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />

      <main className="chat">
        <header className="topbar">
          <button className="icon-btn menu" onClick={() => setSidebarOpen(true)} aria-label="Open settings">
            ☰
          </button>
          <div className="title">
            Ask your documents
            <span className="badge">
              {LABELS[retrievalType]}
              {useReranker && retrievalType === 'hybrid_search' ? ' + rerank' : ''} · k={k}
            </span>
          </div>
          {messages.length > 0 && (
            <button className="ghost" onClick={() => setMessages([])} disabled={loading}>
              New chat
            </button>
          )}
        </header>

        <div className="messages" ref={scrollRef}>
          <div className="messages-inner">
            {messages.length === 0 ? (
              <div className="empty">
                <div className="empty-mark">A</div>
                <h1>What would you like to know?</h1>
                <p>Upload PDFs in the sidebar, then ask questions. Answers are grounded only in your documents.</p>
                <div className="suggestions">
                  {SUGGESTIONS.map((s) => (
                    <button key={s} onClick={() => ask(s)}>
                      {s}
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              messages.map((m) => (
                <Message
                  key={m.id}
                  message={m.error ? { ...m, meta: undefined } : m}
                  onRetry={m.error && m.meta ? () => ask(m.meta!, m.id) : undefined}
                />
              ))
            )}
            {loading && <Thinking />}
          </div>
        </div>

        <form
          className="composer"
          onSubmit={(e) => {
            e.preventDefault()
            ask(input)
          }}
        >
          <div className="composer-inner">
            <textarea
              ref={textareaRef}
              rows={1}
              value={input}
              placeholder="Ask a question about your documents…"
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey && !e.nativeEvent.isComposing) {
                  e.preventDefault()
                  ask(input)
                }
              }}
            />
            {loading ? (
              <button type="button" className="send stop" onClick={() => abortRef.current?.abort()} aria-label="Stop">
                ■
              </button>
            ) : (
              <button type="submit" className="send" disabled={!input.trim()} aria-label="Send">
                ↑
              </button>
            )}
          </div>
          <p className="disclaimer">Enter to send · Shift+Enter for a new line</p>
        </form>
      </main>
    </div>
  )
}
