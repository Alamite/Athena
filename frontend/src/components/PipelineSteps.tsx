import type { PipelineStep } from '../api'
import { formatMs } from '../format'

function StatusIcon({ status }: { status: PipelineStep['status'] }) {
  if (status === 'running') return <span className="step-icon running"><span className="spinner sm" /></span>
  return (
    <span className={`step-icon ${status}`}>
      <svg viewBox="0 0 16 16" width="11" height="11" fill="none" stroke="currentColor" strokeWidth="2.4"
        strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
        {status === 'done' ? <path d="m3.5 8.5 3 3 6-7" /> : <path d="M4.5 4.5l7 7m0-7-7 7" />}
      </svg>
    </span>
  )
}

/** Vertical list of pipeline stages. `showBars` adds a bar for each stage's share of total time. */
export function StepList({ steps, showBars = false }: { steps: PipelineStep[]; showBars?: boolean }) {
  const total = steps.reduce((t, s) => t + (s.duration_ms ?? 0), 0)
  return (
    <ol className="steps">
      {steps.map((s) => (
        <li key={s.id} className={`step ${s.status}`}>
          <StatusIcon status={s.status} />
          <div className="step-main">
            <div className="step-row">
              <span className="step-label">{s.label}</span>
              <span className="step-time">{s.status === 'running' ? '' : formatMs(s.duration_ms)}</span>
            </div>
            {s.detail && <div className="step-detail">{s.detail}</div>}
            {/* {showBars && total > 0 && s.duration_ms != null && (
              <div className="step-bar">
                <span style={{ width: `${Math.max(1, (s.duration_ms / total) * 100)}%` }} />
              </div>
            )} */}
          </div>
        </li>
      ))}
    </ol>
  )
}

/** Shown in place of the answer while the backend is working. */
export function LiveActivity({ steps }: { steps: PipelineStep[] }) {
  const shown: PipelineStep[] = steps.length
    ? steps
    : [{ id: 'connect', label: 'Sending question to backend', status: 'running' }]
  return (
    <div className="msg assistant">
      <div className="avatar">A</div>
      <div className="body">
        <div className="activity">
          <StepList steps={shown} />
        </div>
      </div>
    </div>
  )
}
