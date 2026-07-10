import Link from 'next/link'

export default function Home() {
  return (
    <main className="min-h-screen bg-dark-900 text-white">
      {/* Navigation */}
      <nav className="border-b border-dark-700 bg-dark-900/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-accent flex items-center justify-center font-bold text-sm">
              F
            </div>
            <span className="text-lg font-semibold">FounderOS</span>
          </div>
          <Link
            href="/dashboard"
            className="px-4 py-2 bg-accent hover:bg-accent-hover rounded-lg text-sm font-medium transition-colors"
          >
            Launch App
          </Link>
        </div>
      </nav>

      {/* Hero */}
      <section className="max-w-6xl mx-auto px-6 pt-24 pb-20">
        <div className="max-w-3xl">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-dark-800 border border-dark-600 text-sm text-dark-300 mb-6">
            <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
            AMD AI Developer Hackathon — Track 3
          </div>
          <h1 className="text-5xl md:text-6xl font-bold leading-tight mb-6">
            Your AI-Powered{' '}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-accent to-purple-400">
              Operating System
            </span>
            <br />
            for Building Startups
          </h1>
          <p className="text-xl text-dark-300 mb-8 leading-relaxed">
            6 specialized AI agents working together to help you strategize, research, write, analyze, code, and coach your startup to success.
          </p>
          <div className="flex gap-4">
            <Link
              href="/dashboard"
              className="px-6 py-3 bg-accent hover:bg-accent-hover rounded-lg font-medium transition-colors"
            >
              Start Building →
            </Link>
            <a
              href="https://github.com/b3panda3/founderos-hackathon"
              target="_blank"
              rel="noopener noreferrer"
              className="px-6 py-3 border border-dark-600 hover:border-dark-400 rounded-lg font-medium transition-colors text-dark-200"
            >
              View on GitHub
            </a>
          </div>
        </div>
      </section>

      {/* Agents Preview */}
      <section className="border-t border-dark-700 bg-dark-800/50">
        <div className="max-w-6xl mx-auto px-6 py-20">
          <h2 className="text-2xl font-bold mb-8 text-center">6 Specialized Agents</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {[
              { icon: '🎯', name: 'Strategist', desc: 'Business strategy & market analysis', color: 'blue' },
              { icon: '🔍', name: 'Researcher', desc: 'Deep market research & data', color: 'green' },
              { icon: '✍️', name: 'Writer', desc: 'Pitch decks, emails & content', color: 'purple' },
              { icon: '📊', name: 'Analyst', desc: 'Financials & unit economics', color: 'orange' },
              { icon: '💻', name: 'Coder', desc: 'Technical architecture & code', color: 'cyan' },
              { icon: '🧠', name: 'Coach', desc: 'Mentorship & accountability', color: 'pink' },
            ].map((agent) => (
              <div
                key={agent.name}
                className="p-5 rounded-xl bg-dark-900 border border-dark-700 hover:border-dark-500 transition-colors"
              >
                <div className="text-2xl mb-2">{agent.icon}</div>
                <h3 className="font-semibold mb-1">{agent.name}</h3>
                <p className="text-sm text-dark-400">{agent.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Tech Stack */}
      <section className="max-w-6xl mx-auto px-6 py-20">
        <h2 className="text-2xl font-bold mb-8 text-center">Built With</h2>
        <div className="flex flex-wrap justify-center gap-3">
          {['Next.js', 'FastAPI', 'LangGraph', 'ChromaDB', 'Fireworks AI', 'Gemma 4', 'Docker'].map((tech) => (
            <span
              key={tech}
              className="px-4 py-2 rounded-lg bg-dark-800 border border-dark-700 text-sm text-dark-300"
            >
              {tech}
            </span>
          ))}
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-dark-700 py-8">
        <div className="max-w-6xl mx-auto px-6 text-center text-dark-500 text-sm">
          FounderOS — AMD AI Developer Hackathon Track 3 Submission
        </div>
      </footer>
    </main>
  )
}