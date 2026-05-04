"use client";
import { useEffect, useState } from "react";
import api from "@/lib/api";
import { Resume } from "@/types";
import { formatFileSize } from "@/lib/utils";

export default function ResumesPage() {
  const [resumes, setResumes] = useState<Resume[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get("/resumes").then((res) => { setResumes(res.data.resumes || []); setLoading(false); }).catch((_err) => setLoading(false));
  }, []);

  const handleDelete = async (id: string) => {
    await api.delete(`/resumes/${id}`);
    setResumes(resumes.filter((r) => r.id !== id));
  };

  if (loading) return <div className="p-10 text-muted-foreground">Loading…</div>;

  return (
    <div className="max-w-4xl mx-auto px-6 py-10">
      <h1 className="text-3xl font-bold mb-8">Your Resumes</h1>
      {resumes.length === 0 ? (
        <div className="glass-card rounded-2xl p-12 text-center">
          <div className="text-4xl mb-4">📄</div>
          <p className="text-muted-foreground">No resumes uploaded yet</p>
        </div>
      ) : (
        <div className="space-y-4">
          {resumes.map((r) => (
            <div key={r.id} className="glass-card rounded-xl p-5 flex items-center justify-between">
              <div>
                <p className="font-medium">{r.filename}</p>
                <p className="text-xs text-muted-foreground mt-1">{formatFileSize(r.file_size_bytes)} · {r.parse_status} · {new Date(r.created_at).toLocaleDateString()}</p>
              </div>
              <button onClick={() => handleDelete(r.id)} className="text-xs text-destructive hover:underline">Delete</button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
