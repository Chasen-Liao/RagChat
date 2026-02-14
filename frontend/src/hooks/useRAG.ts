import { useState, useCallback, useEffect } from 'react'

const API_BASE = '/api'

export function useRAG() {
  const [enabled, setEnabled] = useState(false)
  const [loading, setLoading] = useState(false)

  const fetchStatus = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE}/rag/status`)
      if (response.ok) {
        const data = await response.json()
        setEnabled(data.enabled)
      }
    } catch (err) {
      console.error('Failed to fetch RAG status:', err)
    }
  }, [])

  const enable = useCallback(async () => {
    setLoading(true)
    try {
      const response = await fetch(`${API_BASE}/rag/enable`, { method: 'POST' })
      if (response.ok) {
        setEnabled(true)
      }
    } catch (err) {
      console.error('Failed to enable RAG:', err)
    } finally {
      setLoading(false)
    }
  }, [])

  const disable = useCallback(async () => {
    setLoading(true)
    try {
      const response = await fetch(`${API_BASE}/rag/disable`, { method: 'POST' })
      if (response.ok) {
        setEnabled(false)
      }
    } catch (err) {
      console.error('Failed to disable RAG:', err)
    } finally {
      setLoading(false)
    }
  }, [])

  const toggle = useCallback(async () => {
    if (enabled) {
      await disable()
    } else {
      await enable()
    }
  }, [enabled, enable, disable])

  useEffect(() => {
    fetchStatus()
  }, [fetchStatus])

  return {
    enabled,
    loading,
    enable,
    disable,
    toggle,
    refreshStatus: fetchStatus
  }
}
