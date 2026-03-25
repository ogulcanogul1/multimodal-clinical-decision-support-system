import { useState, useEffect, useCallback } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { toast } from 'react-hot-toast'
import { X } from 'lucide-react'
import { getConsultation, closeConsultation } from '../../services/consultationService'
import { getPatientById } from '../../services/patientService'
import { getMessages } from '../../services/chatService'
import { getImageAnalyses } from '../../services/imageAnalysisService'
import { getDocumentAnalyses } from '../../services/documentAnalysisService'
import { CONSULTATION_STATUS_LABELS } from '../../utils/constants'
import PatientInfoPanel from '../../components/consultation/PatientInfoPanel'
import ChatPanel from '../../components/consultation/ChatPanel'
import ImageAnalysisPanel from '../../components/consultation/ImageAnalysisPanel'
import DocumentAnalysisPanel from '../../components/consultation/DocumentAnalysisPanel'
import LoadingSpinner from '../../components/common/LoadingSpinner'

export default function ConsultationWorkspacePage() {
  const { id } = useParams()
  const navigate = useNavigate()

  const [consultation, setConsultation] = useState(null)
  const [patient, setPatient] = useState(null)
  const [messages, setMessages] = useState([])
  const [imageAnalyses, setImageAnalyses] = useState([])
  const [documentAnalyses, setDocumentAnalyses] = useState([])
  const [loading, setLoading] = useState(true)
  const [closing, setClosing] = useState(false)

  const [selectedImageForChat, setSelectedImageForChat] = useState(null)
  const [selectedDocumentForChat, setSelectedDocumentForChat] = useState(null)

  const fetchMessages = useCallback(async () => {
    const res = await getMessages(id)
    setMessages(res.data)
  }, [id])

  const fetchAnalyses = useCallback(async () => {
    const [imgRes, docRes] = await Promise.all([
      getImageAnalyses(id),
      getDocumentAnalyses(id),
    ])
    setImageAnalyses(imgRes.data)
    setDocumentAnalyses(docRes.data)
  }, [id])

  useEffect(() => {
    async function load() {
      try {
        const cRes = await getConsultation(id)
        const c = cRes.data
        setConsultation(c)
        const [pRes, msgRes, imgRes, docRes] = await Promise.all([
          getPatientById(c.patientId),
          getMessages(id),
          getImageAnalyses(id),
          getDocumentAnalyses(id),
        ])
        setPatient(pRes.data)
        setMessages(msgRes.data)
        setImageAnalyses(imgRes.data)
        setDocumentAnalyses(docRes.data)
      } catch {
        toast.error('Konsültasyon yüklenemedi')
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [id])

  async function handleClose() {
    if (!window.confirm('Konsültasyonu kapatmak istediğinizden emin misiniz?')) return
    setClosing(true)
    try {
      const res = await closeConsultation(id)
      setConsultation(res.data)
      toast.success('Konsültasyon kapatıldı')
    } catch {
      toast.error('Konsültasyon kapatılamadı')
    } finally {
      setClosing(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full min-h-[60vh]">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  const isOpen = consultation?.status === 'OPEN'

  return (
    <div className="flex flex-col h-[calc(100vh-3.5rem-3rem)] -m-6">
      {/* Top bar */}
      <div className="flex items-center justify-between px-5 py-3 border-b border-surface-border bg-surface-card shrink-0">
        <div className="flex items-center gap-3">
          <span className="text-sm font-semibold text-text-primary">
            Konsültasyon #{id.slice(0, 8)}
          </span>
          <span className="text-text-muted text-sm">·</span>
          <span className="text-sm text-text-secondary">
            {patient?.firstName} {patient?.lastName}
          </span>
          <span
            className={`text-xs font-medium px-2 py-0.5 rounded-full ${
              isOpen
                ? 'bg-success-100 text-success-700'
                : 'bg-surface-border text-text-muted'
            }`}
          >
            {CONSULTATION_STATUS_LABELS[consultation?.status] ?? consultation?.status}
          </span>
        </div>
        {isOpen && (
          <button
            onClick={handleClose}
            disabled={closing}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium border border-danger-200 text-danger-600 hover:bg-danger-50 transition disabled:opacity-50"
          >
            <X size={14} />
            {closing ? 'Kapatılıyor...' : 'Konsültasyonu Kapat'}
          </button>
        )}
      </div>

      {/* 3-panel layout */}
      <div className="flex flex-1 min-h-0">
        {/* Left — Patient info (20%) */}
        <div className="w-52 shrink-0 border-r border-surface-border bg-surface-card overflow-hidden">
          <PatientInfoPanel patient={patient} />
        </div>

        {/* Center — Chat (flex-1 ~50%) */}
        <div className="flex-1 flex flex-col min-w-0 border-r border-surface-border">
          <ChatPanel
            consultationId={id}
            messages={messages}
            onMessageSent={fetchMessages}
            isOpen={isOpen}
            pendingImage={selectedImageForChat}
            pendingDocument={selectedDocumentForChat}
            onClearImage={() => setSelectedImageForChat(null)}
            onClearDocument={() => setSelectedDocumentForChat(null)}
          />
        </div>

        {/* Right — Analysis panels (30%) */}
        <div className="w-80 shrink-0 flex flex-col min-h-0 overflow-hidden">
          <div className="flex-1 overflow-hidden border-b border-surface-border">
            <ImageAnalysisPanel
              consultationId={id}
              analyses={imageAnalyses}
              onAnalysisAdded={fetchAnalyses}
              onSelectForChat={(a) =>
                setSelectedImageForChat(selectedImageForChat?.id === a.id ? null : a)
              }
              selectedId={selectedImageForChat?.id}
              isOpen={isOpen}
            />
          </div>
          <div className="flex-1 overflow-hidden">
            <DocumentAnalysisPanel
              consultationId={id}
              analyses={documentAnalyses}
              onAnalysisAdded={fetchAnalyses}
              onSelectForChat={(a) =>
                setSelectedDocumentForChat(selectedDocumentForChat?.id === a.id ? null : a)
              }
              selectedId={selectedDocumentForChat?.id}
              isOpen={isOpen}
            />
          </div>
        </div>
      </div>
    </div>
  )
}
