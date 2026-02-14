import { useState, useCallback, useEffect } from 'react'

const API_BASE = '/api'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  isStreaming?: boolean
  sources?: Source[]
  cached?: boolean
  retrieved?: boolean
}

interface Source {
  content: string
  metadata: Record<string, unknown>
}

interface ChatResponse {
  answer: string
  sources: Source[]
  cached?: boolean
  retrieved?: boolean
}

interface SessionMessage {
  role: string
  content: string
  timestamp: string
}

interface SessionData {
  id: string
  name: string
  messages: SessionMessage[]
  created_at: string
  updated_at: string
}

export function useChat(sessionId: string = '') {
  const [messages, setMessages] = useState<Message[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const generateId = () => Math.random().toString(36).substring(2, 15)

  // Load session messages when sessionId changes
  useEffect(() => {
    if (!sessionId) {
      setMessages([])
      return
    }

    const loadSession = async () => {
      try {
        const response = await fetch(`${API_BASE}/sessions/${sessionId}`)
        if (response.ok) {
          const session: SessionData = await response.json()
          const loadedMessages: Message[] = session.messages.map((msg, index) => ({
            id: `loaded-${index}`,
            role: msg.role as 'user' | 'assistant',
            content: msg.content,
            isStreaming: false
          }))
          setMessages(loadedMessages)
        } else {
          setMessages([])
        }
      } catch (err) {
        console.error('Failed to load session:', err)
        setMessages([])
      }
    }

    loadSession()
  }, [sessionId])

  const sendMessage = useCallback(async (content: string) => {
    if (!content.trim() || isLoading || !sessionId) return

    const userMessage: Message = {
      id: generateId(),
      role: 'user',
      content: content.trim()
    }

    setMessages(prev => [...prev, userMessage])
    setIsLoading(true)
    setError(null)

    const assistantMessage: Message = {
      id: generateId(),
      role: 'assistant',
      content: '',
      isStreaming: true
    }

    setMessages(prev => [...prev, assistantMessage])

    try {
      const response = await fetch(`${API_BASE}/chat/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: content.trim(), session_id: sessionId })
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const reader = response.body?.getReader()
      const decoder = new TextDecoder()

      if (!reader) {
        throw new Error('No reader available')
      }

      let accumulatedContent = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const chunk = decoder.decode(value)
        const lines = chunk.split('\n')

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6)
            if (data === '[DONE]') {
              setMessages(prev =>
                prev.map(m =>
                  m.id === assistantMessage.id
                    ? { ...m, isStreaming: false }
                    : m
                )
              )
            } else {
              try {
                const parsed = JSON.parse(data)
                if (parsed.content) {
                  accumulatedContent += parsed.content
                  setMessages(prev =>
                    prev.map(m =>
                      m.id === assistantMessage.id
                        ? { ...m, content: accumulatedContent }
                        : m
                    )
                  )
                }
                if (parsed.error) {
                  throw new Error(parsed.error)
                }
              } catch {
                // Skip unparseable lines
              }
            }
          }
        }
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error'
      setError(errorMessage)
      setMessages(prev =>
        prev.map(m =>
          m.id === assistantMessage.id
            ? { ...m, content: `Error: ${errorMessage}`, isStreaming: false }
            : m
        )
      )
    } finally {
      setIsLoading(false)
    }
  }, [sessionId, isLoading])

  const clearMessages = useCallback(() => {
    setMessages([])
    setError(null)
  }, [])

  return {
    messages,
    isLoading,
    error,
    sendMessage,
    clearMessages,
  }
}

export function useFileUpload() {
  const [isUploading, setIsUploading] = useState(false)
  const [uploadStatus, setUploadStatus] = useState<string | null>(null)

  const uploadFile = useCallback(async (file: File) => {
    setIsUploading(true)
    setUploadStatus(null)

    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await fetch('/api/ingest/file', {
        method: 'POST',
        body: formData
      })

      const result = await response.json()
      if (!response.ok) {
        throw new Error(result.detail || `Upload failed: ${response.status}`)
      }

      setUploadStatus(`Successfully added ${result.chunks_added} chunks`)
      return result
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Upload failed'
      setUploadStatus(`Error: ${errorMessage}`)
      throw err
    } finally {
      setIsUploading(false)
    }
  }, [])

  return { uploadFile, isUploading, uploadStatus }
}
