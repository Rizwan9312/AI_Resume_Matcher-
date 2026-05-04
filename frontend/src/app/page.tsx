"use client";

import Link from "next/link";

export default function HomePage() {
  return (
    <div className="min-h-screen flex flex-col">
      {/* Nav */}
      <nav className="flex items-center justify-between px-8 py-5 border-b border-border/50">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-cyan-400 flex items-center justify-center text-white font-bold text-sm">R</div>
          <span className="font-semibold text-lg tracking-tight">ResumeIQ</span>
        </div>
        <div className="flex items-center gap-4">
          <Link href="/login" className="text-sm text-muted-foreground hover:text-foreground transition">Sign In</Link>
          <Link href="/register" className="text-sm bg-primary text-primary-foreground px-4 py-2 rounded-lg hover:opacity-90 transition font-medium">Get Started</Link>
        </div>
      </nav>

      {/* Hero */}
      <main className="flex-1 flex flex-col items-center justify-center px-4 text-center">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-secondary border border-border text-xs text-muted-foreground mb-8">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          AI-Powered Resume Intelligence
        </div>

        <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight leading-[1.1] max-w-4xl gradient-text mb-6">
          Score. Rewrite. Land the Job.
        </h1>

        <p className="text-lg text-muted-foreground max-w-2xl mb-10 leading-relaxed">
          Combine BERT semantic analysis, TF-IDF matching, and AI-powered scoring to get the most
          accurate, actionable resume feedback available. Built for job seekers and recruiters.
        </p>

        <div className="flex flex-col sm:flex-row gap-4">
          <Link href="/register" className="bg-primary text-primary-foreground px-8 py-3.5 rounded-xl font-semibold text-base hover:opacity-90 transition shadow-lg shadow-primary/20">
            Analyze Your Resume →
          </Link>
          <Link href="/login" className="border border-border text-foreground px-8 py-3.5 rounded-xl font-medium text-base hover:bg-secondary transition">
            Sign In
          </Link>
        </div>

        {/* Feature cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-20 max-w-4xl w-full">
          {[
            { icon: "🧠", title: "BERT Semantic Match", desc: "Deep contextual understanding beyond keyword matching" },
            { icon: "📊", title: "Multi-Score Analysis", desc: "TF-IDF, keyword overlap, and LLM-as-judge scoring" },
            { icon: "✨", title: "AI Bullet Rewriter", desc: "Transform weak bullets into quantified, ATS-optimized statements" },
          ].map((f) => (
            <div key={f.title} className="glass-card rounded-2xl p-6 text-left hover:border-primary/20 transition">
              <div className="text-3xl mb-4">{f.icon}</div>
              <h3 className="font-semibold text-base mb-2">{f.title}</h3>
              <p className="text-sm text-muted-foreground leading-relaxed">{f.desc}</p>
            </div>
          ))}
        </div>
      </main>

      {/* Footer */}
      <footer className="text-center py-8 text-xs text-muted-foreground border-t border-border/30">
        <p>© 2026 ResumeIQ · AI Resume Matcher Enterprise Edition</p>
      </footer>
    </div>
  );
}
