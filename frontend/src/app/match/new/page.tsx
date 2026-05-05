"use client";
import { useSearchParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import api from "@/lib/api";

export default function NewMatchPage() {
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

  return (
    <div className="max-w-2xl mx-auto px-6 py-10">
      <h1 className="text-3xl font-bold mb-8">New Match Analysis</h1>
      {error && <div className="bg-destructive/10 border border-destructive/30 text-destructive text-sm rounded-lg px-4 py-3 mb-6">{error}</div>}
      {step === 1 && (
        <div className="glass-card rounded-2xl p-8">
          <h2 className="text-lg font-semibold mb-4">📄 Upload Resume</h2>
          <div onClick={() => document.getElementById("fi")?.click()}
            onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
            onDragLeave={() => setDragOver(false)}
            onDrop={(e) => { e.preventDefault(); setDragOver(false); if (e.dataTransfer.files[0]) setFile(e.dataTransfer.files[0]); }}
            className={`border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition ${dragOver ? "border-primary bg-primary/5" : "border-border hover:border-primary/40"}`}>
            {file ? <p className="text-emerald-400">✓ {file.name}</p> : <><p className="font-medium">Drop resume here</p><p className="text-sm text-muted-foreground mt-1">PDF or DOCX, max 10MB</p></>}
          </div>
          <input id="fi" type="file" accept=".pdf,.docx" className="hidden" onChange={(e) => e.target.files?.[0] && setFile(e.target.files[0])} />
          <button onClick={handleUpload} disabled={!file || loading} className="w-full mt-6 bg-primary text-primary-foreground py-3 rounded-lg font-semibold disabled:opacity-40">{loading ? "Uploading…" : "Upload & Continue →"}</button>
        </div>
      )}
      {step === 2 && (
        <div className="glass-card rounded-2xl p-8">
          <h2 className="text-lg font-semibold mb-4">📋 Job Description</h2>
          <input type="text" value={jdTitle} onChange={(e) => setJdTitle(e.target.value)} className="w-full bg-background border border-border rounded-lg px-4 py-3 text-sm mb-4 focus:outline-none focus:border-primary" placeholder="Job title (optional)" />
          <textarea value={jdText} onChange={(e) => setJdText(e.target.value)} className="w-full bg-background border border-border rounded-lg px-4 py-3 text-sm min-h-[200px] resize-y focus:outline-none focus:border-primary font-mono" placeholder="Paste job description here…" />
          <button onClick={handleMatch} disabled={!jdText.trim() || loading} className="w-full mt-6 bg-primary text-primary-foreground py-3 rounded-lg font-semibold disabled:opacity-40">{loading ? "Starting…" : "Analyze Match →"}</button>
        </div>
      )}
    </div>
  );
}
