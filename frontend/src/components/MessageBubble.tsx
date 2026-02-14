import React, { useEffect, useRef } from 'react'
import ReactMarkdown from 'react-markdown'
import { User, Bot, Loader2 } from 'lucide-react'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  isStreaming?: boolean
}

interface MessageBubbleProps {
  message: Message
}

export const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
  const isUser = message.role === 'user'
  const messageRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (messageRef.current) {
      messageRef.current.scrollIntoView({ behavior: 'smooth', block: 'end' })
    }
  }, [message.content])

  return (
    <div
      ref={messageRef}
      className={`flex gap-4 animate-slide-up ${isUser ? 'flex-row-reverse' : ''}`}
    >
      <div
        className={`
          flex-shrink-0 w-10 h-10 rounded-xl flex items-center justify-center
          ${isUser 
            ? 'bg-gradient-to-br from-violet-500 to-purple-600' 
            : 'bg-gradient-to-br from-cyan-500 to-blue-600'
          }
          shadow-lg
        `}
      >
        {isUser ? (
          <User className="w-5 h-5 text-white" />
        ) : (
          <Bot className="w-5 h-5 text-white" />
        )}
      </div>

      <div
        className={`
          flex-1 max-w-[75%] glass-card p-4
          ${isUser ? 'bg-white/15' : 'bg-white/5'}
        `}
      >
        <div className="prose prose-invert prose-sm max-w-none">
          {message.content ? (
            <ReactMarkdown
              components={{
                code: ({ className, children, ...props }) => {
                  const isInline = !className
                  return isInline ? (
                    <code className="bg-white/10 px-1.5 py-0.5 rounded text-cyan-300" {...props}>
                      {children}
                    </code>
                  ) : (
                    <code className={className} {...props}>
                      {children}
                    </code>
                  )
                },
                p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
                ul: ({ children }) => <ul className="list-disc pl-4 mb-2">{children}</ul>,
                ol: ({ children }) => <ol className="list-decimal pl-4 mb-2">{children}</ol>,
              }}
            >
              {message.content}
            </ReactMarkdown>
          ) : (
            <div className="flex items-center gap-2 text-white/50">
              <Loader2 className="w-4 h-4 animate-spin" />
              <span>Thinking...</span>
            </div>
          )}
        </div>

        {message.isStreaming && message.content && (
          <span className="inline-block w-2 h-4 bg-cyan-400 animate-pulse ml-1" />
        )}
      </div>
    </div>
  )
}
