"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import api, { setTokens } from "@/lib/api";
import FloatingOrbs from "@/components/FloatingOrbs";
import Button from "@/components/Button";

const BENEFITS = [
  "BERT + TF-IDF scoring",
  "Role-aware weighting",
  "One-click AI rewrite",
];

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [benefitIdx, setBenefitIdx] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setBenefitIdx((i) => (i + 1) % BENEFITS.length);
    }, 3000);
    return () => clearInterval(timer);
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const res = await api.post("/auth/login", { email, password });
      setTokens(res.data.access_token, res.data.refresh_token);
      router.push("/dashboard");
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: { message?: string } } } })?.response?.data?.detail?.message;
      setError(msg || "Login failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex">
      {/* Left Panel — Visual (hidden on mobile) */}
      <div className="hidden lg:flex lg:w-[55%] bg-surface relative items-center justify-center overflow-hidden">
        {/* Decorative floating resume card */}
        <div className="relative z-10 w-72">
          <div className="glass-card no-lift rounded-2xl p-8 border border-white/[0.08]">
            {/* Fake resume lines */}
            <div className="w-20 h-2 bg-ag-accent/40 rounded mb-4" />
            <div className="w-full h-1.5 bg-white/[0.06] rounded mb-2" />
            <div className="w-4/5 h-1.5 bg-white/[0.06] rounded mb-2" />
            <div className="w-full h-1.5 bg-white/[0.06] rounded mb-2" />
            <div className="w-3/5 h-1.5 bg-white/[0.06] rounded mb-6" />
            {/* Score ring (decorative) */}
            <div className="flex justify-center mb-6">
              <div className="w-16 h-16 rounded-full border-4 border-ag-success/60 flex items-center justify-center">
                <span className="text-ag-success font-mono font-bold text-sm">82</span>
              </div>
            </div>
            <div className="w-full h-1.5 bg-white/[0.06] rounded mb-2" />
            <div className="w-2/3 h-1.5 bg-white/[0.06] rounded" />
          </div>
        </div>

        {/* Cycling benefits */}
        <div className="absolute bottom-24 left-0 right-0 text-center z-10">
          <p className="text-sm font-medium text-ag-text-secondary transition-all duration-500">
            {BENEFITS[benefitIdx]}
          </p>
        </div>

        {/* Testimonial */}
        <div className="absolute bottom-8 left-8 right-8 z-10">
          <div className="glass-card no-lift rounded-xl p-4 text-center">
            <p className="text-xs text-ag-text-secondary italic">&ldquo;Landed my dream job after the AI rewrite.&rdquo;</p>
            <p className="text-[10px] text-ag-text-muted mt-1">— Software Engineer</p>
          </div>
        </div>

        {/* Background glow */}
        <div className="absolute inset-0 pointer-events-none">
          <div className="absolute top-1/4 left-1/3 w-80 h-80 bg-ag-accent/8 rounded-full blur-[100px]" />
          <div className="absolute bottom-1/4 right-1/4 w-60 h-60 bg-ag-cyan/6 rounded-full blur-[80px]" />
        </div>
      </div>

      {/* Right Panel — Form */}
      <div className="w-full lg:w-[45%] relative flex flex-col min-h-screen">
        <FloatingOrbs />

        {/* Logo */}
        <div className="relative z-10 px-8 pt-8">
          <Link href="/" className="inline-flex items-center gap-2" aria-label="Back to home">
            <span className="font-syne font-bold text-lg text-ag-text">ResumeIQ</span>
            <span className="w-1.5 h-1.5 rounded-full bg-ag-accent" />
          </Link>
        </div>

        {/* Form — centered */}
        <div className="relative z-10 flex-1 flex items-center justify-center px-8">
          <div className="w-full max-w-sm">
            <p className="section-label mb-2">WELCOME BACK</p>
            <h1 className="font-syne font-bold text-3xl text-ag-text mb-2">
              Sign in to your workspace
            </h1>
            <p className="text-sm text-ag-text-secondary mb-8">
              Continue your job search journey.
            </p>

            <form onSubmit={handleSubmit} className="space-y-5">
              {error && (
                <div className="bg-ag-danger/10 border border-ag-danger/30 text-ag-danger text-sm rounded-xl px-4 py-3">
                  {error}
                </div>
              )}

              <div>
                <label className="block text-xs font-medium text-ag-text-secondary uppercase tracking-wider mb-2">
                  Email
                </label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  aria-label="Email address"
                  className="w-full input-dark rounded-xl px-4 py-3 text-sm"
                  placeholder="you@example.com"
                />
              </div>

              <div>
                <div className="flex items-center justify-between mb-2">
                  <label className="block text-xs font-medium text-ag-text-secondary uppercase tracking-wider">
                    Password
                  </label>
                  <Link
                    href="/forgot-password"
                    className="text-xs text-ag-text-muted hover:text-ag-accent transition"
                  >
                    Forgot password?
                  </Link>
                </div>
                <div className="relative">
                  <input
                    type={showPassword ? "text" : "password"}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    aria-label="Password"
                    className="w-full input-dark rounded-xl px-4 py-3 text-sm pr-12"
                    placeholder="••••••••"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-ag-text-muted hover:text-ag-text-secondary transition text-xs"
                    aria-label={showPassword ? "Hide password" : "Show password"}
                  >
                    {showPassword ? "Hide" : "Show"}
                  </button>
                </div>
              </div>

              <Button
                type="submit"
                variant="primary"
                size="lg"
                disabled={loading}
                className="w-full"
              >
                {loading ? "Signing in…" : "Sign In →"}
              </Button>

              {/* Divider */}
              <div className="flex items-center gap-4">
                <div className="flex-1 h-px bg-white/[0.06]" />
                <span className="text-xs text-ag-text-muted">or</span>
                <div className="flex-1 h-px bg-white/[0.06]" />
              </div>

              <p className="text-center text-sm text-ag-text-secondary">
                Don&apos;t have an account?{" "}
                <Link
                  href="/register"
                  className="text-ag-accent hover:underline font-medium"
                >
                  Create one →
                </Link>
              </p>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}
