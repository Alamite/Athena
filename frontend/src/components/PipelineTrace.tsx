import type { PipelineEvent } from '../services/api'

interface Props {
  events: PipelineEvent[]
}

const STEP_ICONS: Record<string, string> = {
  rewrite_query: '✎',
  vector_search: '🔎',
  bm25_search: '🔤',
  fusion: '🔀',
  rerank: '🎯',
  build_context: '📄',
  generation: '✍',
  citations: '🔖',
}

export default function PipelineTrace({ events }: Props) {
  const order: string[] = []
  const latestByStep = new Map<string, PipelineEvent>()

  for (const event of events) {
    if (!latestByStep.has(event.step)) order.push(event.step)
    latestByStep.set(event.step, event)
  }

  const steps = order.map((step) => latestByStep.get(step)!)

  if (steps.length === 0) return null

  return (
    <div className="mb-2 rounded-xl border border-gray-700 bg-gray-900/60 px-3 py-2.5 space-y-1.5">
      {steps.map((s) => (
        <div key={s.step} className="flex items-start gap-2 text-xs">
          <span className="flex-shrink-0 w-4 pt-0.5 text-center">
            {s.status === 'start' ? (
              <span className="inline-block w-2.5 h-2.5 border-2 border-gray-500 border-t-blue-400 rounded-full animate-spin" />
            ) : s.status === 'error' ? (
              <span className="text-red-400">✕</span>
            ) : (
              <span className="text-emerald-400">✓</span>
            )}
          </span>
          <span className="flex-shrink-0">{STEP_ICONS[s.step] ?? '•'}</span>
          <span
            className={
              s.status === 'start'
                ? 'text-gray-400'
                : s.status === 'error'
                  ? 'text-red-300'
                  : 'text-gray-300'
            }
          >
            {s.message}
          </span>
        </div>
      ))}
    </div>
  )
}
