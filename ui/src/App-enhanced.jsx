import React, { useState, useEffect, useRef } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Textarea } from '@/components/ui/textarea.jsx'
import { Separator } from '@/components/ui/separator.jsx'
import { ScrollArea } from '@/components/ui/scroll-area.jsx'
import io from 'socket.io-client'
import './App.css'

// Icons
const Icons = {
  Plus: () => <span>+</span>,
  Settings: () => <span>⚙️</span>,
  Terminal: () => <span>💻</span>,
  Play: () => <span>▶️</span>,
  Pause: () => <span>⏸️</span>,
  Stop: () => <span>⏹️</span>,
  Send: () => <span>📤</span>,
  Folder: () => <span>📁</span>,
  Code: () => <span>💻</span>,
  Activity: () => <span>📊</span>,
  ChevronLeft: () => <span>←</span>,
  ChevronRight: () => <span>→</span>,
  Maximize2: () => <span>⛶</span>,
  Minimize2: () => <span>⊟</span>,
  Wifi: () => <span>📶</span>,
  WifiOff: () => <span>📵</span>
}

// Terminal Component
const VirtualTerminal = ({ sessionId, isActive }) => {
  const terminalRef = useRef(null)
  const [output, setOutput] = useState('')
  const [input, setInput] = useState('')
  const [socket, setSocket] = useState(null)

  useEffect(() => {
    if (isActive && sessionId) {
      // Connect to WebSocket
      const newSocket = io('http://localhost:5001')
      setSocket(newSocket)

      // Join session room
      newSocket.emit('join_session', { session_id: sessionId })

      // Listen for terminal output
      newSocket.on('terminal_output', (data) => {
        if (data.session_id === sessionId) {
          setOutput(prev => prev + data.output)
        }
      })

      return () => {
        newSocket.emit('leave_session', { session_id: sessionId })
        newSocket.disconnect()
      }
    }
  }, [sessionId, isActive])

  useEffect(() => {
    // Auto-scroll terminal
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight
    }
  }, [output])

  const handleInputSubmit = (e) => {
    e.preventDefault()
    if (socket && input.trim()) {
      socket.emit('terminal_input', {
        session_id: sessionId,
        input: input + '\n'
      })
      setInput('')
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleInputSubmit(e)
    }
  }

  return (
    <div className="terminal-container">
      <div className="terminal-header">
        <div className="terminal-title">
          <Icons.Terminal />
          <span>Terminal - Session {sessionId?.slice(0, 8)}</span>
        </div>
        <div className="terminal-controls">
          <Button size="sm" variant="ghost">
            <Icons.Minimize2 />
          </Button>
          <Button size="sm" variant="ghost">
            <Icons.Maximize2 />
          </Button>
        </div>
      </div>
      <div 
        ref={terminalRef}
        className="terminal-output"
        style={{
          backgroundColor: '#000000',
          color: '#00ff00',
          fontFamily: 'monospace',
          fontSize: '14px',
          padding: '12px',
          height: '300px',
          overflowY: 'auto',
          whiteSpace: 'pre-wrap'
        }}
      >
        {output || 'Terminal ready. Type commands to interact with Amplifier...\n'}
      </div>
      <form onSubmit={handleInputSubmit} className="terminal-input-form">
        <Input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type command and press Enter..."
          className="terminal-input"
          style={{
            backgroundColor: '#111111',
            color: '#ffffff',
            border: '1px solid #333333',
            fontFamily: 'monospace'
          }}
        />
        <Button type="submit" size="sm">
          <Icons.Send />
        </Button>
      </form>
    </div>
  )
}

// Main App Component
function App() {
  const [currentView, setCurrentView] = useState('dashboard')
  const [selectedSession, setSelectedSession] = useState(null)
  const [sessions, setSessions] = useState([])
  const [backendStatus, setBackendStatus] = useState('disconnected')
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)
  const [messages, setMessages] = useState([])
  const [newMessage, setNewMessage] = useState('')

  // Check backend health
  useEffect(() => {
    const checkHealth = async () => {
      try {
        const response = await fetch('http://localhost:5001/api/health')
        if (response.ok) {
          const data = await response.json()
          setBackendStatus(data.status === 'healthy' ? 'connected' : 'error')
        } else {
          setBackendStatus('error')
        }
      } catch (error) {
        setBackendStatus('disconnected')
      }
    }

    checkHealth()
    const interval = setInterval(checkHealth, 10000) // Check every 10 seconds
    return () => clearInterval(interval)
  }, [])

  // Load sessions
  useEffect(() => {
    const loadSessions = async () => {
      try {
        const response = await fetch('http://localhost:5001/api/sessions')
        if (response.ok) {
          const data = await response.json()
          setSessions(data.sessions || [])
        }
      } catch (error) {
        console.error('Failed to load sessions:', error)
      }
    }

    if (backendStatus === 'connected') {
      loadSessions()
      const interval = setInterval(loadSessions, 5000) // Refresh every 5 seconds
      return () => clearInterval(interval)
    }
  }, [backendStatus])

  // Load messages for selected session
  useEffect(() => {
    const loadMessages = async () => {
      if (selectedSession) {
        try {
          const response = await fetch(`http://localhost:5001/api/sessions/${selectedSession.session_id}`)
          if (response.ok) {
            const data = await response.json()
            setMessages(data.messages || [])
          }
        } catch (error) {
          console.error('Failed to load messages:', error)
        }
      }
    }

    loadMessages()
  }, [selectedSession])

  const createNewSession = async () => {
    const sessionName = prompt('Enter session name:')
    if (!sessionName) return

    try {
      const response = await fetch('http://localhost:5001/api/sessions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          name: sessionName
        })
      })

      if (response.ok) {
        const data = await response.json()
        setSessions(prev => [...prev, data.session])
        setSelectedSession(data.session)
        setCurrentView('session')
      }
    } catch (error) {
      console.error('Failed to create session:', error)
    }
  }

  const sendMessage = async (e) => {
    e.preventDefault()
    if (!newMessage.trim() || !selectedSession) return

    try {
      const response = await fetch(`http://localhost:5001/api/sessions/${selectedSession.session_id}/messages`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          message: newMessage
        })
      })

      if (response.ok) {
        setNewMessage('')
        // Messages will be updated by the periodic refresh
      }
    } catch (error) {
      console.error('Failed to send message:', error)
    }
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'connected':
        return <Icons.Wifi />
      case 'disconnected':
        return <Icons.WifiOff />
      default:
        return <Icons.WifiOff />
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'active':
        return '#10b981'
      case 'idle':
        return '#f59e0b'
      case 'error':
        return '#ef4444'
      default:
        return '#888888'
    }
  }

  return (
    <div className="app">
      {/* Sidebar */}
      <div className={`sidebar ${sidebarCollapsed ? 'collapsed' : ''}`}>
        <div className="sidebar-header">
          <div className="app-title">
            <span className="app-icon">⚡</span>
            {!sidebarCollapsed && <span>Amplifier UI</span>}
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
            className="collapse-btn"
          >
            {sidebarCollapsed ? <Icons.ChevronRight /> : <Icons.ChevronLeft />}
          </Button>
        </div>

        {!sidebarCollapsed && (
          <>
            <div className="sidebar-nav">
              <Button
                variant={currentView === 'dashboard' ? 'default' : 'ghost'}
                className="nav-btn"
                onClick={() => setCurrentView('dashboard')}
              >
                <Icons.Activity />
                <span>Dashboard</span>
              </Button>
              <Button
                variant={currentView === 'sessions' ? 'default' : 'ghost'}
                className="nav-btn"
                onClick={() => setCurrentView('sessions')}
              >
                <Icons.Terminal />
                <span>Sessions</span>
              </Button>
            </div>

            <div className="sidebar-section">
              <div className="section-header">
                <h3>SESSIONS ({sessions.length})</h3>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={createNewSession}
                  className="btn-icon"
                >
                  <Icons.Plus />
                </Button>
              </div>

              <div className="session-list">
                {sessions.map((session) => (
                  <div
                    key={session.session_id}
                    className={`session-item ${selectedSession?.session_id === session.session_id ? 'active' : ''}`}
                    onClick={() => {
                      setSelectedSession(session)
                      setCurrentView('session')
                    }}
                  >
                    <div className="session-header">
                      <div
                        className="status-dot"
                        style={{ backgroundColor: getStatusColor(session.status) }}
                      />
                      <span className="session-name">{session.name}</span>
                    </div>
                    <div className="session-preview">
                      Status: {session.status} | Messages: {session.message_count}
                    </div>
                    <div className="session-meta">
                      <span className="session-duration">
                        ${session.cost.toFixed(2)}
                      </span>
                      <div className="session-agents">
                        {session.agents.map((_, i) => (
                          <div key={i} className="agent-dot" />
                        ))}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="sidebar-footer">
              <div className="connection-status">
                <span className="status-indicator">
                  {getStatusIcon(backendStatus)}
                </span>
                <span className="status-text">
                  {backendStatus === 'connected' ? 'Connected to Amplifier' : 'Backend Disconnected'}
                </span>
              </div>
              <div className="session-stats">
                <div className="stat">
                  <span className="stat-value">{sessions.filter(s => s.status === 'active').length}</span>
                  <span className="stat-label">Active</span>
                </div>
                <div className="stat">
                  <span className="stat-value">
                    ${sessions.reduce((sum, s) => sum + s.cost, 0).toFixed(2)}
                  </span>
                  <span className="stat-label">Total</span>
                </div>
              </div>
            </div>
          </>
        )}
      </div>

      {/* Main Content */}
      <div className="main-content">
        <div className="content-header">
          <div className="breadcrumb">
            {currentView === 'dashboard' && 'Outcomes Dashboard'}
            {currentView === 'sessions' && 'Session Management'}
            {currentView === 'session' && selectedSession && `Session: ${selectedSession.name}`}
          </div>
          <div className="header-actions">
            <Button variant="secondary" size="sm">
              <Icons.Settings />
              Settings
            </Button>
          </div>
        </div>

        <div className="content-body">
          {currentView === 'dashboard' && (
            <div className="dashboard-container">
              <div className="dashboard-header">
                <div className="dashboard-title">
                  <h1>Amplifier Enhanced Dashboard</h1>
                  <p>Real-time session management with virtual terminals</p>
                </div>
              </div>

              <div className="metrics-grid">
                <Card>
                  <CardHeader>
                    <CardTitle>Active Sessions</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="metric-value">
                      {sessions.filter(s => s.status === 'active').length}
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Total Cost</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="metric-value">
                      ${sessions.reduce((sum, s) => sum + s.cost, 0).toFixed(2)}
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Backend Status</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="metric-value">
                      <Badge variant={backendStatus === 'connected' ? 'default' : 'destructive'}>
                        {backendStatus}
                      </Badge>
                    </div>
                  </CardContent>
                </Card>
              </div>

              <Card className="sessions-overview">
                <CardHeader>
                  <CardTitle>Session Overview</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="sessions-table">
                    {sessions.map((session) => (
                      <div key={session.session_id} className="session-row">
                        <div className="session-info">
                          <div
                            className="status-indicator"
                            style={{ backgroundColor: getStatusColor(session.status) }}
                          />
                          <div>
                            <div className="session-name">{session.name}</div>
                            <div className="session-id">{session.session_id.slice(0, 8)}</div>
                          </div>
                        </div>
                        <div className="session-metrics">
                          <span>Status: {session.status}</span>
                          <span>Cost: ${session.cost.toFixed(2)}</span>
                          <span>Messages: {session.message_count}</span>
                          <span>Terminal: {session.terminal_active ? '✅' : '❌'}</span>
                        </div>
                        <Button
                          size="sm"
                          onClick={() => {
                            setSelectedSession(session)
                            setCurrentView('session')
                          }}
                        >
                          Open
                        </Button>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

          {currentView === 'session' && selectedSession && (
            <div className="session-container">
              <div className="session-header">
                <h2>{selectedSession.name}</h2>
                <div className="session-badges">
                  <Badge variant={selectedSession.status === 'active' ? 'default' : 'secondary'}>
                    {selectedSession.status}
                  </Badge>
                  <Badge variant="outline">
                    ${selectedSession.cost.toFixed(2)}
                  </Badge>
                </div>
              </div>

              <div className="session-layout">
                {/* Chat Area */}
                <div className="chat-area">
                  <Card>
                    <CardHeader>
                      <CardTitle>AI Assistant Chat</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <ScrollArea className="chat-messages" style={{ height: '300px' }}>
                        {messages.map((message, index) => (
                          <div
                            key={index}
                            className={`message ${message.role}`}
                          >
                            <div className="message-content">{message.content}</div>
                            <div className="message-timestamp">
                              {new Date(message.timestamp).toLocaleTimeString()}
                            </div>
                          </div>
                        ))}
                      </ScrollArea>
                      <form onSubmit={sendMessage} className="chat-input-form">
                        <Textarea
                          value={newMessage}
                          onChange={(e) => setNewMessage(e.target.value)}
                          placeholder="Ask the AI assistant for help..."
                          className="chat-input"
                        />
                        <Button type="submit" disabled={!newMessage.trim()}>
                          <Icons.Send />
                          Send
                        </Button>
                      </form>
                    </CardContent>
                  </Card>
                </div>

                {/* Terminal Area */}
                <div className="terminal-area">
                  <Card>
                    <CardHeader>
                      <CardTitle>Virtual Terminal</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <VirtualTerminal
                        sessionId={selectedSession.session_id}
                        isActive={currentView === 'session'}
                      />
                    </CardContent>
                  </Card>
                </div>
              </div>
            </div>
          )}

          {currentView === 'sessions' && (
            <div className="sessions-management">
              <div className="sessions-header">
                <h2>Session Management</h2>
                <Button onClick={createNewSession}>
                  <Icons.Plus />
                  New Session
                </Button>
              </div>

              <div className="sessions-grid">
                {sessions.map((session) => (
                  <Card key={session.session_id} className="session-card">
                    <CardHeader>
                      <CardTitle className="session-card-title">
                        <div
                          className="status-dot"
                          style={{ backgroundColor: getStatusColor(session.status) }}
                        />
                        {session.name}
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="session-details">
                        <p><strong>Status:</strong> {session.status}</p>
                        <p><strong>Cost:</strong> ${session.cost.toFixed(2)}</p>
                        <p><strong>Messages:</strong> {session.message_count}</p>
                        <p><strong>Terminal:</strong> {session.terminal_active ? 'Active' : 'Inactive'}</p>
                        <p><strong>Created:</strong> {new Date(session.created_at).toLocaleString()}</p>
                      </div>
                      <div className="session-actions">
                        <Button
                          size="sm"
                          onClick={() => {
                            setSelectedSession(session)
                            setCurrentView('session')
                          }}
                        >
                          Open
                        </Button>
                        <Button
                          size="sm"
                          variant="destructive"
                          onClick={async () => {
                            if (confirm('Delete this session?')) {
                              try {
                                await fetch(`http://localhost:5001/api/sessions/${session.session_id}`, {
                                  method: 'DELETE'
                                })
                                setSessions(prev => prev.filter(s => s.session_id !== session.session_id))
                              } catch (error) {
                                console.error('Failed to delete session:', error)
                              }
                            }
                          }}
                        >
                          Delete
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default App
