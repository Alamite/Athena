export default function OwlLoader() {
  return (
    <div className="flex items-center gap-2.5">
      <div className="w-7 h-7 rounded-xl bg-blue-600 flex items-center justify-center flex-shrink-0 animate-owl-bob">
        <svg className="w-4.5 h-4.5" viewBox="0 0 24 24" fill="none">
          {/* Head */}
          <path
            d="M12 4C8.5 4 6 7 6 10.5V15a6 6 0 0012 0v-4.5C18 7 15.5 4 12 4z"
            fill="white"
            fillOpacity="0.15"
          />
          {/* Ear tufts */}
          <path d="M9.5 4L8 1.5" stroke="white" strokeWidth="1.5" strokeLinecap="round" />
          <path d="M14.5 4L16 1.5" stroke="white" strokeWidth="1.5" strokeLinecap="round" />
          {/* Eye whites */}
          <circle cx="9.5" cy="11" r="2.6" fill="white" />
          <circle cx="14.5" cy="11" r="2.6" fill="white" />
          {/* Pupils (blink via vertical scale) */}
          <g style={{ transformBox: 'fill-box', transformOrigin: 'center' }} className="animate-owl-blink">
            <circle cx="9.5" cy="11" r="1.2" fill="#1e40af" />
            <circle cx="14.5" cy="11" r="1.2" fill="#1e40af" />
          </g>
          {/* Beak */}
          <path d="M11 14.5L12 16.5L13 14.5H11Z" fill="white" fillOpacity="0.85" />
        </svg>
      </div>
      <span className="text-xs text-gray-400">Thinking…</span>
    </div>
  )
}
