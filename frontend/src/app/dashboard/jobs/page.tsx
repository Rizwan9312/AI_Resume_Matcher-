"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import api from "@/lib/api";

type JobLibraryItem = {
  id: string;
  title: string | null;
  company: string | null;
  raw_text: string;
  industry_tag: string | null;
  role_tag: string | null;
  best_score: number | null;
  best_resume_id: string | null;
  created_at: string;
};

export default function JobLibraryPage() {
  const router = useRouter();
  const [jobs, setJobs] = useState<JobLibraryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [filterTag, setFilterTag] = useState<string | null>(null);

  // Editing state for tags
  const [editingJobId, setEditingJobId] = useState<string | null>(null);
  const [editIndustry, setEditIndustry] = useState("");
  const [editRole, setEditRole] = useState("");

  const fetchJobs = async () => {
    try {
      const res = await api.get("/jobs/library");
      setJobs(res.data.jobs || []);
    } catch (_err) {
      setError("Failed to load job descriptions");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchJobs();
  }, []);

  const handleUseJd = (id: string) => {
    router.push(`/match/new?jobId=${id}`);
  };

  const handleTagClick = (tag: string) => {
    if (filterTag === tag) {
      setFilterTag(null); // toggle off
    } else {
      setFilterTag(tag);
    }
  };

  const startEditing = (job: JobLibraryItem) => {
    setEditingJobId(job.id);
    setEditIndustry(job.industry_tag || "");
    setEditRole(job.role_tag || "");
  };

  const saveTags = async (id: string) => {
    try {
      await api.patch(`/jobs/${id}/tags`, {
        industry_tag: editIndustry.trim() || null,
        role_tag: editRole.trim() || null,
      });
      setEditingJobId(null);
      await fetchJobs();
    } catch (_err) {
      alert("Failed to save tags");
    }
  };

  const filteredJobs = jobs.filter((j) => {
    if (!filterTag) return true;
    return j.industry_tag === filterTag || j.role_tag === filterTag;
  });

  return (
    <div className="max-w-6xl mx-auto px-6 py-10">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold tracking-tight mb-2">Job Library</h1>
          <p className="text-muted-foreground">Manage and reuse your saved job descriptions.</p>
        </div>
      </div>

      {error && (
        <div className="bg-destructive/10 border border-destructive/30 text-destructive px-4 py-3 rounded-lg mb-6 text-sm">
          {error}
        </div>
      )}

      {filterTag && (
        <div className="mb-6 flex items-center gap-2">
          <span className="text-sm text-muted-foreground">Filtering by tag:</span>
          <span className="bg-primary/20 text-primary px-3 py-1 rounded-full text-sm font-medium flex items-center gap-2">
            {filterTag}
            <button onClick={() => setFilterTag(null)} className="hover:text-primary-foreground hover:bg-primary rounded-full w-4 h-4 flex items-center justify-center transition-colors">
              ×
            </button>
          </span>
        </div>
      )}

      {loading ? (
        <div className="text-center py-20 text-muted-foreground">Loading job descriptions...</div>
      ) : filteredJobs.length === 0 ? (
        <div className="text-center py-20 bg-muted/20 border border-border/50 rounded-2xl">
          <p className="text-muted-foreground mb-4">No job descriptions found.</p>
          <button onClick={() => router.push("/match/new")} className="bg-primary text-primary-foreground px-4 py-2 rounded-lg text-sm font-medium">
            Start a New Match
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredJobs.map((job) => (
            <div key={job.id} className="glass-card rounded-2xl p-6 flex flex-col hover:border-primary/30 transition-all">
              <div className="mb-4 flex-1">
                <h3 className="font-semibold text-lg line-clamp-1" title={job.title || "Untitled Job"}>
                  {job.title || "Untitled Job"}
                </h3>
                {job.company && <p className="text-sm text-muted-foreground line-clamp-1">{job.company}</p>}
                
                <div className="mt-4 flex flex-wrap gap-2">
                  {editingJobId === job.id ? (
                    <div className="flex flex-col gap-2 w-full mt-2">
                      <input 
                        type="text" 
                        placeholder="Industry Tag (e.g. Tech)" 
                        value={editIndustry} 
                        onChange={(e) => setEditIndustry(e.target.value)}
                        className="bg-background border border-border rounded px-2 py-1 text-xs focus:outline-none focus:border-primary"
                      />
                      <input 
                        type="text" 
                        placeholder="Role Tag (e.g. Engineering)" 
                        value={editRole} 
                        onChange={(e) => setEditRole(e.target.value)}
                        className="bg-background border border-border rounded px-2 py-1 text-xs focus:outline-none focus:border-primary"
                      />
                      <div className="flex gap-2 justify-end">
                        <button onClick={() => setEditingJobId(null)} className="text-xs text-muted-foreground hover:text-foreground">Cancel</button>
                        <button onClick={() => saveTags(job.id)} className="text-xs bg-primary text-primary-foreground px-2 py-1 rounded">Save</button>
                      </div>
                    </div>
                  ) : (
                    <>
                      {job.industry_tag ? (
                        <button 
                          onClick={() => handleTagClick(job.industry_tag!)}
                          className="bg-blue-500/10 text-blue-500 hover:bg-blue-500/20 px-2.5 py-1 rounded-md text-xs font-medium transition-colors"
                        >
                          {job.industry_tag}
                        </button>
                      ) : null}
                      {job.role_tag ? (
                        <button 
                          onClick={() => handleTagClick(job.role_tag!)}
                          className="bg-purple-500/10 text-purple-500 hover:bg-purple-500/20 px-2.5 py-1 rounded-md text-xs font-medium transition-colors"
                        >
                          {job.role_tag}
                        </button>
                      ) : null}
                      
                      <button 
                        onClick={() => startEditing(job)}
                        className="text-xs text-muted-foreground hover:text-foreground ml-auto bg-muted/50 px-2 py-1 rounded"
                      >
                        Edit Tags
                      </button>
                    </>
                  )}
                </div>
              </div>

              <div className="border-t border-border pt-4 mt-2 flex items-center justify-between">
                <div>
                  <span className="text-xs text-muted-foreground block mb-1">Best Match Score</span>
                  {job.best_score !== null ? (
                    <span className="font-semibold text-emerald-400">{job.best_score}/100</span>
                  ) : (
                    <span className="text-xs text-muted-foreground italic">No matches</span>
                  )}
                </div>
                
                <button
                  onClick={() => handleUseJd(job.id)}
                  className="bg-primary/10 text-primary hover:bg-primary hover:text-primary-foreground px-4 py-2 rounded-lg text-sm font-medium transition-colors"
                >
                  Use this JD
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
