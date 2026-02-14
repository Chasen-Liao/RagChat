import React, { useState, useRef, useEffect } from 'react'
import { Send, Paperclip, X, CheckCircle, AlertCircle } from 'lucide-react'
import { useFileUpload } from '../hooks/useChat'

interface InputBoxProps {
  onSend: (message: string) => void
  disabled?: boolean
}

export const InputBox: React.FC<InputBoxProps> = ({ onSend, disabled }) => {
  const [message, setMessage] = useState('')
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const { uploadFile, isUploading, uploadStatus } = useFileUpload()

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`
    }
  }, [message])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (selectedFile) {
      try {
        await uploadFile(selectedFile)
        setSelectedFile(null)
        if (fileInputRef.current) {
          fileInputRef.current.value = ''
        }
      } catch {
        // Error handled in hook
      }
      return
    }

    if (message.trim() && !disabled) {
      onSend(message.trim())
      setMessage('')
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      setSelectedFile(file)
    }
  }

  const clearFile = () => {
    setSelectedFile(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  return (
    <div className="space-y-2">
      {selectedFile && (
        <div className="glass-card p-3 flex items-center justify-between animate-fade-in">
          <div className="flex items-center gap-2">
            <Paperclip className="w-4 h-4 text-cyan-400" />
            <span className="text-sm truncate max-w-[200px]">{selectedFile.name}</span>
          </div>
          <button
            onClick={clearFile}
            className="p-1 hover:bg-white/10 rounded-lg transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {uploadStatus && (
        <div className={`flex items-center gap-2 text-sm p-2 rounded-lg animate-fade-in ${
          uploadStatus.includes('Error') 
            ? 'text-red-400 bg-red-500/10' 
            : 'text-green-400 bg-green-500/10'
        }`}>
          {uploadStatus.includes('Error') ? (
            <AlertCircle className="w-4 h-4" />
          ) : (
            <CheckCircle className="w-4 h-4" />
          )}
          {uploadStatus}
        </div>
      )}

      <form onSubmit={handleSubmit} className="relative">
        <div className="glass-card p-2 flex items-end gap-2">
          <input
            ref={fileInputRef}
            type="file"
            accept=".txt,.pdf,.md"
            onChange={handleFileSelect}
            className="hidden"
          />
          
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            disabled={disabled || isUploading}
            className="p-2 hover:bg-white/10 rounded-lg transition-colors disabled:opacity-50"
          >
            <Paperclip className="w-5 h-5" />
          </button>

          <textarea
            ref={textareaRef}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={selectedFile ? "Click send to upload file..." : "Type your message..."}
            disabled={disabled || isUploading}
            rows={1}
            className="flex-1 bg-transparent border-none outline-none resize-none text-white placeholder-white/40 py-2 px-2 disabled:opacity-50"
          />

          <button
            type="submit"
            disabled={disabled || isUploading || (!message.trim() && !selectedFile)}
            className="p-2 bg-gradient-to-r from-violet-500 to-purple-600 rounded-lg hover:opacity-90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isUploading ? (
              <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
            ) : (
              <Send className="w-5 h-5" />
            )}
          </button>
        </div>
      </form>
    </div>
  )
}
