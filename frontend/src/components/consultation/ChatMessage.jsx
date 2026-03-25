import { Bot } from 'lucide-react'
import CitedSources from './CitedSources'
import ConfidenceBar from '../common/ConfidenceBar'
import { formatDateTime } from '../../utils/helpers'

export default function ChatMessage({ message }) {
  const { senderRole, messageContent, timestamp, sources, imageAnalysis, documentAnalysis } = message

  if (senderRole === 'SYSTEM') {
    return (
      <div className="flex justify-center">
        <span className="text-xs text-text-muted bg-surface-hover px-3 py-1 rounded-full">
          {messageContent}
        </span>
      </div>
    )
  }

  if (senderRole === 'DOCTOR') {
    return (
      <div className="flex justify-end">
        <div className="max-w-[70%]">
          <div className="bg-primary-600 text-white rounded-2xl rounded-tr-sm px-4 py-3">
            <p className="text-sm whitespace-pre-wrap">{messageContent}</p>
          </div>
          <p className="text-xs text-text-muted text-right mt-1">{formatDateTime(timestamp)}</p>
        </div>
      </div>
    )
  }

  // AI message
  return (
    <div className="flex gap-3 items-start">
      <div className="w-8 h-8 rounded-full bg-ai-accent/10 border border-ai-accent/20 flex items-center justify-center shrink-0 mt-1">
        <Bot size={16} className="text-ai-accent" />
      </div>
      <div className="flex-1 max-w-[80%]">
        <div className="bg-ai-bg border border-ai-border rounded-2xl rounded-tl-sm px-4 py-3">
          <p className="text-xs font-semibold text-ai-accent mb-2">AI Asistan</p>
          <p className="text-sm text-text-primary whitespace-pre-wrap leading-relaxed">
            {messageContent}
          </p>

          {/* Mini analiz özeti */}
          {imageAnalysis && (
            <div className="mt-3 pt-3 border-t border-surface-border">
              <p className="text-xs text-text-muted mb-1">
                Görüntü Analizi — {imageAnalysis.analysisType}
              </p>
              <p className="text-xs font-medium text-text-primary">{imageAnalysis.aiPrediction}</p>
              <ConfidenceBar confidence={imageAnalysis.confidenceScore} />
            </div>
          )}
          {documentAnalysis && (
            <div className="mt-3 pt-3 border-t border-surface-border">
              <p className="text-xs text-text-muted mb-1">
                Lab Analizi — {documentAnalysis.documentType}
              </p>
              <p className="text-xs font-medium text-text-primary">{documentAnalysis.mlpPrediction}</p>
              <ConfidenceBar confidence={documentAnalysis.confidenceScore} />
            </div>
          )}

          <CitedSources sources={sources} />
        </div>
        <p className="text-xs text-text-muted mt-1">{formatDateTime(timestamp)}</p>
      </div>
    </div>
  )
}
