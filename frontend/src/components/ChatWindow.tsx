import React, { useRef, useEffect } from 'react'
import { MessageBubble } from './MessageBubble'
import { Message } from '../hooks/useChat'
import { Sparkles } from 'lucide-react'

interface ChatWindowProps {
  messages: Message[]
  isLoading: boolean
}

export const ChatWindow: React.FC<ChatWindowProps> = ({ messages, isLoading }) => {
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight
    }
  }, [messages])

  return (
    <div
      ref={containerRef}
      className="flex-1 overflow-y-auto px-4 py-6 space-y-6 scroll-smooth"
    >
      {messages.length === 0 ? (
        <div className="flex flex-col items-center justify-center h-full text-center animate-fade-in">
          <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center mb-6 shadow-xl">
            <Sparkles className="w-10 h-10 text-white" />
          </div>
          <h2 className="text-2xl font-semibold text-white mb-2">
            RAG Chat Assistant
          </h2>
          <p className="text-white/50 max-w-md">
            基于检索增强生成的智能对话助手。上传文档或直接提问，开始您的对话之旅。
          </p>
          <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-4 max-w-lg">
            {[
              { title: '文档问答', desc: '上传文档后提问' },
              { title: '知识检索', desc: '基于向量数据库' },
              { title: '流式响应', desc: '实时生成答案' },
              { title: '对话记忆', desc: '上下文连贯' },
            ].map((item) => (
              <div
                key={item.title}
                className="glass-card p-4 text-left hover:bg-white/15 transition-colors cursor-pointer"
              >
                <div className="text-white font-medium">{item.title}</div>
                <div className="text-white/40 text-sm">{item.desc}</div>
              </div>
            ))}
          </div>
        </div>
      ) : (
        messages.map((message) => (
          <MessageBubble key={message.id} message={message} />
        ))
      )}
    </div>
  )
}
