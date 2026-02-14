import { useState, useCallback, useEffect } from 'react'
import {
  BackgroundEffect,
  ChatWindow,
  InputBox,
  Navbar,
  Sidebar,
} from './components'
import { useChat } from './hooks/useChat'
import { useRAG } from './hooks/useRAG'
import { useSessions } from './hooks/useSessions'

function App() {
  const [currentSessionId, setCurrentSessionId] = useState<string>('')
  const [sidebarOpen, setSidebarOpen] = useState(false)
  
  const { sessions, fetchSessions, createSession, deleteSession } = useSessions()
  const { messages, isLoading, sendMessage, clearMessages } = useChat(currentSessionId)
  const { enabled: ragEnabled, loading: ragLoading, toggle: toggleRAG } = useRAG()

  useEffect(() => {
    if (!currentSessionId && sessions.length > 0) {
      setCurrentSessionId(sessions[0].id)
    }
  }, [sessions, currentSessionId])

  const handleCreateSession = useCallback(async () => {
    const session = await createSession()
    if (session) {
      setCurrentSessionId(session.id)
      clearMessages()
    }
  }, [createSession, clearMessages])

  const handleSelectSession = useCallback((sessionId: string) => {
    setCurrentSessionId(sessionId)
  }, [])

  const handleDeleteSession = useCallback(async (sessionId: string) => {
    const confirmed = window.confirm('确定要删除这个会话吗？')
    if (!confirmed) return
    
    await deleteSession(sessionId)
    if (sessionId === currentSessionId) {
      const remainingSessions = sessions.filter(s => s.id !== sessionId)
      if (remainingSessions.length > 0) {
        setCurrentSessionId(remainingSessions[0].id)
      } else {
        handleCreateSession()
      }
    }
  }, [deleteSession, currentSessionId, sessions, handleCreateSession])

  const handleSend = useCallback(async (message: string) => {
    if (!currentSessionId) {
      const session = await createSession()
      if (session) {
        setCurrentSessionId(session.id)
      }
    }
    await sendMessage(message)
    fetchSessions()
  }, [currentSessionId, createSession, sendMessage, fetchSessions])

  return (
    <div className="h-screen flex relative overflow-hidden">
      <BackgroundEffect />
      
      <div className="flex-1 flex">
        <Sidebar
          sessions={sessions}
          currentSessionId={currentSessionId}
          onSelectSession={handleSelectSession}
          onCreateSession={handleCreateSession}
          onDeleteSession={handleDeleteSession}
          isOpen={sidebarOpen}
          onClose={() => setSidebarOpen(false)}
        />

        <div className="flex-1 flex flex-col h-screen overflow-hidden">
          <Navbar 
            onClearSession={() => setSidebarOpen(!sidebarOpen)}
            ragEnabled={ragEnabled}
            onRAGToggle={toggleRAG}
            ragLoading={ragLoading}
          />
          
          <main className="flex-1 flex flex-col min-h-0 max-w-4xl mx-auto w-full px-4 pt-20 pb-4">
            {ragEnabled && (
              <div className="mb-4 flex-shrink-0 glass-card px-4 py-2 text-sm text-cyan-300 flex items-center gap-2">
                <span className="w-2 h-2 bg-cyan-400 rounded-full animate-pulse" />
                RAG 模式已开启 - 可以上传文档进行问答
              </div>
            )}
            <ChatWindow messages={messages} isLoading={isLoading} />
            <div className="mt-4 flex-shrink-0">
              <InputBox onSend={handleSend} disabled={isLoading} />
            </div>
          </main>

          <footer className="flex-shrink-0 text-center py-2 text-white/30 text-xs">
            Powered by SiliconFlow & LangChain
          </footer>
        </div>
      </div>
    </div>
  )
}

export default App
