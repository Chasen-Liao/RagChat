import React from 'react'
import { Sparkles, Trash2, Menu } from 'lucide-react'

interface NavbarProps {
  onClearSession: () => void
}

export const Navbar: React.FC<NavbarProps> = ({ onClearSession }) => {
  return (
    <nav className="fixed top-0 left-0 right-0 z-50 px-4 py-3">
      <div className="glass-card px-6 py-3 flex items-center justify-between max-w-5xl mx-auto">
        <div className="flex items-center gap-3">
          <button className="lg:hidden p-2 hover:bg-white/10 rounded-lg">
            <Menu className="w-5 h-5" />
          </button>
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center">
              <Sparkles className="w-4 h-4 text-white" />
            </div>
            <span className="font-semibold text-lg text-glow">RAG Chat</span>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={onClearSession}
            className="flex items-center gap-2 px-4 py-2 text-sm text-white/70 hover:text-white hover:bg-white/10 rounded-lg transition-all"
          >
            <Trash2 className="w-4 h-4" />
            <span className="hidden sm:inline">Clear</span>
          </button>
        </div>
      </div>
    </nav>
  )
}
