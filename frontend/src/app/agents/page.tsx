import Link from 'next/link'

const AGENTS = [
  { id: 'strategist', name: 'Strategist', icon: '🎯', color: 'from-blue-500/20 to-blue-900/20', border: 'border-blue-500/30', text: 'text-blue-400', role: 'Senior Startup Strategist', desc: 'Analyzes challenges from a strategic perspective — market sizing, competitive landscape, risk assessment, and prioritized action plans.', model: 'GLM 5.2', prompts: ['Validate my business idea', 'Analyze competitive landscape', 'Strategic framework for growth'] },
  { id: 'researcher', name: 'Researcher', icon: '🔍', color: 'from-green-500/20 to-green-900/20', border: 'border-green-500/30', text: 'text-green-400', role: 'Market Research Specialist', desc: 'Conducts deep market research — finds data, analyzes trends, maps competitors, and identifies opportunities using the knowledge base.', model: 'Llama 3.1 70B', prompts: ['Research AI agent frameworks', 'Find market size data', 'Competitor analysis'] },
  { id: 'writer', name: 'Writer', icon: '✍️', color: 'from-purple-500/20 to-purple-900/20', border: 'border-purple-500/30', text: 'text-purple-400', role: 'Content Creator', desc: 'Crafts polished content — pitch narratives, investor emails, landing page copy, blog posts, and social media content.', model: 'Mistral Large', prompts: ['Cold email to a VC', 'Landing page copy', 'Product launch thread'] },
  { id: 'analyst', name: 'Analyst', icon: '📊', color: 'from-orange-500/20 to-orange-900/20', border: 'border-orange-500/30', text: 'text-orange-400', role: 'Financial Analyst', desc: 'Provides financial analysis — unit economics, revenue projections, burn rate, runway calculations, and fundraising strategy.', model: 'Qwen 2.5 72B', prompts: ['Calculate unit economics', 'Revenue projection', 'Runway analysis'] },
  { id: 'coder', name: 'Coder', icon: '💻', color: 'from-cyan-500/20 to-cyan-900/20', border: 'border-cyan-500/30', text: 'text-cyan-400', role: 'Technical Architect', desc: 'Designs technical architecture and writes code — MVP planning, tech stack recommendations, API design, and deployment guidance.', model: 'DeepSeek V4 Pro', prompts: ['Design MVP architecture', 'Write API endpoint', 'Tech stack recommendation'] },
  { id: 'coach', name: 'Coach', icon: '🧠', color: 'from-pink-500/20 to-pink-900/20', border: 'border-pink-500/30', text: 'text-pink-400', role: 'Startup Coach & Mentor', desc: 'Provides personalized coaching — decision frameworks, accountability, founder well-being, and mentorship. Powered by Gemma 4 (Bonus Challenge).', model: 'Gemma 4 26B ★', prompts: ['Help me prioritize tasks', 'Should I pivot?', 'Investor pitch prep'] },
]

export default function AgentsPage() {
  return (
    <main className="min-h-screen bg-dark-900 text-white">
      <nav className="border-b border-dark-700 bg-dark-900/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
          <Link href="/dashboard" className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-accent flex items-center justify-center font-bold text-sm">F</div>
            <span className="text-lg font-semibold">FounderOS</span>
          </Link>
          <Link href="/dashboard" className="px-4 py-2 bg-accent hover:bg-accent-hover rounded-lg text-sm font-medium transition-colors">
            ← Back to Dashboard
          </Link>
        </div>
      </nav>

      <div className="max-w-6xl mx-auto px-6 py-12">
        <h1 className="text-3xl font-bold mb-2">Agent Gallery</h1>
        <p className="text-dark-400 mb-8">Each agent is powered by a different AI model optimized for its specific task.</p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {AGENTS.map((agent) => (
            <Link
              key={agent.id}
              href={`/dashboard?agent=${agent.id}`}
              className={`block p-6 rounded-2xl bg-gradient-to-br ${agent.color} border ${agent.border} hover:scale-[1.02] transition-transform`}
            >
              <div className="flex items-center gap-3 mb-3">
                <span className="text-3xl">{agent.icon}</span>
                <div>
                  <h2 className={`text-xl font-bold ${agent.text}`}>{agent.name}</h2>
                  <p className="text-xs text-dark-400">{agent.model}</p>
                </div>
              </div>
              <p className="text-sm text-dark-300 mb-1">{agent.role}</p>
              <p className="text-sm text-dark-400 leading-relaxed mb-4">{agent.desc}</p>
              <div className="flex flex-wrap gap-2">
                {agent.prompts.map((prompt, i) => (
                  <span key={i} className="text-xs px-2 py-1 rounded-md bg-dark-900/50 text-dark-400">
                    {prompt}
                  </span>
                ))}
              </div>
            </Link>
          ))}
        </div>
      </div>
    </main>
  )
}