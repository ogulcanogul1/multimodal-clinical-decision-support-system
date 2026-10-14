import { useState } from 'react'
import { toast } from 'react-hot-toast'
import { ClipboardList, ChevronDown, ChevronUp, Plus } from 'lucide-react'
import { uploadDocument } from '../../services/documentAnalysisService'
import { formatDateTime } from '../../utils/helpers'

export default function ClinicalNotesPanel({ consultationId, isOpen, clinicalNotes = [], onNoteAdded }) {
  const [noteText, setNoteText] = useState('')
  const [saving, setSaving] = useState(false)
  const [historyOpen, setHistoryOpen] = useState(false)

  async function handleAdd() {
    if (!noteText.trim()) return
    setSaving(true)
    const blob = new Blob([noteText], { type: 'text/plain' })
    const file = new File([blob], 'klinik-not.txt', { type: 'text/plain' })
    const formData = new FormData()
    formData.append('file', file)
    formData.append('consultationId', consultationId)
    formData.append('documentType', 'CLINICAL_NOTE')
    try {
      await uploadDocument(formData)
      toast.success('Klinik not eklendi')
      setNoteText('')
      onNoteAdded?.()
    } catch {
      toast.error('Not eklenemedi')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="p-3 space-y-2 border-b border-surface-border">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-1.5">
          <ClipboardList size={13} className="text-text-muted" />
          <p className="text-xs font-semibold text-text-secondary uppercase tracking-wide">
            Klinik Notlar
          </p>
        </div>
        {clinicalNotes.length > 0 && (
          <button
            onClick={() => setHistoryOpen((v) => !v)}
            className="flex items-center gap-0.5 text-xs text-text-muted hover:text-text-secondary transition"
          >
            Geçmiş ({clinicalNotes.length})
            {historyOpen ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
          </button>
        )}
      </div>

      {/* History */}
      {historyOpen && clinicalNotes.length > 0 && (
        <div className="space-y-1.5 max-h-32 overflow-y-auto">
          {clinicalNotes.map((note) => (
            <div key={note.id} className="rounded-md border border-surface-border bg-surface-hover p-2 text-xs">
              <span className="text-text-muted block mb-0.5">{formatDateTime(note.createdAt)}</span>
              {note.mlpPrediction && (
                <p className="text-text-primary">{note.mlpPrediction}</p>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Input */}
      {isOpen ? (
        <div className="flex gap-2 items-end">
          <textarea
            value={noteText}
            onChange={(e) => setNoteText(e.target.value)}
            placeholder="Muayene bulguları, semptomlar..."
            rows={2}
            disabled={saving}
            className="flex-1 px-2.5 py-1.5 rounded-lg border border-surface-border bg-white text-xs text-text-primary placeholder:text-text-muted focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none disabled:opacity-50"
          />
          <button
            onClick={handleAdd}
            disabled={!noteText.trim() || saving}
            className="flex items-center gap-1 px-2.5 py-1.5 rounded-lg bg-primary-600 hover:bg-primary-700 text-white text-xs font-medium transition disabled:opacity-50 disabled:cursor-not-allowed shrink-0"
          >
            <Plus size={13} />
            {saving ? '...' : 'Ekle'}
          </button>
        </div>
      ) : (
        <p className="text-xs text-text-muted italic">
          {clinicalNotes.length === 0 ? 'Not bulunmuyor' : ''}
        </p>
      )}
    </div>
  )
}
