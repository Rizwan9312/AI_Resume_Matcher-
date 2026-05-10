"use client";
import { Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import api from "@/lib/api";
import Link from "next/link";
import GlassCard from "@/components/GlassCard";
import Button from "@/components/Button";

function NewMatchPageInner() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [step, setStep] = useState(1);
  const [file, setFile] = useState<File | null>(null);
  const [jdText, setJdText] = useState("");
  const [jdTitle, setJdTitle] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [resumeId, setResumeId] = useState("");
  const [dragOver, setDragOver] = useState(false);
  const [extractedKeywords, setExtractedKeywords] = useState<string[]>([]);
  const [resumeParsedText, setResumeParsedText] = useState("");
  const [isExtracting, setIsExtracting] = useState(false);

  useEffect(() => {
    const jobId = searchParams.get("jobId");
    if (jobId) {
      const fetchJob = async () => {
        try {
          const res = await api.get(`/jobs/${jobId}`);
          if (res.data.raw_text) setJdText(res.data.raw_text);
          if (res.data.title) setJdTitle(res.data.title);
        } catch (err) {
          console.error("Failed to load pre-filled job description", err);
        }
      };
      fetchJob();
    }
  }, [searchParams]);

  useEffect(() => {
    if (step === 2 && resumeId && !resumeParsedText) {
      const interval = setInterval(async () => {
        try {
          const res = await api.get(`/resumes/${resumeId}`);
          if (res.data.parse_status === "done" && res.data.parsed_text) {
            setResumeParsedText(res.data.parsed_text.toLowerCase());
            clearInterval(interval);
          } else if (res.data.parse_status === "failed") {
            setError("Resume parsing failed.");
            clearInterval(interval);
          }
        } catch (err) {
          console.error("Failed to fetch resume status", err);
        }
      }, 2000);
      return () => clearInterval(interval);
    }
  }, [step, resumeId, resumeParsedText]);

  useEffect(() => {
    if (step === 2 && jdText.trim().length > 10) {
      setIsExtracting(true);
      const timer = setTimeout(async () => {
        try {
          const res = await api.post("/jobs/extract-keywords", { raw_text: jdText });
          setExtractedKeywords(res.data.keywords || []);
        } catch (err) {
          console.error("Failed to extract keywords", err);
        } finally {
          setIsExtracting(false);
        }
      }, 800);
      return () => clearTimeout(timer);
    } else if (jdText.trim().length <= 10) {
      setExtractedKeywords([]);
    }
  }, [step, jdText]);

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    try {
      const fd = new FormData();
      fd.append("file", file);
      const res = await api.post("/resumes", fd, { headers: { "Content-Type": "multipart/form-data" } });
      setResumeId(res.data.id);
      setStep(2);
    } catch (_err) { setError("Upload failed"); }
    finally { setLoading(false); }
  };

  const handleMatch = async () => {
    if (!resumeId || !jdText.trim()) return;
    setLoading(true);
    try {
      const jdRes = await api.post("/jobs", { raw_text: jdText, title: jdTitle || undefined });
      const matchRes = await api.post("/matches", { resume_id: resumeId, job_id: jdRes.data.id });
      router.push(`/match/${matchRes.data.match_id}`);
    } catch (_err) { setError("Failed to start match"); }
    finally { setLoading(false); }
  };

  const matchedKeywords = extractedKeywords.filter(kw => resumeParsedText.includes(kw.toLowerCase()));
  const matchPercentage = extractedKeywords.length > 0 ? Math.round((matchedKeywords.length / extractedKeywords.length) * 100) : 0;

  return (
    <div className="max-w-4xl mx-auto px-6 py-10">
      {/* Back link */}
      <Link href="/dashboard" className="inline-flex items-center gap-2 text-sm text-ag-text-secondary hover:text-ag-text transition mb-8">
        ← Back to Dashboard
      </Link>

      <h1 className="font-syne font-bold text-3xl text-ag-text mb-2">
        New Match Analysis
      </h1>
      <p className="text-sm text-ag-text-secondary mb-8">
        Upload your resume and paste a job description to get AI-powered scoring.
      </p>

      {error && (
        <div className="bg-ag-danger/10 border border-ag-danger/30 text-ag-danger text-sm rounded-xl px-4 py-3 mb-6">
          {error}
        </div>
      )}

      {/* Scoring method badges */}
      <div className="flex flex-wrap gap-2 mb-8">
        {["BERT", "TF-IDF", "Keyword Match", "LLM Judge"].map((method) => (
          <span
            key={method}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full border border-white/[0.08] bg-surface/60 text-xs text-ag-text-secondary font-mono"
          >
            <svg className="w-3 h-3 text-ag-accent" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
            </svg>
            {method}
          </span>
        ))}
      </div>

      {step === 1 && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Upload zone */}
          <GlassCard className="p-8" hover={false}>
            <h2 className="font-syne font-semibold text-lg text-ag-text mb-4">📄 Upload Resume</h2>
            <div
              onClick={() => document.getElementById("fi")?.click()}
              onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
              onDragLeave={() => setDragOver(false)}
              onDrop={(e) => { e.preventDefault(); setDragOver(false); if (e.dataTransfer.files[0]) setFile(e.dataTransfer.files[0]); }}
              className={`border-2 border-dashed rounded-2xl p-12 text-center cursor-pointer transition-all duration-300 ${
                dragOver
                  ? "border-ag-accent bg-ag-accent/5"
                  : file
                  ? "border-ag-success/40 bg-ag-success/5"
                  : "border-white/[0.08] hover:border-ag-accent/40"
              }`}
            >
              {file ? (
                <div>
                  <p className="text-ag-success font-medium">✓ {file.name}</p>
                  <p className="text-xs text-ag-text-muted mt-1">{(file.size / 1024).toFixed(0)} KB</p>
                </div>
              ) : (
                <>
                  <div className="text-4xl mb-3 opacity-40">📤</div>
                  <p className="font-medium text-ag-text">Drag your resume here or click to browse</p>
                  <p className="text-sm text-ag-text-muted mt-1">PDF or DOCX, max 10MB</p>
                </>
              )}
            </div>
            <input id="fi" type="file" accept=".pdf,.docx" className="hidden" onChange={(e) => e.target.files?.[0] && setFile(e.target.files[0])} />
            <Button
              onClick={handleUpload}
              disabled={!file || loading}
              variant="primary"
              size="lg"
              className="w-full mt-6"
            >
              {loading ? "Uploading…" : "Upload & Continue →"}
            </Button>
          </GlassCard>

          {/* Info panel */}
          <GlassCard className="p-8 flex flex-col justify-center" hover={false}>
            <h3 className="font-syne font-semibold text-lg text-ag-text mb-4">How it works</h3>
            <div className="space-y-4">
              {[
                { step: "1", text: "Upload your resume (PDF/DOCX)" },
                { step: "2", text: "Paste the target job description" },
                { step: "3", text: "Get AI-powered multi-score analysis" },
                { step: "4", text: "Auto-rewrite to optimize your match" },
              ].map((s) => (
                <div key={s.step} className="flex items-start gap-3">
                  <span className="w-6 h-6 rounded-full bg-ag-accent/10 border border-ag-accent/20 flex items-center justify-center text-xs font-mono text-ag-accent flex-shrink-0">
                    {s.step}
                  </span>
                  <span className="text-sm text-ag-text-secondary">{s.text}</span>
                </div>
              ))}
            </div>
          </GlassCard>
        </div>
      )}

      {step === 2 && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Job Description */}
          <GlassCard className="p-8" hover={false}>
            <h2 className="font-syne font-semibold text-lg text-ag-text mb-4">📋 Job Description</h2>
            <input
              type="text"
              value={jdTitle}
              onChange={(e) => setJdTitle(e.target.value)}
              className="w-full input-dark rounded-xl px-4 py-3 text-sm mb-4"
              placeholder="Job title (optional)"
            />
            <textarea
              value={jdText}
              onChange={(e) => setJdText(e.target.value)}
              className="w-full input-dark rounded-xl px-4 py-3 text-sm min-h-[240px] resize-y font-mono"
              placeholder="Paste job description here…"
            />
            <div className="flex justify-between items-center mt-2">
              <span className="text-[10px] text-ag-text-muted font-mono">
                {jdText.length} characters
              </span>
            </div>
            <Button
              onClick={handleMatch}
              disabled={!jdText.trim() || loading}
              variant="primary"
              size="lg"
              className="w-full mt-6"
            >
              {loading ? "Starting…" : "Run AI Analysis →"}
            </Button>
          </GlassCard>

          {/* Keyword Panel */}
          <div className="space-y-6">
            {extractedKeywords.length > 0 && (
              <GlassCard className="p-6" hover={false}>
                <div className="flex justify-between items-center mb-4">
                  <h3 className="font-syne font-semibold text-sm text-ag-text">ATS Keyword Optimizer</h3>
                  <span className="text-xs font-mono px-2.5 py-1 bg-ag-accent/10 text-ag-accent rounded-lg">
                    {matchedKeywords.length}/{extractedKeywords.length} ({matchPercentage}%)
                  </span>
                </div>
                <div className="flex flex-wrap gap-2">
                  {extractedKeywords.map(kw => {
                    const isMatch = resumeParsedText.includes(kw.toLowerCase());
                    return (
                      <span
                        key={kw}
                        className={`text-[11px] font-medium px-2.5 py-1 rounded-full border transition ${
                          isMatch
                            ? "bg-ag-success/10 text-ag-success border-ag-success/20"
                            : "bg-ag-danger/10 text-ag-danger border-ag-danger/20"
                        }`}
                      >
                        {kw} {isMatch ? "✓" : "✗"}
                      </span>
                    );
                  })}
                </div>
                {isExtracting && (
                  <p className="text-xs text-ag-text-muted mt-3 animate-pulse">Extracting keywords...</p>
                )}
                {!isExtracting && !resumeParsedText && (
                  <p className="text-xs text-ag-warning mt-3 animate-pulse">
                    Waiting for resume parsing to finish to check keywords...
                  </p>
                )}
              </GlassCard>
            )}

            {/* Resume info */}
            <GlassCard className="p-6" hover={false}>
              <h3 className="font-syne font-semibold text-sm text-ag-text mb-3">Resume Status</h3>
              <div className="flex items-center gap-3">
                <div className={`w-2.5 h-2.5 rounded-full ${resumeParsedText ? "bg-ag-success" : "bg-ag-warning animate-pulse"}`} />
                <span className="text-sm text-ag-text-secondary">
                  {resumeParsedText ? "Parsed and ready" : "Parsing resume..."}
                </span>
              </div>
            </GlassCard>
          </div>
        </div>
      )}
    </div>
  );
}

export default function NewMatchPage() {
  return (
    <Suspense fallback={<div className="p-10 text-center text-ag-text-muted">Loading...</div>}>
      <NewMatchPageInner />
    </Suspense>
  );
}