/**
 * FounderOS API client.
 * In production, API is at same origin.
 * In development, Next.js rewrites proxy to localhost:8000.
 */

// Static exports cannot use Next.js rewrites. Development calls FastAPI directly;
// production stays same-origin when FastAPI serves the exported frontend.
export const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ??
  (process.env.NODE_ENV === 'development' ? 'http://localhost:8000' : '')

export interface AgentInfo {
  id: string
  name: string
  role: string
  description: string
  model: string
  icon: string
  color: string
  example_prompts: string[]
}

export interface ChatRequest {
  message: string
  agent: string
  conversation_history?: Array<{ role: string; content: string }>
  stream?: boolean
}

export async function fetchAgents(): Promise<AgentInfo[]> {
  const res = await fetch(`${API_BASE}/api/agents`)
  if (!res.ok) throw new Error('Failed to fetch agents')
  const data = await res.json()
  return data.agents
}

export async function* streamChat(request: ChatRequest): AsyncGenerator<string> {
  const res = await fetch(`${API_BASE}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  })

  if (!res.ok) throw new Error(`Chat API error: ${res.status}`)

  const reader = res.body?.getReader()
  if (!reader) throw new Error('No response body')

  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    buffer += decoder.decode(value, { stream: true })
    const lines = buffer.split('\n')
    buffer = lines.pop() || ''

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const data = line.slice(6).trim()
        if (data === '[DONE]') return
        try {
          const parsed = JSON.parse(data)
          if (parsed.type === 'token' && parsed.content) {
            yield parsed.content
          }
        } catch {
          // Ignore parse errors
        }
      }
    }
  }
}
