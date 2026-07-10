'use client'

import { useState, useRef, useEffect, useCallback } from 'react'
import ReactMarkdown from 'react-markdown'

// Agent definitions (mirrors backend)
const AGENTS = [
  { id: 'strategist', name: 'Strategist', icon: '🎯', color: 'text-blue-400', border: 'border-blue-500/30', bg: 'bg-blue-500/10', desc: 'Business strategy & market analysis' },
  { id: 'researcher', name: 'Researcher', icon: '🔍', color: 'text-green-400', border: 'border-green-500/30', bg: 'bg-green-500/10', desc: 'Deep market research & data' },
  { id: 'writer', name: 'Writer', icon: '✍️', color: 'text-purple-400', border: 'border-purple-500/30', bg: 'bg-purple-500/10', desc: 'Pitch decks, emails & content' },
  { id: 'analyst', name: 'Analyst', icon: '📊', color: 'text-orange-400', border: 'border-orange-500/30', bg: 'bg-orange-500/10', desc: 'Financials & unit economics' },
  { id: 'coder', name: 'Coder', icon: '💻', color: 'text-cyan-400', border: 'border-cyan-500/30', bg: 'bg-cyan-500/10', desc: 'Technical architecture & code' },
  { id: 'coach', name: 'Coach', icon: '🧠', color: 'text-pink-400', border: 'border-pink-500/30', bg: 'bg-pink-500/10', desc: 'Mentorship & accountability' },
]

interface Message {
  role: 'user' | 'assistant' | 'system'
  content: string
  agent?: string
  agentName?: string
  isStreaming?: boolean
}

export default function Dashboard() {
  const [selectedAgent, setSelectedAgent] = useState('strategist')
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isStreaming, setIsStreaming] = useState(false)
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const abortRef = useRef<AbortController | null>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const sendMessage = useCallback(async () => {
    if (!input.trim() || isStreaming) return

    const userMessage = input.trim()
    setInput('')

    // Add user message
    const userMsg: Message = { role: 'user', content: userMessage }
    setMessages(prev => [...prev, userMsg])
    setIsStreaming(true)

    // Add placeholder for assistant
    const assistantMsg: Message = {
      role: 'assistant',
      content: '',
      agent: selectedAgent,
      agentName: AGENTS.find(a => a.id === selectedAgent)?.name || 'Agent',
      isStreaming: true,
    }
    setMessages(prev => [...prev, assistantMsg])

    // Build conversation history (for context)
    const history = messages
      .filter(m => m.role === 'user' || m.role === 'assistant')
      .map(m => ({ role: m.role, content: m.content }))

    abortRef.current = new AbortController()

    try {
      // Determine API URL
      const apiUrl = '/chat'  // Same origin in production, proxied in dev

      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: userMessage,
          agent: selectedAgent,
          conversation_history: history,
          stream: true,
        }),
        signal: abortRef.current.signal,
      })

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`)
      }

      // Read SSE stream
      const reader = response.body?.getReader()
      const decoder = new TextDecoder()

      if (reader) {
        let fullContent = ''
        let buffer = ''

        while (true) {
          const { done, value } = await reader.read()
          if (done) break

          buffer += decoder.decode(value, { stream: true })
          const lines = buffer.split('\n')
          buffer = lines.pop() || ''

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const dataStr = line.slice(6).trim()
              if (dataStr === '[DONE]') continue

              try {
                const data = JSON.parse(dataStr)

                if (data.type === 'token' && data.content) {
                  fullContent += data.content
                  setMessages(prev => {
                    const updated = [...prev]
                    const lastIdx = updated.length - 1
                    updated[lastIdx] = {
                      ...updated[lastIdx],
                      content: fullContent,
                    }
                    return updated
                  })
                } else if (data.type === 'agent') {
                  setMessages(prev => {
                    const updated = [...prev]
                    const lastIdx = updated.length - 1
                    updated[lastIdx] = {
                      ...updated[lastIdx],
                      agent: data.agent,
                      agentName: data.agent_name,
                    }
                    return updated
                  })
                }
              } catch {
                // Ignore JSON parse errors for partial data
              }
            }
          }
        }

        // Mark streaming as done
        setMessages(prev => {
          const updated = [...prev]
          const lastIdx = updated.length - 1
          updated[lastIdx] = {
            ...updated[lastIdx],
            isStreaming: false,
          }
          return updated
        })
      }
    } catch (error: unknown) {
      if (error instanceof Error && error.name !== 'AbortError') {
        setMessages(prev => {
          const updated = [...prev]
          const lastIdx = updated.length - 1
          updated[lastIdx] = {
            ...updated[lastIdx],
            content: '⚠️ Failed to connect to the API. Make sure the backend is running.',
            isStreaming: false,
          }
          return updated
        })
      }
    } finally {
      setIsStreaming(false)
      abortRef.current = null
    }
  }, [input, isStreaming, selectedAgent, messages])

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const currentAgentInfo = AGENTS.find(a => a.id === selectedAgent)!

  return (
    <div className="h-screen flex flex-col bg-dark-900">
      {/* Top Bar */}
      <header className="h-14 border-b border-dark-700 bg-dark-900/95 backdrop-blur-sm flex items-center justify-between px-4 shrink-0">
        <div className="flex items-center gap-3">
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="lg:hidden p-1.5 rounded-lg hover:bg-dark-800 transition-colors"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
          <a href="/" className="flex items-center gap-2 hover:opacity-80 transition-opacity cursor-pointer">
            <div className="w-7 h-7 rounded-lg bg-accent flex items-center justify-center font-bold text-xs">
              F
            </div>
            <span className="font-semibold text-sm">FounderOS</span>
          </a>
        </div>
        <div className="flex items-center gap-2 text-xs text-dark-400">
          <span className={`w-2 h-2 rounded-full ${isStreaming ? 'bg-yellow-400 animate-pulse' : 'bg-green-400'}`} />
          {isStreaming ? `${currentAgentInfo.name} thinking...` : 'Ready'}
        </div>
      </header>

      <div className="flex-1 flex overflow-hidden">
        {/* Sidebar */}
        <aside className={`${sidebarOpen ? 'w-72' : 'w-0'} transition-all duration-300 border-r border-dark-700 bg-dark-800/50 overflow-hidden shrink-0`}>
          <div className="p-4 h-full overflow-y-auto">
            <h3 className="text-xs font-semibold text-dark-400 uppercase tracking-wider mb-3">Agents</h3>
            <div className="space-y-1.5">
              {AGENTS.map((agent) => (
                <button
                  key={agent.id}
                  onClick={() => setSelectedAgent(agent.id)}
                  className={`w-full text-left p-3 rounded-xl border transition-all duration-200 ${
                    selectedAgent === agent.id
                      ? `${agent.border} ${agent.bg} shadow-lg`
                      : 'border-transparent hover:bg-dark-700/50'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <span className="text-xl">{agent.icon}</span>
                    <div className="min-w-0">
                      <div className={`font-medium text-sm ${selectedAgent === agent.id ? agent.color : 'text-dark-200'}`}>
                        {agent.name}
                      </div>
                      <div className="text-xs text-dark-500 truncate">{agent.desc}</div>
                    </div>
                  </div>
                </button>
              ))}
            </div>

            {/* Quick Info */}
            <div className="mt-6 p-3 rounded-xl bg-dark-900/50 border border-dark-700">
              <h4 className="text-xs font-semibold text-dark-400 mb-2">Selected Agent</h4>
              <div className="flex items-center gap-2 mb-1">
                <span>{currentAgentInfo.icon}</span>
                <span className={`text-sm font-medium ${currentAgentInfo.color}`}>{currentAgentInfo.name}</span>
              </div>
              <p className="text-xs text-dark-400 leading-relaxed">{currentAgentInfo.desc}</p>
            </div>

            {/* Suggested Prompts */}
            <div className="mt-4">
              <h4 className="text-xs font-semibold text-dark-400 mb-2">Try Asking...</h4>
              <div className="space-y-1.5">
                {getSuggestedPrompts(selectedAgent).map((prompt, i) => (
                  <button
                    key={i}
                    onClick={() => setInput(prompt)}
                    className="w-full text-left text-xs p-2 rounded-lg bg-dark-900/30 hover:bg-dark-700/50 text-dark-300 transition-colors line-clamp-2"
                  >
                    {prompt}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </aside>

        {/* Main Chat Area */}
        <main className="flex-1 flex flex-col min-w-0">
          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 md:p-6">
            {messages.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center text-center px-4">
                <div className="text-5xl mb-4">{currentAgentInfo.icon}</div>
                <h2 className="text-2xl font-bold mb-2">{currentAgentInfo.name}</h2>
                <p className="text-dark-400 mb-8 max-w-md">{currentAgentInfo.desc}</p>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-w-lg w-full">
                  {getSuggestedPrompts(selectedAgent).map((prompt, i) => (
                    <button
                      key={i}
                      onClick={() => setInput(prompt)}
                      className="text-left p-3 rounded-xl bg-dark-800 border border-dark-700 hover:border-dark-500 text-sm text-dark-300 transition-colors"
                    >
                      {prompt}
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              <div className="max-w-3xl mx-auto space-y-6">
                {messages.map((msg, idx) => (
                  <div key={idx} className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : ''}`}>
                    {msg.role === 'assistant' && (
                      <div className="w-8 h-8 rounded-lg bg-dark-800 border border-dark-700 flex items-center justify-center text-sm shrink-0">
                        {AGENTS.find(a => a.id === msg.agent)?.icon || '🤖'}
                      </div>
                    )}
                    <div
                      className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                        msg.role === 'user'
                          ? 'bg-accent text-white rounded-br-md'
                          : 'bg-dark-800 border border-dark-700 rounded-bl-md'
                      }`}
                    >
                      {msg.role === 'assistant' && msg.agentName && (
                        <div className={`text-xs font-medium mb-1 ${AGENTS.find(a => a.id === msg.agent)?.color || 'text-dark-400'}`}>
                          {msg.agentName}
                        </div>
                      )}
                      {msg.role === 'user' ? (
                        <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                      ) : (
                        <div className={`markdown-content text-sm ${msg.isStreaming ? 'cursor-blink' : ''}`}>
                          <ReactMarkdown>{msg.content || '...'}</ReactMarkdown>
                        </div>
                      )}
                    </div>
                    {msg.role === 'user' && (
                      <div className="w-8 h-8 rounded-lg bg-accent/20 border border-accent/30 flex items-center justify-center text-sm shrink-0">
                        👤
                      </div>
                    )}
                  </div>
                ))}
                <div ref={messagesEndRef} />
              </div>
            )}
          </div>

          {/* Input Area */}
          <div className="border-t border-dark-700 bg-dark-900/95 backdrop-blur-sm p-4">
            <div className="max-w-3xl mx-auto">
              <div className="flex gap-2 items-end">
                <div className="flex-1 relative">
                  <textarea
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder={`Ask the ${currentAgentInfo.name}...`}
                    rows={1}
                    className="w-full bg-dark-800 border border-dark-700 rounded-xl px-4 py-3 pr-12 text-sm text-dark-100 placeholder:text-dark-500 focus:outline-none focus:border-accent/50 resize-none max-h-32 overflow-y-auto"
                    style={{ minHeight: '48px' }}
                  />
                </div>
                <button
                  onClick={sendMessage}
                  disabled={!input.trim() || isStreaming}
                  className="p-3 bg-accent hover:bg-accent-hover disabled:bg-dark-700 disabled:text-dark-500 rounded-xl transition-colors shrink-0"
                >
                  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                  </svg>
                </button>
              </div>
              <div className="flex items-center justify-between mt-2 text-xs text-dark-500">
                <span>Model: {getModelName(selectedAgent)}</span>
                <span>Press Enter to send, Shift+Enter for new line</span>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}

function getSuggestedPrompts(agentId: string): string[] {
  const prompts: Record<string, string[]> = {
    strategist: [
      'Help me validate my startup idea',
      'Analyze my competitive landscape',
      'What metrics should I track at pre-seed?',
    ],
    researcher: [
      'Research the AI agent market',
      'Find data on SaaS growth trends',
      'Analyze competitors in my space',
    ],
    writer: [
      'Write a cold email to a VC',
      'Create a landing page hero section',
      'Draft a product launch tweet thread',
    ],
    analyst: [
      'Calculate unit economics for my SaaS',
      'Build a 12-month revenue projection',
      'How much runway do I have?',
    ],
    coder: [
      'Design architecture for my MVP',
      'Write a FastAPI auth endpoint',
      'Recommend a tech stack for AI app',
    ],
    coach: [
      'I feel overwhelmed, help me prioritize',
      'Should I pivot or persevere?',
      'Help me prepare for investor meeting',
    ],
  }
  return prompts[agentId] || prompts.strategist
}

function getModelName(agentId: string): string {
  const models: Record<string, string> = {
    strategist: 'GLM 5.2 (Fireworks/AMD)',
    researcher: 'Llama 3.1 70B (Fireworks/AMD)',
    writer: 'Mistral Large (Fireworks/AMD)',
    analyst: 'Qwen 2.5 72B (Fireworks/AMD)',
    coder: 'DeepSeek V4 Pro (Fireworks/AMD)',
    coach: 'Gemma 4 26B (Fireworks/AMD) ★',
  }
  return models[agentId] || 'GLM 5.2'
}