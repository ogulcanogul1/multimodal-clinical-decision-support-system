import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { toast } from 'react-hot-toast'
import { Upload, Image, Maximize2, CheckCircle, XCircle, X } from 'lucide-react'
import { uploadImage, giveImageFeedback } from '../../services/imageAnalysisService'
import { ANALYSIS_TYPE_LABELS } from '../../utils/constants'
import ConfidenceBar from '../common/ConfidenceBar'
import LoadingSpinner from '../common/LoadingSpinner'

const FILENAME_KEY = (id) => `img_filename_${id}`

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
  const [uploadRequested, setUploadRequested] = useState(false)

  // Analyses come from server; show upload area only if there are none or user clicked X
  const showUpload = analyses.length === 0 || uploadRequested
  // Use the most recently uploaded analysis
  const analysis = analyses[analyses.length - 1] ?? null

  function getFilename(a) {
    return localStorage.getItem(FILENAME_KEY(a.id)) ?? ANALYSIS_TYPE_LABELS[a.analysisType] ?? a.analysisType
  }

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
        const res = await uploadImage(formData)
        localStorage.setItem(FILENAME_KEY(res.data.id), file.name)
        toast.success('Görüntü analizi tamamlandı')
        setUploadRequested(false)
        onSelectForChat(res.data)
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

      {/* Upload area */}
      {showUpload && (
        <>
          <select
            value={analysisType}
            onChange={(e) => setAnalysisType(e.target.value)}
            className="w-full px-3 py-2 rounded-lg border border-surface-border bg-white text-sm text-text-primary focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          >
            {Object.entries(ANALYSIS_TYPE_LABELS).map(([v, l]) => (
              <option key={v} value={v}>{l}</option>
            ))}
          </select>

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
                  <Image size={22} className="text-text-muted" />
                </div>
                <p className="text-sm font-medium text-text-secondary">
                  Görüntüyü buraya sürükleyin
                </p>
                <p className="text-xs text-text-muted">veya tıklayarak seçin</p>
                <span className="mt-1 text-xs text-text-muted bg-surface-hover border border-surface-border px-2 py-0.5 rounded-full">
                  JPG, PNG, DICOM
                </span>
              </div>
            )}
          </div>
        </>
      )}

      {/* Analysis card — shown when upload is done */}
      {!showUpload && analysis && (
        <div
          className={`rounded-xl border p-3 space-y-3 cursor-pointer transition ${
            selectedId === analysis.id
              ? 'border-primary-400 bg-primary-50'
              : 'border-surface-border bg-surface-card hover:bg-surface-hover'
          }`}
          onClick={() => onSelectForChat(analysis)}
        >
          {/* Filename + X */}
          <div className="flex items-start justify-between gap-2">
            <div className="flex items-center gap-1.5 min-w-0">
              <Image size={14} className="text-text-muted shrink-0" />
              <span className="text-xs font-semibold text-text-primary truncate">
                {getFilename(analysis)}
              </span>
            </div>
            <button
              onClick={(e) => { e.stopPropagation(); setUploadRequested(true) }}
              className="shrink-0 p-0.5 rounded hover:bg-surface-border transition text-text-muted hover:text-text-primary"
              title="Kaldır"
            >
              <X size={14} />
            </button>
          </div>

          {/* Selected badge */}
          {selectedId === analysis.id && (
            <span className="inline-block text-xs font-medium text-primary-700 bg-primary-100 px-2 py-0.5 rounded-full">
              Sohbete eklenecek
            </span>
          )}

          {/* AI results — only if prediction exists */}
          {analysis.aiPrediction && (
            <>
              <div>
                <p className="text-xs text-text-muted">AI Tahmini</p>
                <p className="text-sm font-medium text-text-primary">{analysis.aiPrediction}</p>
              </div>

              <div>
                <p className="text-xs text-text-muted mb-1">Güven</p>
                <ConfidenceBar confidence={analysis.confidenceScore} />
              </div>

              {analysis.heatmapUrl && (
                <div className="space-y-1.5" onClick={(e) => e.stopPropagation()}>
                  <p className="text-xs text-text-muted font-medium">Aktivasyon Haritası (Grad-CAM)</p>
                  <div className="relative rounded-lg overflow-hidden border border-surface-border bg-surface-hover">
                    <img
                      src={analysis.heatmapUrl}
                      alt="Grad-CAM aktivasyon haritası"
                      className="w-full object-cover rounded-lg"
                      onError={(e) => { e.currentTarget.parentElement.style.display = 'none' }}
                    />
                    <a
                      href={analysis.heatmapUrl}
                      target="_blank"
                      rel="noreferrer"
                      className="absolute top-1.5 right-1.5 flex items-center gap-0.5 px-1.5 py-0.5 rounded bg-black/50 hover:bg-black/70 text-white text-[10px] font-medium transition"
                    >
                      <Maximize2 size={10} />
                      Büyüt
                    </a>
                  </div>
                  <p className="text-[10px] text-text-muted leading-relaxed">
                    Kırmızı/sarı bölgeler modelin tanı için odaklandığı alanları gösterir.
                  </p>
                </div>
              )}

              {/* Feedback — only after AI prediction */}
              {analysis.doctorFeedback === null || analysis.doctorFeedback === undefined ? (
                <div className="flex gap-2 pt-0.5">
                  <button
                    onClick={(e) => { e.stopPropagation(); handleFeedback(analysis.id, true) }}
                    disabled={feedbackLoading[analysis.id]}
                    className="flex items-center gap-1 px-2.5 py-1 text-xs rounded-md bg-success-100 text-success-700 hover:bg-success-500 hover:text-white transition disabled:opacity-50"
                  >
                    <CheckCircle size={12} /> Onayla
                  </button>
                  <button
                    onClick={(e) => { e.stopPropagation(); handleFeedback(analysis.id, false) }}
                    disabled={feedbackLoading[analysis.id]}
                    className="flex items-center gap-1 px-2.5 py-1 text-xs rounded-md bg-danger-100 text-danger-600 hover:bg-danger-500 hover:text-white transition disabled:opacity-50"
                  >
                    <XCircle size={12} /> Reddet
                  </button>
                </div>
              ) : analysis.doctorFeedback === true ? (
                <span className="inline-flex items-center gap-1 text-xs font-medium text-success-700 bg-success-100 px-2 py-0.5 rounded-full">
                  <CheckCircle size={11} /> Onaylandı
                </span>
              ) : (
                <span className="inline-flex items-center gap-1 text-xs font-medium text-danger-600 bg-danger-100 px-2 py-0.5 rounded-full">
                  <XCircle size={11} /> Reddedildi
                </span>
              )}
            </>
          )}
        </div>
      )}
    </div>
  )
}
