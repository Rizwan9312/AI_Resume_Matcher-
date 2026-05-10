"use client";

import Link from "next/link";
import { useEffect, useState, useRef } from "react";
import FloatingOrbs from "@/components/FloatingOrbs";
import GlassCard from "@/components/GlassCard";
import ScoreRing from "@/components/ScoreRing";
import Button from "@/components/Button";

/* ── Navbar ─────────────────────────────────────────────── */
function LandingNav() {
  const [scrolled, setScrolled] = useState(false);
  useEffect(() => {
    const handler = () => setScrolled(window.scrollY > 80);
    window.addEventListener("scroll", handler, { passive: true });
    return () => window.removeEventListener("scroll", handler);
  }, []);

  return (
    <nav
      className={`fixed top-0 inset-x-0 z-50 transition-all duration-500 ${
        scrolled
          ? "border-b border-white/[0.06] bg-[#050508]/80 backdrop-blur-2xl"
          : "bg-transparent"
      }`}
    >
      <div className="max-w-6xl mx-auto flex items-center justify-between px-6 h-16">
        <Link href="/" className="flex items-center gap-2 group" aria-label="ResumeIQ Home">
          <span className="font-syne font-bold text-xl text-ag-text tracking-tight">
            ResumeIQ
          </span>
          <span className="w-1.5 h-1.5 rounded-full bg-ag-accent animate-pulse-glow" />
        </Link>
        <div className="flex items-center gap-3">
          <Link href="/login">
            <Button variant="ghost" size="sm">Sign In</Button>
          </Link>
          <Link href="/register">
            <Button variant="primary" size="sm">Get Started</Button>
          </Link>
        </div>
      </div>
    </nav>
  );
}

/* ── Hero ───────────────────────────────────────────────── */
function HeroSection() {
  return (
    <section className="relative min-h-screen flex flex-col items-center justify-center px-6 text-center pt-16">
      <FloatingOrbs />

      {/* Badge */}
      <div className="relative z-10 inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-white/[0.08] bg-surface/60 backdrop-blur-md mb-8 animate-fade-in-up">
        <span className="text-ag-accent text-xs">✦</span>
        <span className="text-xs font-medium text-ag-text-secondary tracking-wider uppercase">
          AI-Powered Resume Intelligence
        </span>
      </div>

      {/* Headline */}
      <h1 className="relative z-10 font-syne font-extrabold text-5xl md:text-7xl tracking-tight leading-[1.1] max-w-4xl mb-6 animate-fade-in-up"
          style={{ animationDelay: "0.1s" }}>
        Match Smarter.{" "}
        <br className="hidden md:block" />
        <span className="text-ag-accent">Land Faster.</span>
      </h1>

      {/* Sub-headline */}
      <p className="relative z-10 text-lg md:text-xl text-ag-text-secondary max-w-2xl mb-10 leading-relaxed animate-fade-in-up"
         style={{ animationDelay: "0.2s" }}>
        ResumeIQ analyzes your resume against any job description using BERT, TF-IDF,
        and LLM scoring — then rewrites it to get you hired.
      </p>

      {/* CTAs */}
      <div className="relative z-10 flex flex-col sm:flex-row gap-4 mb-12 animate-fade-in-up"
           style={{ animationDelay: "0.3s" }}>
        <Link href="/register">
          <Button variant="primary" size="lg">Analyze My Resume →</Button>
        </Link>
        <a href="#how-it-works">
          <Button variant="ghost" size="lg">See How It Works</Button>
        </a>
      </div>

      {/* Trust bar */}
      <div className="relative z-10 inline-flex items-center gap-0 rounded-full border border-white/[0.06] bg-surface/40 backdrop-blur-sm animate-fade-in-up"
           style={{ animationDelay: "0.4s" }}>
        {[
          "10,000+ Resumes Analyzed",
          "94% Match Accuracy",
          "Free to Start",
        ].map((stat, i) => (
          <div key={stat} className="flex items-center">
            {i > 0 && <div className="w-px h-4 bg-white/[0.08]" />}
            <span className="px-5 py-2.5 text-xs text-ag-text-secondary font-medium whitespace-nowrap">
              {stat}
            </span>
          </div>
        ))}
      </div>
    </section>
  );
}

/* ── How It Works ───────────────────────────────────────── */
function HowItWorks() {
  const steps = [
    { num: "01", title: "Upload Resume", desc: "Upload your PDF or DOCX resume" },
    { num: "02", title: "AI Scoring", desc: "BERT + TF-IDF + Keyword + LLM analysis" },
    { num: "03", title: "Auto-Rewrite", desc: "AI rewrites your resume to match the job" },
  ];

  return (
    <section id="how-it-works" className="max-w-6xl mx-auto px-6 py-24">
      <p className="section-label mb-4">01 / HOW IT WORKS</p>
      <h2 className="font-syne font-bold text-3xl md:text-4xl mb-12 text-ag-text">
        Three Steps to Your Next Job
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {steps.map((step) => (
          <GlassCard key={step.num} className="p-8 relative overflow-hidden">
            {/* Glowing top border */}
            <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-ag-accent/60 via-ag-cyan/30 to-transparent" />
            {/* Decorative watermark number */}
            <span className="absolute top-4 right-4 font-syne text-[80px] font-extrabold leading-none text-white/[0.04] pointer-events-none select-none">
              {step.num}
            </span>
            <span className="section-label text-ag-accent">{step.num}</span>
            <h3 className="font-syne font-bold text-lg mt-3 mb-2 text-ag-text">
              {step.title}
            </h3>
            <p className="text-sm text-ag-text-secondary leading-relaxed">
              {step.desc}
            </p>
          </GlassCard>
        ))}
      </div>
    </section>
  );
}

/* ── Features ───────────────────────────────────────────── */
function FeaturesSection() {
  return (
    <section className="max-w-6xl mx-auto px-6 py-24">
      <p className="section-label mb-4">02 / FEATURES</p>
      <h2 className="font-syne font-bold text-3xl md:text-4xl mb-12 text-ag-text">
        Enterprise-Grade Analysis
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Large card — spans 2 cols */}
        <GlassCard className="md:col-span-2 p-8">
          <h3 className="font-syne font-bold text-lg mb-6 text-ag-text">
            Multi-Dimensional Scoring
          </h3>
          <div className="space-y-4">
            {[
              { label: "BERT Semantic", value: 82, color: "#6C63FF" },
              { label: "TF-IDF Cosine", value: 71, color: "#00D4FF" },
              { label: "Keyword Match", value: 65, color: "#00FF88" },
              { label: "LLM Judge", value: 78, color: "#FFB800" },
            ].map((bar) => (
              <div key={bar.label} className="flex items-center gap-4">
                <span className="text-xs text-ag-text-secondary w-28 font-mono">{bar.label}</span>
                <div className="flex-1 h-2 bg-white/[0.04] rounded-full overflow-hidden">
                  <div
                    className="h-full rounded-full transition-all duration-1000"
                    style={{ width: `${bar.value}%`, background: bar.color }}
                  />
                </div>
                <span className="text-xs font-mono w-8 text-right" style={{ color: bar.color }}>
                  {bar.value}
                </span>
              </div>
            ))}
          </div>
        </GlassCard>

        {/* Small cards */}
        {[
          { icon: "🎯", title: "Role-Aware Weighting", desc: "Auto-detects job category and optimizes score weights" },
          { icon: "🔍", title: "Keyword Gap Analysis", desc: "Identifies matched and missing skills at a glance" },
          { icon: "✨", title: "One-Click Rewrite", desc: "AI rewrites your entire resume in seconds" },
        ].map((f) => (
          <GlassCard key={f.title} className="p-6">
            <div className="text-2xl mb-3">{f.icon}</div>
            <h3 className="font-syne font-bold text-sm mb-2 text-ag-text">{f.title}</h3>
            <p className="text-xs text-ag-text-secondary leading-relaxed">{f.desc}</p>
          </GlassCard>
        ))}
      </div>
    </section>
  );
}

/* ── Score Preview ──────────────────────────────────────── */
function ScorePreview() {
  return (
    <section className="max-w-6xl mx-auto px-6 py-24">
      <p className="section-label mb-4">03 / RESULTS</p>
      <h2 className="font-syne font-bold text-3xl md:text-4xl mb-12 text-ag-text">
        See What Your Score Looks Like
      </h2>

      <div className="flex justify-center mb-12">
        <GlassCard className="p-10 max-w-lg w-full text-center">
          <ScoreRing score={82} size={180} strokeWidth={12} className="mx-auto mb-6" />
          <div className="grid grid-cols-2 gap-3 mb-6">
            {[
              { label: "BERT", val: 85, color: "#6C63FF" },
              { label: "TF-IDF", val: 74, color: "#00D4FF" },
              { label: "Keyword", val: 68, color: "#00FF88" },
              { label: "LLM", val: 80, color: "#FFB800" },
            ].map((m) => (
              <div key={m.label} className="flex items-center gap-2">
                <div className="flex-1 h-1.5 bg-white/[0.04] rounded-full overflow-hidden">
                  <div className="h-full rounded-full" style={{ width: `${m.val}%`, background: m.color }} />
                </div>
                <span className="text-[10px] font-mono" style={{ color: m.color }}>{m.val}</span>
              </div>
            ))}
          </div>
          <div className="flex flex-wrap justify-center gap-2 mb-4">
            {["React", "TypeScript", "Node.js"].map((kw) => (
              <span key={kw} className="px-2.5 py-1 rounded-md text-xs bg-ag-success/10 text-ag-success border border-ag-success/20">✓ {kw}</span>
            ))}
            {["GraphQL", "Docker"].map((kw) => (
              <span key={kw} className="px-2.5 py-1 rounded-md text-xs bg-ag-danger/10 text-ag-danger border border-ag-danger/20">✗ {kw}</span>
            ))}
          </div>
        </GlassCard>
      </div>

      {/* Testimonials */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {[
          { quote: "Went from 45 to 89 after one rewrite. Got the interview the same week.", role: "Software Engineer" },
          { quote: "The keyword gap analysis alone is worth it — found 8 missing skills.", role: "Marketing Manager" },
          { quote: "Best resume tool I've used. The BERT scoring is scarily accurate.", role: "Data Scientist" },
        ].map((t) => (
          <GlassCard key={t.role} className="p-6">
            <p className="text-sm text-ag-text-secondary leading-relaxed italic mb-4">"{t.quote}"</p>
            <p className="text-xs text-ag-text-muted">— {t.role}</p>
          </GlassCard>
        ))}
      </div>
    </section>
  );
}

/* ── CTA Banner ─────────────────────────────────────────── */
function CtaBanner() {
  return (
    <section className="relative py-24 overflow-hidden">
      {/* Radial glow */}
      <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
        <div className="w-[600px] h-[300px] bg-ag-accent/10 rounded-full blur-[120px]" />
      </div>
      <div className="relative z-10 text-center max-w-2xl mx-auto px-6">
        <h2 className="font-syne font-bold text-3xl md:text-4xl mb-6 text-ag-text">
          Ready to Outmatch the Competition?
        </h2>
        <Link href="/register">
          <Button variant="primary" size="lg">
            Start for Free — No Credit Card
          </Button>
        </Link>
      </div>
    </section>
  );
}

/* ── Footer ─────────────────────────────────────────────── */
function Footer() {
  return (
    <footer className="border-t border-white/[0.06] py-8">
      <div className="max-w-6xl mx-auto px-6 flex flex-col md:flex-row items-center justify-between gap-4">
        <span className="font-syne font-bold text-sm text-ag-text-secondary">ResumeIQ</span>
        <div className="flex items-center gap-6 text-xs text-ag-text-muted">
          <a href="#features" className="hover:text-ag-text transition">Features</a>
          <Link href="/login" className="hover:text-ag-text transition">Sign In</Link>
          <Link href="/register" className="hover:text-ag-text transition">Register</Link>
        </div>
        <span className="text-xs text-ag-text-muted">© 2026 ResumeIQ</span>
      </div>
    </footer>
  );
}

/* ── Page ────────────────────────────────────────────────── */
export default function HomePage() {
  return (
    <div className="min-h-screen">
      <LandingNav />
      <HeroSection />
      <HowItWorks />
      <FeaturesSection />
      <ScorePreview />
      <CtaBanner />
      <Footer />
    </div>
  );
}
