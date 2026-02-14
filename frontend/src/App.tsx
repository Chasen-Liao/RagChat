import { useState } from 'react'
import {
  BackgroundEffect,
  ChatWindow,
  InputBox,
  Navbar,
} from './components'
import { useChat } from './hooks/useChat'

function App() {
  const [sessionId] = useState('default')
  const { messages, isLoading, sendMessage, clearSession } = useChat(sessionId)

  return (
    <div className="min-h-screen flex flex-col relative">
      <BackgroundEffect />
      <Navbar onClearSession={clearSession} />
      
      <main className="flex-1 flex flex-col max-w-4xl mx-auto w-full px-4 pt-20 pb-6">
        <ChatWindow messages={messages} isLoading={isLoading} />
        <div className="mt-4">
          <InputBox onSend={sendMessage} disabled={isLoading} />
        </div>
      </main>

      <footer className="text-center py-4 text-white/30 text-sm">
        Powered by SiliconFlow & LangChain
      </footer>
    </div>
  )
}

export default App
