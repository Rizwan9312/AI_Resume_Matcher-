/** Shared TypeScript types for the AI Resume Matcher frontend. */

export interface User {
  id: string;
  email: string;
  role: "job_seeker" | "recruiter" | "admin";
  full_name: string;
  tenant_id: string;
  is_verified: boolean;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

export interface Resume {
  id: string;
  filename: string;
  file_size_bytes: number;
  mime_type: string;
  parse_status: "pending" | "done" | "failed";
  parsed_sections?: Record<string, string>;
  created_at: string;
}

export interface Job {
  id: string;
  title?: string;
  company?: string;
  raw_text: string;
  parsed_data?: Record<string, unknown>;
  source_url?: string;
  created_at: string;
}

export interface MatchResult {
  id: string;
  status: "pending" | "processing" | "complete" | "failed";
  resume_id: string;
  job_id: string;
  final_score?: number;
  bert_score?: number;
  tfidf_score?: number;
  keyword_score?: number;
  llm_score?: number;
  role_detected?: string;
  weights_used?: Record<string, number>;
  score_breakdown?: Record<string, number>;
  matched_keywords?: string[];
  missing_keywords?: string[];
  section_scores?: Record<string, number>;
  llm_verdict?: {
    overall_fit: number;
    experience_match: number;
    skills_match: number;
    soft_skills_match: number;
    seniority_match: number;
    strengths: string[];
    gaps: string[];
    recommendation: string;
    one_line_summary: string;
  };
  feedback_text?: string;
  processing_ms?: number;
  created_at: string;
  completed_at?: string;
}

export interface RewriteSession {
  id: string;
  status: "pending" | "complete" | "failed";
  bullet_count?: number;
  weak_count?: number;
  rewrites?: Array<{
    original: string;
    rewritten_variants: string[];
    reason: string;
  }>;
  created_at: string;
}

export interface APIError {
  code: string;
  message: string;
}
