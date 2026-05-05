"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import api from "@/lib/api";
import { MatchResult } from "@/types";

export default function MatchesPage() {
  const [matches, setMatches] = useState<MatchResult[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const limit = 20;

  useEffect(() => {
    setLoading(true);
    api.get(`/matches?page=${page}&limit=${limit}`)
      .then((res) => { 
        setMatches(res.data.matches || []); 
        setTotal(res.data.total || 0);
        setLoading(false); 
      })
      .catch((_err) => setLoading(false));
  }, [page]);

  const getScoreColor = (score: number | null | undefined) => {
    if (score == null) return "text-muted-foreground";
    if (score >= 80) return "text-emerald-500";
    if (score >= 60) return "text-amber-400";
    if (score >= 40) return "text-orange-500";
    return "text-red-500";
  };

  const totalPages = Math.ceil(total / limit);

  return (
    <div className="max-w-4xl mx-auto px-6 py-10">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold text-foreground">Match History</h1>
        <Link 
          href="/match/new" 
          className="bg-primary text-primary-foreground px-5 py-2.5 rounded-xl text-sm font-medium hover:bg-primary/90 transition-colors shadow-lg shadow-primary/20"
        >
          New Match
        </Link>
      </div>

      {loading && matches.length === 0 ? (
        <div className="p-10 text-muted-foreground text-center">Loading matches...</div>
      ) : matches.length === 0 ? (
        <div className="glass-card rounded-2xl p-16 text-center border border-border/50 bg-background/30 backdrop-blur-md">
          <div className="text-5xl mb-6">🎯</div>
          <h2 className="text-xl font-semibold mb-2">No matches found</h2>
          <p className="text-muted-foreground">Start a new match analysis to see your results here.</p>
        </div>
      ) : (
        <>
          <div className="space-y-4">
            {matches.map((m) => {
              let statusColor = "bg-muted text-muted-foreground";
              if (m.status === "pending" || m.status === "processing") statusColor = "bg-amber-500/20 text-amber-500 border-amber-500/30";
              else if (m.status === "complete") statusColor = "bg-emerald-500/20 text-emerald-500 border-emerald-500/30";
              else if (m.status === "failed") statusColor = "bg-red-500/20 text-red-500 border-red-500/30";

              return (
                <Link 
                  key={m.id} 
                  href={`/match/${m.id}`} 
                  className="glass-card rounded-xl p-5 flex items-center justify-between border border-border/50 hover:bg-white/[0.02] hover:border-primary/30 transition-all group block"
                >
                  <div>
                    <p className="font-medium text-foreground group-hover:text-primary transition-colors">
                      {m.role_detected || "Resume Analysis"}
                    </p>
                    <div className="flex items-center gap-3 mt-2 text-xs text-muted-foreground">
                      <span>{new Date(m.created_at).toLocaleDateString()} {new Date(m.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                      <span>•</span>
                      <span className={`px-2 py-0.5 rounded-full text-[10px] uppercase font-semibold border ${statusColor}`}>
                        {m.status}
                      </span>
                    </div>
                  </div>
                  
                  {m.final_score != null ? (
                    <div className="text-right">
                      <div className={`text-3xl font-bold ${getScoreColor(m.final_score)}`}>
                        {Math.round(m.final_score)}
                      </div>
                      <div className="text-[10px] uppercase tracking-wider text-muted-foreground mt-1">Match Score</div>
                    </div>
                  ) : (
                    <div className="text-right text-muted-foreground text-sm font-medium">
                      {m.status === "failed" ? "Failed" : "Pending..."}
                    </div>
                  )}
                </Link>
              );
            })}
          </div>

          {totalPages > 1 && (
            <div className="flex justify-center items-center gap-4 mt-8">
              <button 
                onClick={() => setPage(p => Math.max(1, p - 1))}
                disabled={page === 1}
                className="px-4 py-2 rounded-lg bg-secondary text-secondary-foreground disabled:opacity-50 hover:bg-secondary/80 transition-colors text-sm font-medium"
              >
                Previous
              </button>
              <span className="text-sm text-muted-foreground">
                Page {page} of {totalPages}
              </span>
              <button 
                onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
                className="px-4 py-2 rounded-lg bg-secondary text-secondary-foreground disabled:opacity-50 hover:bg-secondary/80 transition-colors text-sm font-medium"
              >
                Next
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
