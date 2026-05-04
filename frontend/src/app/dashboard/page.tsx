"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import api from "@/lib/api";

export default function DashboardPage() {
  const [stats, setStats] = useState({ resumes: 0, matches: 0, avgScore: 0 });

  useEffect(() => {
    const loadStats = async () => {
      try {
        const [resumeRes, matchRes] = await Promise.all([
          api.get("/resumes"),
          api.get("/matches?limit=100"),
        ]);
        const matches = matchRes.data.matches || [];
        const completed = matches.filter((m: { status: string; final_score?: number }) => m.status === "complete");
        const avg = completed.length
          ? Math.round(completed.reduce((s: number, m: { final_score?: number }) => s + (m.final_score || 0), 0) / completed.length)
          : 0;
        setStats({
          resumes: (resumeRes.data.resumes || []).length,
          matches: matches.length,
          avgScore: avg,
        });
      } catch (_err) { /* logged in interceptor */ }
    };
    loadStats();
  }, []);

  return (
    <div className="max-w-6xl mx-auto px-6 py-10">
      <div className="mb-10">
        <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-muted-foreground mt-1">Your resume intelligence overview</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
        {[
          { label: "Resumes Uploaded", value: stats.resumes, icon: "📄" },
          { label: "Matches Run", value: stats.matches, icon: "🎯" },
          { label: "Avg Score", value: `${stats.avgScore}/100`, icon: "📊" },
        ].map((s) => (
          <div key={s.label} className="glass-card rounded-2xl p-6">
            <div className="text-2xl mb-3">{s.icon}</div>
            <div className="text-3xl font-bold">{s.value}</div>
            <div className="text-sm text-muted-foreground mt-1">{s.label}</div>
          </div>
        ))}
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Link href="/match/new" className="glass-card rounded-2xl p-8 hover:border-primary/30 transition group">
          <div className="text-3xl mb-4">🚀</div>
          <h3 className="text-lg font-semibold group-hover:text-primary transition">New Match Analysis</h3>
          <p className="text-sm text-muted-foreground mt-2">Upload a resume and paste a job description to get instant AI scoring</p>
        </Link>
        <Link href="/dashboard/resumes" className="glass-card rounded-2xl p-8 hover:border-primary/30 transition group">
          <div className="text-3xl mb-4">📁</div>
          <h3 className="text-lg font-semibold group-hover:text-primary transition">Manage Resumes</h3>
          <p className="text-sm text-muted-foreground mt-2">View, upload, and organize your resume library</p>
        </Link>
      </div>
    </div>
  );
}
