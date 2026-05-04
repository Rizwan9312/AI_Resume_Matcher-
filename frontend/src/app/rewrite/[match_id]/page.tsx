"use client";
import { useEffect, useState, useRef } from "react";
import { useParams, useRouter } from "next/navigation";
import api from "@/lib/api";
import { RewriteSession } from "@/types";

const STEPS = [
  { label: "Analyzing job description", pct: 15 },
  { label: "Evaluating original resume", pct: 35 },
  { label: "Generating ATS-optimized content", pct: 70 },
  { label: "Finalizing formatting", pct: 90 },
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
        <div className="w-16 h-16 rounded-full bg-primary/10 border border-primary/20 flex items-center justify-center text-3xl mx-auto mb-6">
          ✍️
        </div>
        <h2 className="text-xl font-bold text-center mb-1">Rewriting your resume</h2>
        <p className="text-sm text-muted-foreground text-center mb-8">
          Our AI is completely overhauling your resume. This may take up to 2 minutes...
        </p>

        <div className="w-full bg-muted rounded-full h-2 mb-2 overflow-hidden">
          <div
            className="h-full bg-primary rounded-full transition-all duration-500 ease-out"
            style={{ width: `${displayPct}%` }}
          />
        </div>
        <p className="text-xs text-muted-foreground text-right mb-8">{displayPct}%</p>

        <div className="grid grid-cols-1 gap-3">
          {STEPS.map((step, i) => {
            const done = activeStep > i + 1;
            const active = activeStep === i + 1;
            return (
              <div
                key={step.label}
                className={`glass-card rounded-xl px-4 py-3 flex items-center gap-3 transition-all duration-300 ${
                  active ? "border-primary/40" : done ? "border-emerald-400/30" : ""
                }`}
              >
                <div
                  className={`w-2.5 h-2.5 rounded-full flex-shrink-0 transition-all duration-300 ${
                    done
                      ? "bg-emerald-400"
                      : active
                      ? "bg-primary animate-pulse"
                      : "bg-muted-foreground/30"
                  }`}
                />
                <span
                  className={`text-sm transition-colors duration-300 ${
                    active || done ? "text-foreground" : "text-muted-foreground"
                  }`}
                >
                  {step.label}
                </span>
                {done && <span className="ml-auto text-emerald-400 text-sm">✓</span>}
              </div>
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
        // First request creates the session using the match_id
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

  if (error) {
    return (
      <div className="max-w-2xl mx-auto px-6 py-20 text-center">
        <div className="text-5xl mb-6">❌</div>
        <h2 className="text-2xl font-bold text-destructive mb-4">Rewrite Failed</h2>
        <p className="text-muted-foreground mb-8">{error}</p>
        <button onClick={() => router.back()} className="px-6 py-2 rounded-xl bg-secondary text-secondary-foreground hover:bg-secondary/80">
          Go Back
        </button>
      </div>
    );
  }

  if (!session || session.status === "pending" || session.status === "processing") {
    return <ProcessingScreen />;
  }

  if (session.status === "failed") {
    return (
      <div className="max-w-2xl mx-auto px-6 py-20 text-center">
        <div className="text-5xl mb-6">❌</div>
        <h2 className="text-2xl font-bold text-destructive mb-4">Rewrite Failed</h2>
        <p className="text-muted-foreground mb-8">An error occurred while rewriting your resume.</p>
        <button onClick={() => router.back()} className="px-6 py-2 rounded-xl bg-secondary text-secondary-foreground hover:bg-secondary/80">
          Go Back
        </button>
      </div>
    );
  }

  const { rewrites } = session;

  return (
    <div className="max-w-5xl mx-auto px-6 py-10">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
        <div>
          <h1 className="text-3xl font-bold">✨ Your Rewritten Resume</h1>
          <p className="text-muted-foreground mt-1">Optimized for maximum ATS visibility and impact.</p>
        </div>
        <button 
          onClick={handleDownload}
          className="px-6 py-2.5 rounded-xl bg-primary text-primary-foreground hover:bg-primary/90 font-medium transition-all shadow-lg hover:shadow-primary/25 flex items-center gap-2"
        >
          📥 Download .txt
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-6">
          <div className="glass-card rounded-2xl p-8">
            <h3 className="text-sm uppercase tracking-widest text-muted-foreground mb-6">Document View</h3>
            <div className="whitespace-pre-wrap font-mono text-sm bg-background/50 p-6 rounded-xl border border-border/50 h-[800px] overflow-y-auto">
              {rewrites?.rewritten_resume || "No resume text available."}
            </div>
          </div>
        </div>

        <div className="space-y-6">
          <div className="glass-card rounded-2xl p-6">
            <h3 className="text-xs uppercase tracking-widest text-muted-foreground mb-4">📈 Expected Impact</h3>
            <div className="text-2xl font-bold text-emerald-400">
              {rewrites?.estimated_score_improvement || "+ N/A"}
            </div>
            <p className="text-sm text-muted-foreground mt-1">Score Improvement</p>
          </div>

          <div className="glass-card rounded-2xl p-6">
            <h3 className="text-xs uppercase tracking-widest text-muted-foreground mb-4">💡 Overall Suggestions</h3>
            <ul className="space-y-3">
              {(rewrites?.overall_suggestions || []).map((s, i) => (
                <li key={i} className="text-sm flex gap-2">
                  <span className="text-primary mt-0.5">•</span>
                  <span className="text-muted-foreground">{s}</span>
                </li>
              ))}
            </ul>
          </div>

          <div className="glass-card rounded-2xl p-6">
            <h3 className="text-xs uppercase tracking-widest text-muted-foreground mb-4">🎯 ATS Keywords Added</h3>
            <div className="flex flex-wrap gap-2">
              {(rewrites?.ats_keywords_added || []).map((kw) => (
                <span key={kw} className="px-2.5 py-1 rounded-md text-xs bg-emerald-400/10 text-emerald-400 border border-emerald-400/20">
                  {kw}
                </span>
              ))}
            </div>
          </div>

          <div className="glass-card rounded-2xl p-6">
            <h3 className="text-xs uppercase tracking-widest text-muted-foreground mb-4">🛠️ Sections Improved</h3>
            <div className="space-y-4">
              {Object.entries(rewrites?.sections_improved || {}).map(([section, desc]) => (
                <div key={section}>
                  <h4 className="text-xs font-semibold capitalize mb-1 text-foreground">{section}</h4>
                  <p className="text-sm text-muted-foreground">{desc as string}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
