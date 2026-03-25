import { useState, useRef, useEffect } from 'react'
import { Send, X, Image, FileText, Bot } from 'lucide-react'
import { toast } from 'react-hot-toast'
import { sendMessage } from '../../services/chatService'
import ChatMessage from './ChatMessage'

export default function ChatPanel({
  consultationId,
  messages,
  onMessageSent,
  isOpen,
  pendingImage,
  pendingDocument,
  onClearImage,
  onClearDocument,
}) {
  const [text, setText] = useState('')
  const [sending, setSending] = useState(false)
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, sending])

  async function handleSend() {
    if (!text.trim() && !pendingImage && !pendingDocument) return
    if (!isOpen) {
      toast.error('Kapalı bir konsültasyona mesaj gönderilemez')
      return
    }

    setSending(true)
    try {
      await sendMessage(consultationId, {
        messageContent: text.trim() || '(Analiz değerlendirmesi istendi)',
        imageAnalysisId: pendingImage?.id ?? null,
        documentAnalysisId: pendingDocument?.id ?? null,
      })
      setText('')
      onClearImage?.()
      onClearDocument?.()
      await onMessageSent()
    } catch {
      toast.error('Mesaj gönderilemedi')
    } finally {
      setSending(false)
    }
  }

  return (
    <div className="flex flex-col h-full">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center text-text-muted">
            <Bot size={36} className="mb-2 opacity-30" />
            <p className="text-sm">Hastanın bulgularını AI asistanla paylaşın.</p>
          </div>
        )}
        {messages.map((m) => (
          <ChatMessage key={m.id} message={m} />
        ))}

        {/* AI loading state */}
        {sending && (
          <div className="flex gap-3 items-start">
            <div className="w-8 h-8 rounded-full bg-ai-accent/10 border border-ai-accent/20 flex items-center justify-center shrink-0">
              <Bot size={16} className="text-ai-accent" />
            </div>
            <div className="bg-ai-bg border border-ai-border rounded-2xl rounded-tl-sm px-4 py-4 max-w-[80%]">
              <p className="text-xs font-semibold text-ai-accent mb-3">AI Asistan</p>
              <div className="flex items-center gap-2">
                <div className="flex gap-1">
                  <span className="w-2 h-2 rounded-full bg-ai-accent/40 animate-bounce" style={{ animationDelay: '0ms' }} />
                  <span className="w-2 h-2 rounded-full bg-ai-accent/40 animate-bounce" style={{ animationDelay: '150ms' }} />
                  <span className="w-2 h-2 rounded-full bg-ai-accent/40 animate-bounce" style={{ animationDelay: '300ms' }} />
                </div>
                <span className="text-sm text-text-secondary font-medium animate-pulse">
                  Yapay Zeka Konsilyumu Değerlendiriyor... Lütfen Bekleyin
                </span>
              </div>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input area */}
      <div className="border-t border-surface-border p-3 space-y-2">
        {/* Attached analysis badges */}
        {(pendingImage || pendingDocument) && (
          <div className="flex flex-wrap gap-2">
            {pendingImage && (
              <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-primary-100 text-primary-700 text-xs font-medium">
                <Image size={12} />
                Görüntü: {pendingImage.analysisType}
                <button onClick={onClearImage} className="ml-1 hover:text-primary-900">
                  <X size={12} />
                </button>
              </div>
            )}
            {pendingDocument && (
              <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-warning-100 text-warning-600 text-xs font-medium">
                <FileText size={12} />
                Lab: {pendingDocument.documentType}
                <button onClick={onClearDocument} className="ml-1 hover:text-warning-800">
                  <X size={12} />
                </button>
              </div>
            )}
          </div>
        )}

        <div className="flex gap-2">
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault()
                handleSend()
              }
            }}
            placeholder="Mesajınızı yazın... (Shift+Enter yeni satır)"
            rows={2}
            disabled={sending || !isOpen}
            className="flex-1 px-3 py-2.5 rounded-lg border border-surface-border bg-white text-sm text-text-primary placeholder-text-muted focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none transition disabled:bg-surface-bg disabled:cursor-not-allowed"
          />
          <button
            onClick={handleSend}
            disabled={sending || !isOpen || (!text.trim() && !pendingImage && !pendingDocument)}
            className="self-end flex items-center justify-center w-10 h-10 rounded-lg bg-primary-600 hover:bg-primary-700 text-white transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Send size={16} />
          </button>
        </div>
        {!isOpen && (
          <p className="text-xs text-text-muted text-center">Bu konsültasyon kapalıdır.</p>
        )}
      </div>
    </div>
  )
}
