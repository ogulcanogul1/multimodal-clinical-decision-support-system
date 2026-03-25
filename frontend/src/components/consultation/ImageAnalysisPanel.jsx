import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { toast } from 'react-hot-toast'
import { Upload, Image, ExternalLink, CheckCircle, XCircle } from 'lucide-react'
import { uploadImage, giveImageFeedback } from '../../services/imageAnalysisService'
import { ANALYSIS_TYPE_LABELS } from '../../utils/constants'
import ConfidenceBar from '../common/ConfidenceBar'
import LoadingSpinner from '../common/LoadingSpinner'
import { formatDateTime } from '../../utils/helpers'

export default function ImageAnalysisPanel({
  consultationId,
  analyses,
  onAnalysisAdded,
  onSelectForChat,
  selectedId,
  isOpen,
}) {
  const [analysisType, setAnalysisType] = useState('XRAY')
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
      formData.append('analysisType', analysisType)
      try {
        await uploadImage(formData)
        toast.success('Görüntü analizi tamamlandı')
        onAnalysisAdded()
      } catch {
        toast.error('Görüntü yüklenemedi')
      } finally {
        setUploading(false)
      }
    },
    [consultationId, analysisType, isOpen, onAnalysisAdded]
  )

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'image/*': [] },
    multiple: false,
    disabled: uploading || !isOpen,
  })

  async function handleFeedback(id, approved) {
    setFeedbackLoading((prev) => ({ ...prev, [id]: true }))
    try {
      await giveImageFeedback(id, approved)
      toast.success(approved ? 'Onaylandı' : 'Reddedildi')
      onAnalysisAdded()
    } catch {
      toast.error('Geri bildirim gönderilemedi')
    } finally {
      setFeedbackLoading((prev) => ({ ...prev, [id]: false }))
    }
  }

  return (
    <div className="h-full overflow-y-auto p-4 space-y-4">
      <p className="text-xs font-semibold text-text-secondary uppercase tracking-wide">
        Tıbbi Görüntü Analizi
      </p>

      {/* Type selector */}
      <select
        value={analysisType}
        onChange={(e) => setAnalysisType(e.target.value)}
        className="w-full px-3 py-2 rounded-lg border border-surface-border bg-white text-sm text-text-primary focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
      >
        {Object.entries(ANALYSIS_TYPE_LABELS).map(([v, l]) => (
          <option key={v} value={v}>{l}</option>
        ))}
      </select>

      {/* Dropzone */}
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-xl p-5 text-center cursor-pointer transition ${
          isDragActive
            ? 'border-primary-500 bg-primary-50'
            : 'border-surface-border hover:border-primary-300 hover:bg-surface-hover'
        } ${(uploading || !isOpen) ? 'opacity-50 cursor-not-allowed' : ''}`}
      >
        <input {...getInputProps()} />
        {uploading ? (
          <div className="flex flex-col items-center gap-2">
            <LoadingSpinner />
            <p className="text-xs text-text-muted">Analiz ediliyor...</p>
          </div>
        ) : (
          <>
            <Upload size={24} className="mx-auto text-text-muted mb-2" />
            <p className="text-xs text-text-secondary">
              {isDragActive ? 'Bırakın...' : 'Görüntüyü sürükleyin veya tıklayın'}
            </p>
          </>
        )}
      </div>

      {/* Analyses list */}
      {analyses.length > 0 && (
        <div className="space-y-3">
          <p className="text-xs font-semibold text-text-secondary uppercase tracking-wide border-t border-surface-border pt-3">
            Mevcut Analizler
          </p>
          {analyses.map((a) => (
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
                  <Image size={14} className="text-text-muted" />
                  <span className="text-xs font-semibold text-text-primary">
                    {ANALYSIS_TYPE_LABELS[a.analysisType] ?? a.analysisType}
                  </span>
                </div>
                <span className="text-xs text-text-muted">{formatDateTime(a.createdAt)}</span>
              </div>

              <div>
                <p className="text-xs text-text-muted">Tahmin</p>
                <p className="text-sm font-medium text-text-primary">{a.aiPrediction}</p>
              </div>

              <div>
                <p className="text-xs text-text-muted mb-1">Güven</p>
                <ConfidenceBar confidence={a.confidenceScore} />
              </div>

              {a.heatmapUrl && (
                <a
                  href={a.heatmapUrl}
                  target="_blank"
                  rel="noreferrer"
                  onClick={(e) => e.stopPropagation()}
                  className="flex items-center gap-1 text-xs text-primary-600 hover:text-primary-700"
                >
                  <ExternalLink size={12} />
                  Isı Haritasını Görüntüle
                </a>
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
          ))}
        </div>
      )}
    </div>
  )
}
