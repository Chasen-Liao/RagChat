import React from 'react'

interface GlassCardProps {
  children: React.ReactNode
  className?: string
}

export const GlassCard: React.FC<GlassCardProps> = ({ children, className = '' }) => {
  return (
    <div className={`glass-card glass-shadow ${className}`}>
      {children}
    </div>
  )
}
