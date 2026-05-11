"use client";
import { useEffect, useState, useRef } from "react";
import { useParams, useRouter } from "next/navigation";
import api from "@/lib/api";
import { RewriteSession } from "@/types";
import GlassCard from "@/components/GlassCard";
import Button from "@/components/Button";
import JobRecommendations from "@/components/JobRecommendations";

const STEPS = [
  { label: "Analyzing job description", pct: 15 },
  { label: "Extracting key requirements", pct: 35 },
  { label: "Rewriting experience section", pct: 70 },
  { label: "Optimizing for ATS", pct: 90 },
];

function ProcessingScreen() {
  const [activeStep, setActiveStep] = useState(0);
  const [displayPct, setDisplayPct] = useState(0);

  useEffect(() => {
    const delays = [1500, 4000, 10000, 16000];
    const timers = delays.map((d, i) =>
      setTimeout(() => setActiveStep(i + 1), d)
    );
    return () => timers.forEach(clearTimeout);
  }, []);

  useEffect(() => {
    const target = activeStep < STEPS.length ? STEPS[activeStep]?.pct ?? 0 : 95;
    const current = activeStep === 0 ? 0 : STEPS[activeStep - 1]?.pct ?? 0;
    const diff = target - current;
    let frame = 0;
    const total = 40;
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
          <span className="text-3xl">✍️</span>
        </div>

        <h2 className="font-syne font-bold text-xl text-center text-ag-text mb-1">
          Rewriting your resume
        </h2>
        <p className="text-sm text-ag-text-secondary text-center mb-8">
          Our AI is completely overhauling your resume. This may take up to 2 minutes...
        </p>

        {/* Indeterminate-style progress */}
        <div className="w-full bg-white/[0.04] rounded-full h-2 mb-2 overflow-hidden">
          <div className="h-full rounded-full progress-fill" style={{ width: `${displayPct}%` }} />
        </div>
        <p className="text-xs text-ag-text-muted text-right mb-8 font-mono">{displayPct}%</p>

        {/* Step labels */}
        <div className="grid grid-cols-1 gap-3">
          {STEPS.map((step, i) => {
            const done = activeStep > i + 1;
            const active = activeStep === i + 1;
            return (
              <GlassCard
                key={step.label}
                hover={false}
                className={`rounded-xl px-4 py-3 flex items-center gap-3 transition-all duration-300 ${
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

export default function RewritePage() {
  const params = useParams();
  const router = useRouter();
  const [session, setSession] = useState<RewriteSession | null>(null);
  const [polling, setPolling] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const startedRef = useRef(false);

  useEffect(() => {
    if (!params.match_id) return;

    const startRewrite = async () => {
      try {
        const res = await api.post("/rewrites", { match_id: params.match_id });
        setSession(res.data);
      } catch (err: any) {
        setError(err.response?.data?.detail || "Failed to start rewrite process");
        setPolling(false);
      }
    };

    if (!startedRef.current) {
      startedRef.current = true;
      startRewrite();
    }
  }, [params.match_id]);

  useEffect(() => {
    if (!session?.id || !polling) return;

    const poll = async () => {
      try {
        const res = await api.get(`/rewrites/${session.id}`);
        setSession(res.data);
        if (res.data.status === "complete" || res.data.status === "failed") {
          setPolling(false);
        }
      } catch (err) {
        console.error("Polling error", err);
      }
    };

    const interval = setInterval(poll, 3000);
    return () => clearInterval(interval);
  }, [session?.id, polling]);

  const handleDownload = () => {
    if (!session?.rewrites?.rewritten_resume) return;
    const blob = new Blob([session.rewrites.rewritten_resume], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `Rewritten_Resume_${new Date().getTime()}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  /* ── State: Error ──────────────────────────────────────── */
  if (error) {
    return (
      <div className="max-w-2xl mx-auto px-6 py-20 text-center">
        <GlassCard className="p-10" hover={false}>
          <div className="text-5xl mb-6">❌</div>
          <h2 className="font-syne font-bold text-2xl text-ag-danger mb-4">Rewrite Failed</h2>
          <p className="text-ag-text-secondary mb-8">{error}</p>
          <Button variant="ghost" onClick={() => router.back()}>Go Back</Button>
        </GlassCard>
      </div>
    );
  }

  /* ── State: Processing ─────────────────────────────────── */
  if (!session || session.status === "pending" || session.status === "processing") {
    return <ProcessingScreen />;
  }

  /* ── State: Failed ─────────────────────────────────────── */
  if (session.status === "failed") {
    return (
      <div className="max-w-2xl mx-auto px-6 py-20 text-center">
        <GlassCard className="p-10" hover={false}>
          <div className="text-5xl mb-6">❌</div>
          <h2 className="font-syne font-bold text-2xl text-ag-danger mb-4">Rewrite Failed</h2>
          <p className="text-ag-text-secondary mb-8">An error occurred while rewriting your resume.</p>
          <Button variant="ghost" onClick={() => router.back()}>Go Back</Button>
        </GlassCard>
      </div>
    );
  }

  /* ── State: Complete ───────────────────────────────────── */
  const { rewrites } = session;

  return (
    <div className="max-w-5xl mx-auto px-6 py-10">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
        <div>
          <h1 className="font-syne font-bold text-3xl text-ag-text">✨ Your Rewritten Resume</h1>
          <p className="text-ag-text-secondary mt-1 text-sm">
            Optimized for maximum ATS visibility and impact.
          </p>
        </div>
        <Button onClick={handleDownload} variant="primary" size="md">
          📥 Download .txt
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Main document */}
        <div className="lg:col-span-2">
          <GlassCard className="p-8" hover={false}>
            <div className="flex items-center gap-2 mb-6">
              <h3 className="text-xs uppercase tracking-widest text-ag-text-muted">Document View</h3>
              <span className="text-[9px] px-2 py-0.5 rounded-full bg-ag-accent/10 text-ag-accent border border-ag-accent/20">
                AI-generated
              </span>
            </div>
            <div className="whitespace-pre-wrap font-mono text-sm bg-bg/50 p-6 rounded-xl border border-white/[0.04] h-[800px] overflow-y-auto text-ag-text-secondary leading-relaxed">
              {rewrites?.rewritten_resume || "No resume text available."}
            </div>
          </GlassCard>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Score improvement */}
          <GlassCard className="p-6" hover={false}>
            <h3 className="text-xs uppercase tracking-widest text-ag-text-muted mb-4">📈 Expected Impact</h3>
            <div className="text-2xl font-bold text-ag-success font-mono">
              {rewrites?.estimated_score_improvement || "+ N/A"}
            </div>
            <p className="text-sm text-ag-text-muted mt-1">Score Improvement</p>
          </GlassCard>

          {/* Suggestions */}
          <GlassCard className="p-6" hover={false}>
            <h3 className="text-xs uppercase tracking-widest text-ag-text-muted mb-4">💡 Overall Suggestions</h3>
            <ul className="space-y-3">
              {(rewrites?.overall_suggestions || []).map((s, i) => (
                <li key={i} className="text-sm flex gap-2">
                  <span className="text-ag-accent mt-0.5">•</span>
                  <span className="text-ag-text-secondary">{s}</span>
                </li>
              ))}
            </ul>
          </GlassCard>

          {/* ATS Keywords */}
          <GlassCard className="p-6" hover={false}>
            <h3 className="text-xs uppercase tracking-widest text-ag-text-muted mb-4">🎯 ATS Keywords Added</h3>
            <div className="flex flex-wrap gap-2">
              {(rewrites?.ats_keywords_added || []).map((kw) => (
                <span key={kw} className="px-2.5 py-1 rounded-md text-xs bg-ag-success/10 text-ag-success border border-ag-success/20">
                  {kw}
                </span>
              ))}
            </div>
          </GlassCard>

          {/* Sections improved */}
          <GlassCard className="p-6" hover={false}>
            <h3 className="text-xs uppercase tracking-widest text-ag-text-muted mb-4">🛠️ Sections Improved</h3>
            <div className="space-y-4">
              {Object.entries(rewrites?.sections_improved || {}).map(([section, desc]) => (
                <div key={section}>
                  <h4 className="text-xs font-semibold capitalize mb-1 text-ag-text">{section}</h4>
                  <p className="text-sm text-ag-text-secondary">{desc as string}</p>
                </div>
              ))}
            </div>
          </GlassCard>
        </div>
      </div>

      {/* Full-width download */}
      <div className="mt-8">
        <Button onClick={handleDownload} variant="primary" size="lg" className="w-full">
          📥 Download Optimized Resume (.txt)
        </Button>
      </div>

      {/* Job Recommendations — after rewrite completion */}
      {session.resume_id && (
        <JobRecommendations
          resumeId={session.resume_id}
          matchResultId={params.match_id as string}
          autoTrigger={false}
        />
      )}
    </div>
  );
}
