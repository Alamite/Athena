import { useCallback, useRef, useState } from 'react'
import type { DocumentInfo } from '../services/api'
import { uploadDocument } from '../services/api'

interface Props {
  documents: DocumentInfo[]
  onUploadSuccess: () => void
}

type UploadState = 'idle' | 'uploading' | 'success' | 'error'

export default function FileUploader({ documents, onUploadSuccess }: Props) {
  const [uploadState, setUploadState] = useState<UploadState>('idle')
  const [statusMessage, setStatusMessage] = useState('')
  const [isDragOver, setIsDragOver] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)

  const handleFile = useCallback(
    async (file: File) => {
      if (!file.name.endsWith('.md')) {
        setUploadState('error')
        setStatusMessage('Only .md files are accepted')
        return
      }

      setUploadState('uploading')
      setStatusMessage(`Ingesting ${file.name}...`)

      try {
        const result = await uploadDocument(file)
        setUploadState('success')
        setStatusMessage(`${result.filename} — ${result.chunks_created} chunks created`)
        onUploadSuccess()
      } catch {
        setUploadState('error')
        setStatusMessage('Upload failed. Check the backend logs.')
      }
    },
    [onUploadSuccess],
  )

  const onDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault()
      setIsDragOver(false)
      const file = e.dataTransfer.files[0]
      if (file) handleFile(file)
    },
    [handleFile],
  )

  const onInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) handleFile(file)
    e.target.value = ''
  }

  const borderColor =
    isDragOver
      ? 'border-blue-500 bg-blue-950/30'
      : uploadState === 'success'
        ? 'border-emerald-600/50 bg-emerald-950/20'
        : uploadState === 'error'
          ? 'border-red-600/50 bg-red-950/20'
          : 'border-gray-600 bg-gray-800/50 hover:border-gray-500'

  return (
    <div className="space-y-3">
      <div
        className={`relative rounded-xl border-2 border-dashed transition-colors cursor-pointer ${borderColor}`}
        onDragOver={(e) => {
          e.preventDefault()
          setIsDragOver(true)
        }}
        onDragLeave={() => setIsDragOver(false)}
        onDrop={onDrop}
        onClick={() => inputRef.current?.click()}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".md"
          className="hidden"
          onChange={onInputChange}
        />

        <div className="py-5 px-4 flex flex-col items-center gap-2 text-center">
          {uploadState === 'uploading' ? (
            <>
              <div className="w-6 h-6 border-2 border-blue-400 border-t-transparent rounded-full animate-spin" />
              <p className="text-sm text-blue-300">{statusMessage}</p>
            </>
          ) : uploadState === 'success' ? (
            <>
              <svg className="w-6 h-6 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              <p className="text-sm text-emerald-300">{statusMessage}</p>
              <p className="text-xs text-gray-500">Drop another file to ingest</p>
            </>
          ) : uploadState === 'error' ? (
            <>
              <svg className="w-6 h-6 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
              <p className="text-sm text-red-300">{statusMessage}</p>
              <p className="text-xs text-gray-500">Click to try again</p>
            </>
          ) : (
            <>
              <svg className="w-6 h-6 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5" />
              </svg>
              <p className="text-sm text-gray-300">
                <span className="text-blue-400 font-medium">Click to upload</span>{' '}
                or drag and drop
              </p>
              <p className="text-xs text-gray-500">.md files only</p>
            </>
          )}
        </div>
      </div>

      {documents.length > 0 && (
        <div className="space-y-1">
          {documents.map((doc) => (
            <div
              key={doc.name}
              className="flex items-center justify-between px-3 py-2 rounded-lg bg-gray-800/60 border border-gray-700/50"
            >
              <div className="flex items-center gap-2 min-w-0">
                <svg className="w-3.5 h-3.5 text-gray-500 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <span className="text-xs text-gray-300 truncate">{doc.name}.md</span>
              </div>
              <span className="text-[11px] text-gray-500 flex-shrink-0 ml-2">
                {doc.chunks} chunks
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
