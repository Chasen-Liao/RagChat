import { useState, useCallback, useEffect } from 'react'

const API_BASE = '/api'

interface Message {
  role: string
  content: string
  timestamp: string
}

interface Session {
  id: string
  name: string
  messages: Message[]
  created_at: string
  updated_at: string
}

export function useSessions() {
  const [sessions, setSessions] = useState<Session[]>([])
  const [loading, setLoading] = useState(false)

  const fetchSessions = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE}/sessions`)
      if (response.ok) {
        const data = await response.json()
        setSessions(data.sessions)
      }
    } catch (err) {
      console.error('Failed to fetch sessions:', err)
    }
  }, [])

  const createSession = useCallback(async (name?: string): Promise<Session | null> => {
    setLoading(true)
    try {
      const response = await fetch(`${API_BASE}/sessions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name })
      })
      if (response.ok) {
        const session = await response.json()
        await fetchSessions()
        return session
      }
    } catch (err) {
      console.error('Failed to create session:', err)
    } finally {
      setLoading(false)
    }
    return null
  }, [fetchSessions])

  const deleteSession = useCallback(async (sessionId: string): Promise<boolean> => {
    try {
      const response = await fetch(`${API_BASE}/sessions/${sessionId}`, {
        method: 'DELETE'
      })
      if (response.ok) {
        await fetchSessions()
        return true
      }
    } catch (err) {
      console.error('Failed to delete session:', err)
    }
    return false
  }, [fetchSessions])

  useEffect(() => {
    fetchSessions()
  }, [fetchSessions])

  return {
    sessions,
    loading,
    fetchSessions,
    createSession,
    deleteSession
  }
}
