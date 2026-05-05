"use client";
import { useEffect, useState } from "react";
import api from "@/lib/api";
import { Resume } from "@/types";
import { formatFileSize, getScoreColor } from "@/lib/utils";

interface VersionItem {
  id: string;
  version_number: number;
  is_active: boolean;
  created_at: string;
  best_score: number | null;
}

export default function ResumesPage() {
  const [resumes, setResumes] = useState<Resume[]>([]);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState<Record<string, boolean>>({});
  const [versionsData, setVersionsData] = useState<Record<string, VersionItem[]>>({});

  const fetchResumes = () => {
    setLoading(true);
    api.get("/resumes")
      .then((res) => { setResumes(res.data.resumes || []); setLoading(false); })
      .catch((_err) => setLoading(false));
  };

  useEffect(() => {
    fetchResumes();
  }, []);

  const handleDelete = async (id: string) => {
    if (window.confirm("Are you sure you want to delete this resume?")) {
      await api.delete(`/resumes/${id}`);
      setResumes(resumes.filter((r) => r.id !== id));
    }
  };

  const handleToggleVersions = async (resumeId: string, groupId: string) => {
    const isExpanded = expanded[groupId];
    setExpanded({ ...expanded, [groupId]: !isExpanded });
    
    if (!isExpanded && !versionsData[groupId]) {
      try {
        const res = await api.get(`/resumes/${resumeId}/versions`);
        setVersionsData(prev => ({ ...prev, [groupId]: res.data.versions }));
      } catch (err) {
        console.error("Failed to fetch versions", err);
      }
    }
  };

  const handleSetActive = async (resumeId: string, groupId: string) => {
    try {
      await api.patch(`/resumes/${resumeId}/set-active`);
      fetchResumes(); // Refresh the main list
      // Refresh the inline versions list too
      const res = await api.get(`/resumes/${resumeId}/versions`);
      setVersionsData(prev => ({ ...prev, [groupId]: res.data.versions }));
    } catch (err) {
      console.error("Failed to set active", err);
    }
  };

  // Group resumes by their root family (parent_resume_id or id)
  const groupedResumes: Record<string, Resume[]> = {};
  resumes.forEach(r => {
    const groupId = r.parent_resume_id || r.id;
    if (!groupedResumes[groupId]) groupedResumes[groupId] = [];
    groupedResumes[groupId].push(r);
  });

  const displayResumes = Object.values(groupedResumes).map(group => {
    // Find the active one, or default to the first one (highest version generally)
    return group.find(r => r.is_active) || group[0];
  });

  if (loading && resumes.length === 0) return <div className="p-10 text-muted-foreground text-center">Loading resumes...</div>;

  return (
    <div className="max-w-4xl mx-auto px-6 py-10">
      <h1 className="text-3xl font-bold mb-8 text-foreground">Your Resumes</h1>
      {displayResumes.length === 0 ? (
        <div className="glass-card rounded-2xl p-16 text-center border border-border/50 bg-background/30 backdrop-blur-md">
          <div className="text-5xl mb-6">📄</div>
          <h2 className="text-xl font-semibold mb-2">No resumes found</h2>
          <p className="text-muted-foreground">Upload a resume to get started with your analysis.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {displayResumes.map((r) => {
            const groupId = r.parent_resume_id || r.id;
            const familySize = groupedResumes[groupId].length;
            const isExpanded = expanded[groupId] || false;
            const versions = versionsData[groupId] || [];

            let statusColor = "bg-muted text-muted-foreground";
            if (r.parse_status === "pending") statusColor = "bg-amber-500/20 text-amber-500 border-amber-500/30";
            else if (r.parse_status === "done") statusColor = "bg-emerald-500/20 text-emerald-500 border-emerald-500/30";
            else if (r.parse_status === "failed") statusColor = "bg-red-500/20 text-red-500 border-red-500/30";

            return (
              <div key={r.id} className="flex flex-col gap-2">
                <div className="glass-card rounded-xl p-5 flex items-center justify-between border border-border/50 hover:bg-white/[0.02] transition-colors">
                  <div>
                    <div className="flex items-center gap-3">
                      <p className="font-medium text-foreground">{r.filename}</p>
                      <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-primary/20 text-primary border border-primary/30">
                        v{r.version_number || 1}
                      </span>
                      {familySize > 1 && (
                        <button 
                          onClick={() => handleToggleVersions(r.id, groupId)}
                          className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-secondary text-secondary-foreground border border-border/50 hover:bg-secondary/80 transition-colors"
                        >
                          {isExpanded ? "Hide Versions" : `${familySize} Versions`}
                        </button>
                      )}
                    </div>
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

                {isExpanded && versions.length > 0 && (
                  <div className="ml-8 space-y-2 border-l-2 border-border/50 pl-4 py-2">
                    {versions.map(v => (
                      <div key={v.id} className="glass-card rounded-lg p-3 flex items-center justify-between border border-border/30 bg-background/50">
                        <div className="flex items-center gap-3">
                          <span className="text-sm font-semibold text-foreground w-6">v{v.version_number}</span>
                          <span className="text-xs text-muted-foreground w-24">
                            {new Date(v.created_at).toLocaleDateString()}
                          </span>
                          {v.best_score != null ? (
                            <span className={`text-xs font-semibold ${getScoreColor(v.best_score)}`}>
                              Best: {Math.round(v.best_score)}/100
                            </span>
                          ) : (
                            <span className="text-xs text-muted-foreground">No matches yet</span>
                          )}
                        </div>
                        
                        <div className="flex items-center gap-3">
                          {v.is_active ? (
                            <span className="px-2 py-1 rounded-md text-[10px] uppercase font-bold bg-emerald-500/20 text-emerald-500 border border-emerald-500/30">
                              Active
                            </span>
                          ) : (
                            <button 
                              onClick={() => handleSetActive(v.id, groupId)}
                              className="px-3 py-1 rounded-md text-xs font-medium text-primary bg-primary/10 hover:bg-primary/20 border border-primary/20 transition-colors"
                            >
                              Set Active
                            </button>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
