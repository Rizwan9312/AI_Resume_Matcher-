"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import api from "@/lib/api";
import { MatchResult } from "@/types";
import { getScoreColor } from "@/lib/utils";

export default function MatchesPage() {
  const [matches, setMatches] = useState<MatchResult[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get("/matches?limit=50").then((res) => { setMatches(res.data.matches || []); setLoading(false); }).catch((_err) => setLoading(false));
  }, []);

  if (loading) return <div className="p-10 text-muted-foreground">Loading…</div>;

  return (
    <div className="max-w-4xl mx-auto px-6 py-10">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold">Match History</h1>
        <Link href="/match/new" className="bg-primary text-primary-foreground px-4 py-2 rounded-lg text-sm font-medium">New Match</Link>
      </div>
      {matches.length === 0 ? (
        <div className="glass-card rounded-2xl p-12 text-center">
          <div className="text-4xl mb-4">🎯</div>
          <p className="text-muted-foreground">No matches yet</p>
        </div>
      ) : (
        <div className="space-y-4">
          {matches.map((m) => (
            <Link key={m.id} href={`/match/${m.id}`} className="glass-card rounded-xl p-5 flex items-center justify-between hover:border-primary/20 transition block">
              <div>
                <p className="font-medium">{m.role_detected || "Analysis"}</p>
                <p className="text-xs text-muted-foreground mt-1">{m.status} · {new Date(m.created_at).toLocaleDateString()}</p>
              </div>
              {m.final_score != null && <div className={`text-2xl font-bold ${getScoreColor(m.final_score)}`}>{Math.round(m.final_score)}</div>}
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
