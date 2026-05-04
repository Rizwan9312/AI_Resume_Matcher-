"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import api from "@/lib/api";
import { MatchResult } from "@/types";
import { getScoreColor } from "@/lib/utils";

const STEPS = [
  { label: "Parsing resume",       pct: 20 },
  { label: "Extracting keywords",  pct: 42 },
  { label: "BERT + TF-IDF scoring",pct: 68 },
  { label: "AI analysis",          pct: 88 },
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
        {/* Icon */}
        <div className="w-16 h-16 rounded-full bg-primary/10 border border-primary/20 flex items-center justify-center text-3xl mx-auto mb-6">
          🧠
        </div>

        <h2 className="text-xl font-bold text-center mb-1">Analyzing your resume</h2>
        <p className="text-sm text-muted-foreground text-center mb-8">
          Running AI scoring pipeline — this takes about 60–90 seconds
        </p>

        {/* Progress bar */}
        <div className="w-full bg-muted rounded-full h-2 mb-2 overflow-hidden">
          <div
            className="h-full bg-primary rounded-full transition-all duration-500 ease-out"
            style={{ width: `${displayPct}%` }}
          />
        </div>
        <p className="text-xs text-muted-foreground text-right mb-8">{displayPct}%</p>

        {/* Step indicators */}
        <div className="grid grid-cols-2 gap-3">
          {STEPS.map((step, i) => {
            const done = activeStep > i + 1;
            const active = activeStep === i + 1;
            return (
              <div
                key={step.label}
                className={`glass-card rounded-xl px-3 py-2.5 flex items-center gap-2.5 transition-all duration-300 ${
                  active ? "border-primary/40" : done ? "border-emerald-400/30" : ""
                }`}
              >
                <div
                  className={`w-2 h-2 rounded-full flex-shrink-0 transition-all duration-300 ${
                    done
                      ? "bg-emerald-400"
                      : active
                      ? "bg-primary animate-pulse"
                      : "bg-muted-foreground/30"
                  }`}
                />
                <span
                  className={`text-xs transition-colors duration-300 ${
                    active || done ? "text-foreground" : "text-muted-foreground"
                  }`}
                >
                  {step.label}
                </span>
                {done && <span className="ml-auto text-emerald-400 text-xs">✓</span>}
              </div>
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
      <div className="text-muted-foreground text-sm">Loading…</div>
    </div>
  );

  if (match.status === "pending" || match.status === "processing") {
    return <ProcessingScreen />;
  }

  if (match.status === "failed") {
    return (
      <div className="max-w-2xl mx-auto px-6 py-10 text-center">
        <div className="text-5xl mb-6">❌</div>
        <h2 className="text-xl font-bold text-destructive">Analysis Failed</h2>
        <p className="text-muted-foreground mt-2">{match.feedback_text || "An error occurred"}</p>
      </div>
    );
  }

  const score = match.final_score || 0;

  return (
    <div className="max-w-4xl mx-auto px-6 py-10">
      <h1 className="text-3xl font-bold mb-8">Match Results</h1>

      <div className="glass-card rounded-2xl p-8 mb-6 text-center relative overflow-hidden">
        {score < 70 && (
          <div className="absolute top-0 left-0 w-full bg-amber-500/20 text-amber-500 text-xs py-1.5 font-medium">
            Score is low. Consider rewriting your resume.
          </div>
        )}
        <div className="text-xs uppercase tracking-widest text-muted-foreground mb-4 mt-4">Overall Match Score</div>
        <div className={`text-6xl font-extrabold ${getScoreColor(score)}`}>{Math.round(score)}</div>
        <div className="text-sm text-muted-foreground mt-1">/ 100</div>
        <div className="flex flex-col items-center gap-4 mt-6">
          {match.role_detected && (
            <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-primary/10 border border-primary/20 text-sm text-primary">
              🎯 {match.role_detected}
            </div>
          )}
          <Link 
            href={`/rewrite/${match.id}`}
            className="inline-flex items-center gap-2 px-6 py-2.5 rounded-xl bg-primary text-primary-foreground hover:bg-primary/90 font-medium transition-all shadow-lg hover:shadow-primary/25"
          >
            ✨ Auto-Rewrite Resume
          </Link>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        {[
          { label: "BERT Semantic",  value: match.bert_score,    color: "text-purple-400" },
          { label: "TF-IDF Cosine",  value: match.tfidf_score,   color: "text-blue-400" },
          { label: "Keyword Match",  value: match.keyword_score, color: "text-emerald-400" },
          { label: "LLM Score",      value: match.llm_score,     color: "text-amber-400" },
        ].map((s) => (
          <div key={s.label} className="glass-card rounded-xl p-4 text-center">
            <div className={`text-2xl font-bold ${s.color}`}>
              {s.value != null ? Math.round(s.value) : "—"}
            </div>
            <div className="text-xs text-muted-foreground mt-1">{s.label}</div>
          </div>
        ))}
      </div>

      {match.feedback_text && (
        <div className="glass-card rounded-xl p-6 mb-6 border-l-4 border-primary">
          <p className="text-sm leading-relaxed text-muted-foreground">{match.feedback_text}</p>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        <div className="glass-card rounded-xl p-6">
          <h3 className="text-xs uppercase tracking-widest text-muted-foreground mb-3">✅ Matched Keywords</h3>
          <div className="flex flex-wrap gap-2">
            {(match.matched_keywords || []).map((kw) => (
              <span key={kw} className="px-2.5 py-1 rounded-md text-xs bg-emerald-400/10 text-emerald-400 border border-emerald-400/20">{kw}</span>
            ))}
            {(!match.matched_keywords || match.matched_keywords.length === 0) && (
              <span className="text-sm text-muted-foreground">None</span>
            )}
          </div>
        </div>
        <div className="glass-card rounded-xl p-6">
          <h3 className="text-xs uppercase tracking-widest text-muted-foreground mb-3">❌ Missing Keywords</h3>
          <div className="flex flex-wrap gap-2">
            {(match.missing_keywords || []).map((kw) => (
              <span key={kw} className="px-2.5 py-1 rounded-md text-xs bg-destructive/10 text-destructive border border-destructive/20">{kw}</span>
            ))}
            {(!match.missing_keywords || match.missing_keywords.length === 0) && (
              <span className="text-sm text-muted-foreground">None</span>
            )}
          </div>
        </div>
      </div>

      {match.llm_verdict && (
        <div className="glass-card rounded-xl p-6">
          <h3 className="text-xs uppercase tracking-widest text-muted-foreground mb-4">🤖 AI Verdict</h3>
          <p className="text-sm mb-4">{match.llm_verdict.one_line_summary}</p>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <h4 className="text-xs text-emerald-400 font-medium mb-2">Strengths</h4>
              <ul className="space-y-1">
                {(match.llm_verdict.strengths || []).map((s, i) => (
                  <li key={i} className="text-sm text-muted-foreground">• {s}</li>
                ))}
              </ul>
            </div>
            <div>
              <h4 className="text-xs text-destructive font-medium mb-2">Gaps</h4>
              <ul className="space-y-1">
                {(match.llm_verdict.gaps || []).map((g, i) => (
                  <li key={i} className="text-sm text-muted-foreground">• {g}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}