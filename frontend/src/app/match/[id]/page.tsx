"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import api from "@/lib/api";
import { MatchResult } from "@/types";
import GlassCard from "@/components/GlassCard";
import ScoreRing from "@/components/ScoreRing";
import Button from "@/components/Button";
import JobRecommendations from "@/components/JobRecommendations";

const STEPS = [
  { label: "Parsing resume", pct: 20 },
  { label: "Extracting keywords", pct: 42 },
  { label: "BERT + TF-IDF scoring", pct: 68 },
  { label: "AI analysis", pct: 88 },
];

function ProcessingScreen() {
  const [activeStep, setActiveStep] = useState(0);
  const [displayPct, setDisplayPct] = useState(0);

  useEffect(() => {
    const delays = [800, 2400, 5000, 9000];
    const timers = delays.map((d, i) =>
      setTimeout(() => setActiveStep(i + 1), d)
    );
    return () => timers.forEach(clearTimeout);
  }, []);

  useEffect(() => {
    const target = activeStep < STEPS.length ? STEPS[activeStep]?.pct ?? 0 : 88;
    const current = activeStep === 0 ? 0 : STEPS[activeStep - 1]?.pct ?? 0;
    const diff = target - current;
    let frame = 0;
    const total = 30;
    const timer = setInterval(() => {
      frame++;
      setDisplayPct(Math.round(current + (diff * frame) / total));
      if (frame >= total) clearInterval(timer);
    }, 16);
    return () => clearInterval(timer);
  }, [activeStep]);

  return (
    <div className="flex flex-col items-center justify-center min-h-screen px-6">
      <div className="w-full max-w-md">
        {/* Pulsing orb */}
        <div className="w-20 h-20 rounded-full bg-ag-accent/10 border border-ag-accent/20 flex items-center justify-center mx-auto mb-8 animate-pulse-glow">
          <span className="text-3xl">🧠</span>
        </div>

        <h2 className="font-syne font-bold text-xl text-center text-ag-text mb-1">
          Analyzing your resume
        </h2>
        <p className="text-sm text-ag-text-secondary text-center mb-8">
          Running AI scoring pipeline — this takes about 60–90 seconds
        </p>

        {/* Progress bar */}
        <div className="w-full bg-white/[0.04] rounded-full h-2 mb-2 overflow-hidden">
          <div
            className="h-full rounded-full progress-fill"
            style={{ width: `${displayPct}%` }}
          />
        </div>
        <p className="text-xs text-ag-text-muted text-right mb-8 font-mono">{displayPct}%</p>

        {/* Steps */}
        <div className="grid grid-cols-1 gap-3">
          {STEPS.map((step, i) => {
            const done = activeStep > i + 1;
            const active = activeStep === i + 1;
            return (
              <GlassCard
                key={step.label}
                hover={false}
                className={`rounded-xl px-4 py-3 flex items-center gap-3 ${
                  active ? "border-ag-accent/40" : done ? "border-ag-success/30" : ""
                }`}
              >
                <div
                  className={`w-2.5 h-2.5 rounded-full flex-shrink-0 transition-all duration-300 ${
                    done
                      ? "bg-ag-success"
                      : active
                      ? "bg-ag-accent animate-pulse"
                      : "bg-white/[0.1]"
                  }`}
                />
                <span
                  className={`text-sm transition-colors duration-300 ${
                    active || done ? "text-ag-text" : "text-ag-text-muted"
                  }`}
                >
                  {step.label}
                </span>
                {done && <span className="ml-auto text-ag-success text-sm">✓</span>}
              </GlassCard>
            );
          })}
        </div>
      </div>
    </div>
  );
}

export default function MatchResultPage() {
  const params = useParams();
  const [match, setMatch] = useState<MatchResult | null>(null);
  const [polling, setPolling] = useState(true);
  const [showVerdict, setShowVerdict] = useState(false);

  useEffect(() => {
    if (!params.id) return;
    const poll = async () => {
      try {
        const res = await api.get(`/matches/${params.id}`);
        setMatch(res.data);
        if (res.data.status === "complete" || res.data.status === "failed") {
          setPolling(false);
        }
      } catch (_err) { setPolling(false); }
    };
    poll();
    if (polling) {
      const interval = setInterval(poll, 2000);
      return () => clearInterval(interval);
    }
  }, [params.id, polling]);

  if (!match) return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="text-ag-text-muted text-sm">Loading…</div>
    </div>
  );

  if (match.status === "pending" || match.status === "processing") {
    return <ProcessingScreen />;
  }

  if (match.status === "failed") {
    return (
      <div className="max-w-2xl mx-auto px-6 py-20 text-center">
        <GlassCard className="p-10" hover={false}>
          <div className="text-5xl mb-6">❌</div>
          <h2 className="font-syne font-bold text-2xl text-ag-danger mb-4">Analysis Failed</h2>
          <p className="text-ag-text-secondary mb-6">{match.feedback_text || "An error occurred"}</p>
          <Link href="/match/new">
            <Button variant="ghost">Try Again</Button>
          </Link>
        </GlassCard>
      </div>
    );
  }

  const score = match.final_score || 0;

  const getScoreColor = (s: number) => {
    if (s >= 80) return "text-ag-success";
    if (s >= 60) return "text-ag-warning";
    return "text-ag-danger";
  };

  return (
    <div className="max-w-4xl mx-auto px-6 py-10">
      {/* Header */}
      <Link href="/dashboard" className="inline-flex items-center gap-2 text-sm text-ag-text-secondary hover:text-ag-text transition mb-6">
        ← Back
      </Link>
      <h1 className="font-syne font-bold text-3xl text-ag-text mb-8">
        Match Analysis Results
      </h1>

      {/* Hero Score Card */}
      <GlassCard className="p-10 mb-8 text-center" hover={false}>
        <ScoreRing score={score} size={200} strokeWidth={14} className="mx-auto mb-4" />
        <p className="text-xs uppercase tracking-widest text-ag-text-muted mt-2">Overall Match Score</p>

        {/* Role badge */}
        {match.role_detected && (
          <div className="mt-4 inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-ag-accent/10 border border-ag-accent/20 text-sm text-ag-accent">
            🎯 Detected Role: {match.role_detected}
          </div>
        )}

        {/* Rewrite CTA */}
        {score < 80 && (
          <div className="mt-8 p-4 rounded-xl bg-ag-warning/5 border border-ag-warning/20">
            <p className="text-sm text-ag-warning mb-3">
              Your score is below 80. Let AI rewrite your resume.
            </p>
            <Link href={`/rewrite/${match.id}`}>
              <Button variant="primary" size="md">Rewrite My Resume →</Button>
            </Link>
          </div>
        )}
        {score >= 80 && (
          <div className="mt-6">
            <Link href={`/rewrite/${match.id}`}>
              <Button variant="ghost" size="md">✨ Auto-Rewrite Resume</Button>
            </Link>
          </div>
        )}
      </GlassCard>

      {/* 4 Metric Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        {[
          { label: "BERT Semantic", value: match.bert_score, color: "#6C63FF" },
          { label: "TF-IDF Cosine", value: match.tfidf_score, color: "#00D4FF" },
          { label: "Keyword Match", value: match.keyword_score, color: "#00FF88" },
          { label: "LLM Score", value: match.llm_score, color: "#FFB800" },
        ].map((s) => (
          <GlassCard key={s.label} className="p-4" hover={false}>
            <div className="text-xs text-ag-text-muted mb-2 font-mono">{s.label}</div>
            <div className="text-2xl font-bold font-mono mb-2" style={{ color: s.color }}>
              {s.value != null ? Math.round(s.value) : "—"}
            </div>
            <div className="h-1.5 bg-white/[0.04] rounded-full overflow-hidden">
              <div
                className="h-full rounded-full transition-all duration-1000"
                style={{
                  width: `${s.value != null ? Math.min(s.value, 100) : 0}%`,
                  background: s.color,
                }}
              />
            </div>
          </GlassCard>
        ))}
      </div>

      {/* AI Feedback */}
      {match.feedback_text && (
        <GlassCard className="p-6 mb-8 border-l-4 border-ag-accent" hover={false}>
          <h3 className="text-xs uppercase tracking-widest text-ag-text-muted mb-3">AI Feedback</h3>
          <p className="text-sm leading-relaxed text-ag-text-secondary">{match.feedback_text}</p>
        </GlassCard>
      )}

      {/* Keywords */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        <GlassCard className="p-6" hover={false}>
          <h3 className="text-xs uppercase tracking-widest text-ag-text-muted mb-3">✅ Matched Keywords</h3>
          <div className="flex flex-wrap gap-2">
            {(match.matched_keywords || []).map((kw) => (
              <span key={kw} className="px-2.5 py-1 rounded-md text-xs bg-ag-success/10 text-ag-success border border-ag-success/20">
                ✓ {kw}
              </span>
            ))}
            {(!match.matched_keywords || match.matched_keywords.length === 0) && (
              <span className="text-sm text-ag-text-muted">None</span>
            )}
          </div>
        </GlassCard>
        <GlassCard className="p-6" hover={false}>
          <h3 className="text-xs uppercase tracking-widest text-ag-text-muted mb-3">❌ Missing Keywords</h3>
          <div className="flex flex-wrap gap-2">
            {(match.missing_keywords || []).map((kw) => (
              <span key={kw} className="px-2.5 py-1 rounded-md text-xs bg-ag-danger/10 text-ag-danger border border-ag-danger/20">
                ✗ {kw}
              </span>
            ))}
            {(!match.missing_keywords || match.missing_keywords.length === 0) && (
              <span className="text-sm text-ag-text-muted">None</span>
            )}
          </div>
        </GlassCard>
      </div>

      {/* LLM Verdict */}
      {match.llm_verdict && (
        <GlassCard className="p-6" hover={false}>
          <button
            onClick={() => setShowVerdict(!showVerdict)}
            className="w-full flex items-center justify-between text-left"
            aria-label="Toggle LLM verdict details"
          >
            <h3 className="text-xs uppercase tracking-widest text-ag-text-muted">🤖 AI Verdict</h3>
            <span className="text-ag-text-muted text-xs">{showVerdict ? "▲ Collapse" : "▼ Expand"}</span>
          </button>

          <p className="text-sm mt-3 text-ag-text-secondary">{match.llm_verdict.one_line_summary}</p>

          {showVerdict && (
            <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className="text-xs text-ag-success font-medium mb-2">Strengths</h4>
                <ul className="space-y-1.5">
                  {(match.llm_verdict.strengths || []).map((s, i) => (
                    <li key={i} className="text-sm text-ag-text-secondary flex items-start gap-2">
                      <span className="text-ag-success mt-0.5">•</span>
                      {s}
                    </li>
                  ))}
                </ul>
              </div>
              <div>
                <h4 className="text-xs text-ag-danger font-medium mb-2">Gaps</h4>
                <ul className="space-y-1.5">
                  {(match.llm_verdict.gaps || []).map((g, i) => (
                    <li key={i} className="text-sm text-ag-text-secondary flex items-start gap-2">
                      <span className="text-ag-danger mt-0.5">•</span>
                      {g}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          )}
        </GlassCard>
      )}

      {/* Job Recommendations */}
      <JobRecommendations
        resumeId={match.resume_id}
        matchResultId={match.id}
        autoTrigger={false}
      />
    </div>
  );
}