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
  const [history, setHistory] = useState<any[]>([]);
  const [comparing, setComparing] = useState(false);
  const [compareMatchId, setCompareMatchId] = useState<string>("");
  const [compareData, setCompareData] = useState<{match1: MatchResult, match2: MatchResult} | null>(null);

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

  useEffect(() => {
    if (match?.status === "complete" && history.length === 0) {
      api.get(`/resumes/${match.resume_id}/history`)
        .then(res => setHistory(res.data.history || []))
        .catch(console.error);
    }
  }, [match?.status, match?.resume_id, history.length]);

  const handleCompare = async (e: React.ChangeEvent<HTMLSelectElement>) => {
    const id2 = e.target.value;
    setCompareMatchId(id2);
    if (!id2) {
      setCompareData(null);
      return;
    }
    try {
      const res = await api.get(`/matches/compare?match_id_1=${match?.id}&match_id_2=${id2}`);
      setCompareData(res.data);
    } catch (err) {
      console.error(err);
    }
  };

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
          
          <div className="mt-2 flex flex-col items-center">
            {!comparing ? (
              <button 
                onClick={() => setComparing(true)}
                className="text-sm text-muted-foreground hover:text-primary transition-colors underline"
              >
                Compare with another match
              </button>
            ) : (
              <div className="flex items-center gap-3">
                <select 
                  value={compareMatchId} 
                  onChange={handleCompare}
                  className="bg-background border border-border rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:border-primary text-foreground"
                >
                  <option value="">-- Select a match to compare --</option>
                  {history.filter(h => h.match_id !== match.id).map(h => (
                    <option key={h.match_id} value={h.match_id}>
                      {h.job_title || "Unknown Job"} - {Math.round(h.final_score || 0)} ({(new Date(h.created_at)).toLocaleDateString()})
                    </option>
                  ))}
                  {history.filter(h => h.match_id !== match.id).length === 0 && (
                    <option disabled>No other matches found for this resume</option>
                  )}
                </select>
                <button 
                  onClick={() => { setComparing(false); setCompareData(null); setCompareMatchId(""); }}
                  className="text-xs text-muted-foreground hover:text-destructive"
                >
                  Cancel
                </button>
              </div>
            )}
          </div>
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

      {compareData && (
        <div className="mt-12 pt-10 border-t border-border/50">
          <h2 className="text-2xl font-bold mb-6">Match Comparison</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {[compareData.match1, compareData.match2].map((m, idx) => (
              <div key={m.id} className={`glass-card rounded-2xl p-6 border ${idx === 0 ? "border-primary/30" : "border-border/50"}`}>
                <h3 className="text-sm uppercase tracking-widest text-muted-foreground mb-4">
                  {idx === 0 ? "Current Match" : "Compared Match"}
                </h3>
                <div className={`text-4xl font-bold mb-6 ${getScoreColor(m.final_score || 0)}`}>
                  {Math.round(m.final_score || 0)} <span className="text-lg text-muted-foreground font-normal">/ 100</span>
                </div>
                
                <div className="space-y-4">
                  <div>
                    <div className="text-xs text-muted-foreground mb-1">Scores (BERT / TF-IDF / Key / LLM)</div>
                    <div className="text-sm font-medium">
                      {m.bert_score != null ? Math.round(m.bert_score) : "—"} / {" "}
                      {m.tfidf_score != null ? Math.round(m.tfidf_score) : "—"} / {" "}
                      {m.keyword_score != null ? Math.round(m.keyword_score) : "—"} / {" "}
                      {m.llm_score != null ? Math.round(m.llm_score) : "—"}
                    </div>
                  </div>
                  <div>
                    <div className="text-xs text-muted-foreground mb-1">Matched Keywords</div>
                    <div className="text-sm flex flex-wrap gap-1">
                      {(m.matched_keywords || []).slice(0, 5).map((kw: string) => (
                        <span key={kw} className="px-1.5 py-0.5 bg-emerald-500/10 text-emerald-400 rounded text-xs">{kw}</span>
                      ))}
                      {(m.matched_keywords || []).length > 5 && <span className="text-xs text-muted-foreground">+{m.matched_keywords!.length - 5} more</span>}
                    </div>
                  </div>
                  <div>
                    <div className="text-xs text-muted-foreground mb-1">Missing Keywords</div>
                    <div className="text-sm flex flex-wrap gap-1">
                      {(m.missing_keywords || []).slice(0, 5).map((kw: string) => (
                        <span key={kw} className="px-1.5 py-0.5 bg-destructive/10 text-destructive rounded text-xs">{kw}</span>
                      ))}
                      {(m.missing_keywords || []).length > 5 && <span className="text-xs text-muted-foreground">+{m.missing_keywords!.length - 5} more</span>}
                    </div>
                  </div>
                  {m.feedback_text && (
                    <div>
                      <div className="text-xs text-muted-foreground mb-1">Feedback</div>
                      <p className="text-xs line-clamp-3 text-muted-foreground">{m.feedback_text}</p>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {history.length > 0 && (
        <div className="mt-12 pt-10 border-t border-border/50">
          <h2 className="text-2xl font-bold mb-6">Historical Score Trend</h2>
          <div className="glass-card rounded-2xl p-2">
            <div className="space-y-1">
              {history.map(h => (
                <Link 
                  key={h.match_id} 
                  href={`/match/${h.match_id}`} 
                  className={`flex items-center justify-between p-4 rounded-xl transition-all ${h.match_id === match.id ? 'bg-primary/5 border border-primary/20' : 'hover:bg-white/[0.02] border border-transparent'}`}
                >
                  <div>
                    <p className="font-medium text-foreground">{h.job_title || "Unknown Job"}</p>
                    <p className="text-xs text-muted-foreground mt-1">
                      {new Date(h.created_at).toLocaleDateString()} at {new Date(h.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </p>
                  </div>
                  <div className="flex items-center gap-4">
                    {h.match_id === match.id && (
                      <span className="text-[10px] uppercase tracking-wider text-primary font-semibold px-2 py-1 bg-primary/10 rounded-full">Current</span>
                    )}
                    <div className={`text-2xl font-bold ${getScoreColor(h.final_score)} w-12 text-right`}>
                      {h.final_score != null ? Math.round(h.final_score) : "—"}
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}