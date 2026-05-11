"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useEffect } from "react";
import api from "@/lib/api";
import GlassCard from "@/components/GlassCard";
import Button from "@/components/Button";

interface JobRec {
  id: string;
  job_title: string;
  employer_name: string;
  employer_logo?: string;
  job_publisher: string;
  job_location: string;
  job_employment_type: string;
  job_apply_link: string;
  job_posted_at: string | null;
  relevance_score: number;
  job_salary_min?: number;
  job_salary_max?: number;
  job_salary_currency?: string;
}

interface Props {
  resumeId: string;
  matchResultId?: string;
  autoTrigger?: boolean;
}

export default function JobRecommendations({
  resumeId,
  matchResultId,
  autoTrigger = true,
}: Props) {
  const queryClient = useQueryClient();

  // Fire the trigger once on mount so a Celery task is queued if not already running
  useEffect(() => {
    if (!autoTrigger) return;
    api
      .post("/jobs-feed/trigger", null, {
        params: { resume_id: resumeId, match_result_id: matchResultId },
      })
      .catch(() => {});
  }, [resumeId, matchResultId, autoTrigger]);

  // Poll every 4s while empty, slow to 30s once results arrive
  const { data: jobs = [], isLoading } = useQuery<JobRec[]>({
    queryKey: ["job-recs", resumeId, matchResultId],
    queryFn: async () => {
      const res = await api.get("/jobs-feed/", {
        params: {
          resume_id: resumeId,
          match_result_id: matchResultId,
          limit: 10,
        },
      });
      return res.data;
    },
    refetchInterval: (query) =>
      !query.state.data || query.state.data.length === 0 ? 4000 : 30000,
    staleTime: 30000,
  });

  const dismiss = useMutation({
    mutationFn: (id: string) =>
      api.patch(`/jobs-feed/${id}/dismiss`),
    onSuccess: () =>
      queryClient.invalidateQueries({ queryKey: ["job-recs"] }),
  });

  const formatSalary = (
    min?: number,
    max?: number,
    currency?: string
  ): string | null => {
    if (!min && !max) return null;
    const sym = currency ?? "$";
    const fmt = (n: number) => `${sym}${(n / 1000).toFixed(0)}k`;
    if (min && max) return `${fmt(min)} – ${fmt(max)}`;
    if (max) return `Up to ${fmt(max)}`;
    return `From ${fmt(min!)}`;
  };

  const scoreColor = (score: number) => {
    if (score >= 60) return "text-ag-success";
    if (score >= 35) return "text-ag-warning";
    return "text-ag-text-muted";
  };

  // Skeleton while waiting for first results
  if (isLoading && jobs.length === 0) {
    return (
      <section className="mt-8">
        <SectionHeader count={0} loading />
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <GlassCard key={i} hover={false} className="h-36 rounded-xl opacity-50 animate-pulse" />
          ))}
        </div>
      </section>
    );
  }

  // Empty state while Celery task is still running
  if (!isLoading && jobs.length === 0) {
    return (
      <section className="mt-8">
        <SectionHeader count={0} loading={false} />
        <GlassCard hover={false} className="p-8 text-center">
          <div className="text-3xl mb-3">🔍</div>
          <p className="text-sm text-ag-text-secondary">
            Searching for matching jobs — usually takes 10–20 seconds…
          </p>
        </GlassCard>
      </section>
    );
  }

  return (
    <section className="mt-8">
      <SectionHeader count={jobs.length} loading={false} />

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {jobs.map((job) => (
          <GlassCard
            key={job.id}
            hover={true}
            className="p-5 rounded-xl flex flex-col gap-2"
          >
            {/* Header: logo + publisher badge + match score */}
            <div className="flex items-center gap-2">
              {job.employer_logo && (
                <img
                  src={job.employer_logo}
                  alt={job.employer_name}
                  className="w-7 h-7 rounded-md object-contain"
                />
              )}
              <span className="text-[10px] px-2 py-0.5 rounded-full border border-[var(--border-color)] text-ag-text-secondary">
                {job.job_publisher}
              </span>
              <span className={`ml-auto text-xs font-medium font-mono ${scoreColor(job.relevance_score)}`}>
                {job.relevance_score.toFixed(0)}% match
              </span>
            </div>

            {/* Job title */}
            <p className="font-medium text-[15px] text-ag-text leading-tight">
              {job.job_title}
            </p>

            {/* Company name */}
            <p className="text-sm text-ag-text-secondary">
              {job.employer_name}
            </p>

            {/* Location and type */}
            <p className="text-xs text-ag-text-muted">
              {[job.job_location, job.job_employment_type].filter(Boolean).join(" · ")}
            </p>

            {/* Salary if available */}
            {formatSalary(job.job_salary_min, job.job_salary_max, job.job_salary_currency) && (
              <p className="text-xs text-ag-success font-medium">
                {formatSalary(job.job_salary_min, job.job_salary_max, job.job_salary_currency)}
              </p>
            )}

            {/* Actions */}
            <div className="flex items-center gap-3 mt-2">
              <a
                href={job.job_apply_link}
                target="_blank"
                rel="noopener noreferrer"
              >
                <Button variant="primary" size="sm">
                  Apply →
                </Button>
              </a>
              <button
                onClick={() => dismiss.mutate(job.id)}
                className="text-xs text-ag-text-muted hover:text-ag-text transition cursor-pointer"
              >
                Dismiss
              </button>
            </div>
          </GlassCard>
        ))}
      </div>
    </section>
  );
}

function SectionHeader({ count, loading }: { count: number; loading: boolean }) {
  return (
    <div className="flex items-baseline gap-3 mb-4">
      <h2 className="font-syne font-bold text-lg text-ag-text">
        🔗 Matching Jobs
      </h2>
      <span className="text-xs text-ag-text-muted">
        {loading
          ? "searching LinkedIn & Indeed…"
          : count > 0
          ? `${count} results · updated live`
          : "from LinkedIn & Indeed"}
      </span>
    </div>
  );
}
