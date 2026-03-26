import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { toast } from 'react-hot-toast'
import { Upload, FileText, CheckCircle, XCircle } from 'lucide-react'
import { uploadDocument, giveDocumentFeedback } from '../../services/documentAnalysisService'
import { DOCUMENT_TYPE_LABELS } from '../../utils/constants'
import ConfidenceBar from '../common/ConfidenceBar'
import LoadingSpinner from '../common/LoadingSpinner'
import { formatDateTime } from '../../utils/helpers'

const IMPORTANCE_LABELS = {
  high: 'Yüksek Etki',
  medium: 'Orta Etki',
  low: 'Düşük Etki',
  yüksek_etki: 'Yüksek Etki',
  orta_etki: 'Orta Etki',
  düşük_etki: 'Düşük Etki',
}

export default function DocumentAnalysisPanel({
  consultationId,
  analyses,
  onAnalysisAdded,
  onSelectForChat,
  selectedId,
  isOpen,
}) {
  const [documentType, setDocumentType] = useState('BLOOD_TEST')
  const [uploading, setUploading] = useState(false)
  const [feedbackLoading, setFeedbackLoading] = useState({})

  const onDrop = useCallback(
    async (acceptedFiles) => {
      if (!isOpen) { toast.error('Kapalı konsültasyona analiz eklenemez'); return }
      const file = acceptedFiles[0]
      if (!file) return
      setUploading(true)
      const formData = new FormData()
      formData.append('file', file)
      formData.append('consultationId', consultationId)
      formData.append('documentType', documentType)
      try {
        await uploadDocument(formData)
        toast.success('Doküman analizi tamamlandı')
        onAnalysisAdded()
      } catch {
        toast.error('Doküman yüklenemedi')
      } finally {
        setUploading(false)
      }
    },
    [consultationId, documentType, isOpen, onAnalysisAdded]
  )

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'application/pdf': ['.pdf'], 'text/*': [] },
    multiple: false,
    disabled: uploading || !isOpen,
  })

  async function handleFeedback(id, approved) {
    setFeedbackLoading((prev) => ({ ...prev, [id]: true }))
    try {
      await giveDocumentFeedback(id, approved)
      toast.success(approved ? 'Onaylandı' : 'Reddedildi')
      onAnalysisAdded()
    } catch {
      toast.error('Geri bildirim gönderilemedi')
    } finally {
      setFeedbackLoading((prev) => ({ ...prev, [id]: false }))
    }
  }

  function getTopFeatures(featureImportance) {
    if (!featureImportance) return []
    return Object.entries(featureImportance)
      .slice(0, 4)
  }

  return (
    <div className="h-full overflow-y-auto p-4 space-y-4">
      <p className="text-xs font-semibold text-text-secondary uppercase tracking-wide">
        Laboratuvar Analizi
      </p>

      <select
        value={documentType}
        onChange={(e) => setDocumentType(e.target.value)}
        className="w-full px-3 py-2 rounded-lg border border-surface-border bg-white text-sm text-text-primary focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
      >
        {Object.entries(DOCUMENT_TYPE_LABELS).map(([v, l]) => (
          <option key={v} value={v}>{l}</option>
        ))}
      </select>

      {/* Dropzone */}
      <div
        {...getRootProps()}
        className={`relative border-2 border-dashed rounded-xl py-8 px-4 text-center cursor-pointer transition-all duration-200 ${
          isDragActive
            ? 'border-primary-500 bg-primary-50 scale-[1.01]'
            : 'border-surface-border hover:border-primary-400 hover:bg-primary-50/40'
        } ${(uploading || !isOpen) ? 'opacity-50 cursor-not-allowed' : ''}`}
      >
        <input {...getInputProps()} />
        {uploading ? (
          <div className="flex flex-col items-center gap-3">
            <LoadingSpinner size="md" />
            <p className="text-sm font-medium text-text-secondary">Analiz ediliyor...</p>
            <p className="text-xs text-text-muted">Lütfen bekleyin</p>
          </div>
        ) : isDragActive ? (
          <div className="flex flex-col items-center gap-2">
            <div className="w-12 h-12 rounded-full bg-primary-100 flex items-center justify-center">
              <Upload size={22} className="text-primary-600" />
            </div>
            <p className="text-sm font-semibold text-primary-600">Dosyayı bırakın</p>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-2">
            <div className="w-12 h-12 rounded-full bg-surface-hover border border-surface-border flex items-center justify-center mb-1">
              <FileText size={22} className="text-text-muted" />
            </div>
            <p className="text-sm font-medium text-text-secondary">
              Dosyayı buraya sürükleyin
            </p>
            <p className="text-xs text-text-muted">veya tıklayarak seçin</p>
            <span className="mt-1 text-xs text-text-muted bg-surface-hover border border-surface-border px-2 py-0.5 rounded-full">
              PDF, TXT
            </span>
          </div>
        )}
      </div>

      {/* Analyses */}
      {analyses.length > 0 && (
        <div className="space-y-3">
          <p className="text-xs font-semibold text-text-secondary uppercase tracking-wide border-t border-surface-border pt-3">
            Mevcut Analizler
          </p>
          {analyses.map((a) => {
            const topFeatures = getTopFeatures(a.featureImportance)
            return (
              <div
                key={a.id}
                className={`rounded-lg border p-3 space-y-2 cursor-pointer transition ${
                  selectedId === a.id
                    ? 'border-primary-400 bg-primary-50'
                    : 'border-surface-border bg-surface-card hover:bg-surface-hover'
                }`}
                onClick={() => onSelectForChat(a)}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-1.5">
                    <FileText size={14} className="text-text-muted" />
                    <span className="text-xs font-semibold text-text-primary">
                      {DOCUMENT_TYPE_LABELS[a.documentType] ?? a.documentType}
                    </span>
                  </div>
                  <span className="text-xs text-text-muted">{formatDateTime(a.createdAt)}</span>
                </div>

                <div>
                  <p className="text-xs text-text-muted">Tahmin</p>
                  <p className="text-sm font-medium text-text-primary">{a.mlpPrediction}</p>
                </div>

                <div>
                  <p className="text-xs text-text-muted mb-1">Güven</p>
                  <ConfidenceBar confidence={a.confidenceScore} />
                </div>

                {topFeatures.length > 0 && (
                  <div>
                    <p className="text-xs text-text-muted mb-1">Önemli Faktörler</p>
                    <ul className="space-y-0.5">
                      {topFeatures.map(([key, val]) => (
                        <li key={key} className="flex justify-between text-xs">
                          <span className="text-text-primary">{key}</span>
                          <span className="text-text-muted">
                            {IMPORTANCE_LABELS[val] ?? val}
                          </span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Feedback */}
                {a.doctorFeedback === null || a.doctorFeedback === undefined ? (
                  <div className="flex gap-2 pt-1">
                    <button
                      onClick={(e) => { e.stopPropagation(); handleFeedback(a.id, true) }}
                      disabled={feedbackLoading[a.id]}
                      className="flex items-center gap-1 px-2.5 py-1 text-xs rounded-md bg-success-100 text-success-700 hover:bg-success-500 hover:text-white transition disabled:opacity-50"
                    >
                      <CheckCircle size={12} /> Onayla
                    </button>
                    <button
                      onClick={(e) => { e.stopPropagation(); handleFeedback(a.id, false) }}
                      disabled={feedbackLoading[a.id]}
                      className="flex items-center gap-1 px-2.5 py-1 text-xs rounded-md bg-danger-100 text-danger-600 hover:bg-danger-500 hover:text-white transition disabled:opacity-50"
                    >
                      <XCircle size={12} /> Reddet
                    </button>
                  </div>
                ) : a.doctorFeedback === true ? (
                  <span className="inline-flex items-center gap-1 text-xs font-medium text-success-700 bg-success-100 px-2 py-0.5 rounded-full">
                    <CheckCircle size={11} /> Onaylandı
                  </span>
                ) : (
                  <span className="inline-flex items-center gap-1 text-xs font-medium text-danger-600 bg-danger-100 px-2 py-0.5 rounded-full">
                    <XCircle size={11} /> Reddedildi
                  </span>
                )}
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
