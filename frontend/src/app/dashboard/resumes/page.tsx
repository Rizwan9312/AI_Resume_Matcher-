"use client";
import { useEffect, useState } from "react";
import api from "@/lib/api";
import { Resume } from "@/types";
import { formatFileSize } from "@/lib/utils";

export default function ResumesPage() {
  const [resumes, setResumes] = useState<Resume[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get("/resumes")
      .then((res) => { setResumes(res.data.resumes || []); setLoading(false); })
      .catch((_err) => setLoading(false));
  }, []);

  const handleDelete = async (id: string) => {
    if (window.confirm("Are you sure you want to delete this resume?")) {
      await api.delete(`/resumes/${id}`);
      setResumes(resumes.filter((r) => r.id !== id));
    }
  };

  if (loading) return <div className="p-10 text-muted-foreground text-center">Loading resumes...</div>;

  return (
    <div className="max-w-4xl mx-auto px-6 py-10">
      <h1 className="text-3xl font-bold mb-8 text-foreground">Your Resumes</h1>
      {resumes.length === 0 ? (
        <div className="glass-card rounded-2xl p-16 text-center border border-border/50 bg-background/30 backdrop-blur-md">
          <div className="text-5xl mb-6">📄</div>
          <h2 className="text-xl font-semibold mb-2">No resumes found</h2>
          <p className="text-muted-foreground">Upload a resume to get started with your analysis.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {resumes.map((r) => {
            let statusColor = "bg-muted text-muted-foreground";
            if (r.parse_status === "pending") statusColor = "bg-amber-500/20 text-amber-500 border-amber-500/30";
            else if (r.parse_status === "done") statusColor = "bg-emerald-500/20 text-emerald-500 border-emerald-500/30";
            else if (r.parse_status === "failed") statusColor = "bg-red-500/20 text-red-500 border-red-500/30";

            return (
              <div key={r.id} className="glass-card rounded-xl p-5 flex items-center justify-between border border-border/50 hover:bg-white/[0.02] transition-colors">
                <div>
                  <p className="font-medium text-foreground">{r.filename}</p>
                  <div className="flex items-center gap-3 mt-2 text-xs text-muted-foreground">
                    <span>{formatFileSize(r.file_size_bytes)}</span>
                    <span>•</span>
                    <span>{new Date(r.created_at).toLocaleDateString()}</span>
                    <span>•</span>
                    <span className={`px-2 py-0.5 rounded-full text-[10px] uppercase font-semibold border ${statusColor}`}>
                      {r.parse_status}
                    </span>
                  </div>
                </div>
                <button 
                  onClick={() => handleDelete(r.id)} 
                  className="px-3 py-1.5 rounded-md text-xs font-medium text-destructive bg-destructive/10 hover:bg-destructive/20 transition-colors border border-destructive/20"
                >
                  Delete
                </button>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
