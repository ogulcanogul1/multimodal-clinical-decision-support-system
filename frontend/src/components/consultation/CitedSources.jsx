import { useState } from 'react'
import { ChevronDown, ChevronUp, ExternalLink } from 'lucide-react'

export default function CitedSources({ sources }) {
  const [open, setOpen] = useState(false)
  if (!sources || sources.length === 0) return null

  return (
    <div className="mt-2 border-t border-surface-border pt-2">
      <button
        onClick={() => setOpen(!open)}
        className="flex items-center gap-1 text-xs text-text-secondary hover:text-text-primary transition"
      >
        {open ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
        Kaynakları {open ? 'Gizle' : 'Göster'} ({sources.length})
      </button>
      {open && (
        <ul className="mt-2 space-y-1">
          {sources.map((src, i) => (
            <li key={i} className="flex items-start gap-2 text-xs text-text-secondary">
              <span className="shrink-0 font-medium text-ai-accent">Ref-{i + 1}</span>
              <span className="line-clamp-2">{src.title ?? src}</span>
              {src.url && (
                <a
                  href={src.url}
                  target="_blank"
                  rel="noreferrer"
                  className="shrink-0 text-primary-600 hover:text-primary-700"
                >
                  <ExternalLink size={12} />
                </a>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
