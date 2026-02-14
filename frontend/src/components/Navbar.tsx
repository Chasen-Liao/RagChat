import React from 'react'
import { Sparkles, Trash2, Menu, Database, DatabaseZap } from 'lucide-react'

interface NavbarProps {
  onClearSession: () => void
  ragEnabled: boolean
  onRAGToggle: () => void
  ragLoading: boolean
}

export const Navbar: React.FC<NavbarProps> = ({ 
  onClearSession, 
  ragEnabled, 
  onRAGToggle,
  ragLoading 
}) => {
  return (
    <nav className="fixed top-0 left-0 right-0 z-50 px-4 py-3">
      <div className="glass-card px-6 py-3 flex items-center justify-between max-w-5xl mx-auto">
        <div className="flex items-center gap-3">
          <button 
            onClick={onClearSession}
            className="p-2 hover:bg-white/10 rounded-lg transition-colors"
            title="切换会话列表"
          >
            <Menu className="w-5 h-5" />
          </button>
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center">
              <Sparkles className="w-4 h-4 text-white" />
            </div>
            <span className="font-semibold text-lg text-glow hidden sm:inline">RAG Chat</span>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={onRAGToggle}
            disabled={ragLoading}
            className={`flex items-center gap-2 px-4 py-2 text-sm rounded-lg transition-all ${
              ragEnabled 
                ? 'bg-cyan-500/20 text-cyan-300 hover:bg-cyan-500/30' 
                : 'text-white/70 hover:text-white hover:bg-white/10'
            }`}
            title={ragEnabled ? 'RAG enabled - click to disable' : 'RAG disabled - click to enable'}
          >
            {ragLoading ? (
              <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
            ) : ragEnabled ? (
              <DatabaseZap className="w-4 h-4" />
            ) : (
              <Database className="w-4 h-4" />
            )}
            <span className="hidden sm:inline">RAG</span>
            <span className={`w-2 h-2 rounded-full ${ragEnabled ? 'bg-cyan-400' : 'bg-white/30'}`} />
          </button>
        </div>
      </div>
    </nav>
  )
}
