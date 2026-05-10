"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import api from "@/lib/api";
import GlassCard from "@/components/GlassCard";
import Button from "@/components/Button";

export default function DashboardPage() {
  const [stats, setStats] = useState({ resumes: 0, matches: 0, avgScore: 0, rewrites: 0 });
  const [recentMatches, setRecentMatches] = useState<any[]>([]);

  useEffect(() => {
    const loadStats = async () => {
      try {
        const [resumeRes, matchRes] = await Promise.all([
          api.get("/resumes"),
          api.get("/matches?limit=100"),
        ]);
        const matches = matchRes.data.matches || [];
        const completed = matches.filter(
          (m: { status: string; final_score?: number }) => m.status === "complete"
        );
        const avg = completed.length
          ? Math.round(
              completed.reduce(
                (s: number, m: { final_score?: number }) =>
                  s + (m.final_score || 0),
                0
              ) / completed.length
            )
          : 0;
        setStats({
          resumes: (resumeRes.data.resumes || []).length,
          matches: matches.length,
          avgScore: avg,
          rewrites: 0,
        });
        setRecentMatches(completed.slice(0, 5));
      } catch (_err) {
        /* logged in interceptor */
      }
    };
    loadStats();
  }, []);

  const getScoreColor = (score: number) => {
    if (score >= 80) return "text-ag-success";
    if (score >= 60) return "text-ag-warning";
    return "text-ag-danger";
  };

  return (
    <div className="max-w-6xl mx-auto px-6 py-10">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-10 gap-2">
        <div>
          <h1 className="font-syne font-bold text-3xl text-ag-text tracking-tight">
            Dashboard
          </h1>
          <p className="text-ag-text-secondary text-sm mt-1">
            Your resume intelligence overview
          </p>
        </div>
        <p className="text-xs text-ag-text-muted font-mono">
          {new Date().toLocaleDateString("en-US", {
            weekday: "long",
            year: "numeric",
            month: "long",
            day: "numeric",
          })}
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-10">
        {[
          { label: "Resumes Uploaded", value: stats.resumes, icon: "📄" },
          { label: "Matches Run", value: stats.matches, icon: "🎯" },
          { label: "Average Score", value: `${stats.avgScore}`, icon: "📊" },
          { label: "Rewrites Done", value: stats.rewrites, icon: "✨" },
        ].map((s) => (
          <GlassCard key={s.label} className="p-6">
            <div className="text-lg mb-3">{s.icon}</div>
            <div className="text-3xl font-bold font-mono text-ag-text">{s.value}</div>
            <div className="text-xs text-ag-text-secondary mt-1">{s.label}</div>
          </GlassCard>
        ))}
      </div>

      {/* Recent Matches */}
      {recentMatches.length > 0 && (
        <div className="mb-10">
          <h2 className="font-syne font-bold text-lg text-ag-text mb-4">
            Recent Matches
          </h2>
          <GlassCard className="p-2" hover={false}>
            <div className="divide-y divide-white/[0.04]">
              {recentMatches.map((m: any) => (
                <Link
                  key={m.id}
                  href={`/match/${m.id}`}
                  className="flex items-center justify-between px-4 py-3 rounded-xl hover:bg-white/[0.02] transition"
                >
                  <div>
                    <p className="text-sm font-medium text-ag-text">
                      Match Analysis
                    </p>
                    <p className="text-xs text-ag-text-muted mt-0.5">
                      {new Date(m.created_at).toLocaleDateString()}
                    </p>
                  </div>
                  <div className="flex items-center gap-3">
                    <span
                      className={`text-xs px-2 py-0.5 rounded-full ${
                        m.status === "complete"
                          ? "bg-ag-success/10 text-ag-success"
                          : "bg-ag-warning/10 text-ag-warning"
                      }`}
                    >
                      {m.status}
                    </span>
                    <span
                      className={`text-xl font-bold font-mono ${getScoreColor(
                        m.final_score || 0
                      )}`}
                    >
                      {m.final_score != null ? Math.round(m.final_score) : "—"}
                    </span>
                  </div>
                </Link>
              ))}
            </div>
          </GlassCard>
        </div>
      )}

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Link href="/match/new">
          <GlassCard className="p-8 group cursor-pointer">
            <div className="text-3xl mb-4">🚀</div>
            <h3 className="font-syne font-semibold text-lg text-ag-text group-hover:text-ag-accent transition mb-2">
              New Match Analysis
            </h3>
            <p className="text-sm text-ag-text-secondary">
              Upload a resume and paste a job description to get instant AI
              scoring
            </p>
          </GlassCard>
        </Link>
        <Link href="/dashboard/resumes">
          <GlassCard className="p-8 group cursor-pointer">
            <div className="text-3xl mb-4">📁</div>
            <h3 className="font-syne font-semibold text-lg text-ag-text group-hover:text-ag-accent transition mb-2">
              Manage Resumes
            </h3>
            <p className="text-sm text-ag-text-secondary">
              View, upload, and organize your resume library
            </p>
          </GlassCard>
        </Link>
      </div>
    </div>
  );
}
