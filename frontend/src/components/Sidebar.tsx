import React, { useState } from 'react'
import { Plus, Trash2, MessageSquare, X, ChevronRight } from 'lucide-react'

interface Session {
  id: string
  name: string
  messages: Array<{ role: string; content: string; timestamp: string }>
  created_at: string
  updated_at: string
}

interface SidebarProps {
  sessions: Session[]
  currentSessionId: string
  onSelectSession: (sessionId: string) => void
  onCreateSession: () => void
  onDeleteSession: (sessionId: string) => void
  isOpen: boolean
  onClose: () => void
}

export const Sidebar: React.FC<SidebarProps> = ({
  sessions,
  currentSessionId,
  onSelectSession,
  onCreateSession,
  onDeleteSession,
  isOpen,
  onClose
}) => {
  const [isHovered, setIsHovered] = useState(false)
  const isExpanded = isHovered || isOpen

  return (
    <>
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={onClose}
        />
      )}
      
      {/* Hover trigger zone - left edge */}
      <div 
        className="fixed left-0 top-0 w-4 h-full z-30 hidden lg:block"
        onMouseEnter={() => setIsHovered(true)}
      />
      
      <aside
        className={`
          fixed lg:static top-0 left-0 h-full z-50
          glass-card rounded-none lg:rounded-2xl
          flex flex-col overflow-hidden
          transition-all duration-300 ease-in-out
          ${isExpanded ? 'w-64' : 'w-0 lg:w-12'}
          ${isExpanded ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
        `}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => {
          setIsHovered(false)
          if (isOpen) onClose()
        }}
      >
        {/* Collapsed state indicator */}
        {!isExpanded && (
          <div className="hidden lg:flex flex-col items-center py-4 h-full">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center mb-4">
              <MessageSquare className="w-4 h-4 text-white" />
            </div>
            <div className="flex-1 flex flex-col items-center gap-2 py-2">
              {sessions.slice(0, 5).map((session, index) => (
                <div
                  key={session.id}
                  className={`
                    w-8 h-8 rounded-lg flex items-center justify-center text-xs
                    ${currentSessionId === session.id 
                      ? 'bg-white/20 text-white' 
                      : 'bg-white/5 text-white/50'
                    }
                  `}
                >
                  {index + 1}
                </div>
              ))}
            </div>
            <ChevronRight className="w-4 h-4 text-white/30" />
          </div>
        )}

        {/* Expanded content */}
        <div className={`flex flex-col h-full ${isExpanded ? 'opacity-100' : 'opacity-0'} transition-opacity duration-200`}>
          <div className="flex items-center justify-between p-4 border-b border-white/10">
            <h2 className="font-semibold text-white/90">会话列表</h2>
            <button
              onClick={onClose}
              className="lg:hidden p-2 hover:bg-white/10 rounded-lg transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          <button
            onClick={onCreateSession}
            className="m-4 mb-2 flex items-center gap-2 px-4 py-3 
                       bg-gradient-to-r from-violet-500/20 to-purple-500/20
                       hover:from-violet-500/30 hover:to-purple-500/30
                       border border-white/10 rounded-xl transition-all"
          >
            <Plus className="w-4 h-4" />
            <span className="text-sm">新建会话</span>
          </button>

          <div className="flex-1 overflow-y-auto px-2 py-2 space-y-1">
            {sessions.length === 0 ? (
              <div className="text-center text-white/40 text-sm py-8">
                暂无会话
              </div>
            ) : (
              sessions.map((session) => (
                <div
                  key={session.id}
                  className={`
                    group flex items-center gap-3 px-3 py-2.5 rounded-xl cursor-pointer
                    transition-all
                    ${currentSessionId === session.id 
                      ? 'bg-white/15 border border-white/20' 
                      : 'hover:bg-white/5'
                    }
                  `}
                  onClick={() => {
                    onSelectSession(session.id)
                    onClose()
                  }}
                >
                  <MessageSquare className="w-4 h-4 text-white/50 flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-white/90 truncate">{session.name}</p>
                    <p className="text-xs text-white/40">
                      {session.messages.length} 条消息
                    </p>
                  </div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      onDeleteSession(session.id)
                    }}
                    className="opacity-0 group-hover:opacity-100 p-1.5 
                             hover:bg-red-500/20 rounded-lg transition-all"
                    title="删除会话"
                  >
                    <Trash2 className="w-3.5 h-3.5 text-red-400" />
                  </button>
                </div>
              ))
            )}
          </div>

          <div className="p-4 border-t border-white/10">
            <p className="text-xs text-white/30 text-center">
              共 {sessions.length} 个会话
            </p>
          </div>
        </div>
      </aside>
    </>
  )
}
