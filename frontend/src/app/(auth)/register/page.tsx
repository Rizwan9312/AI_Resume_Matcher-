"use client";

import { useState, useMemo } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import api, { setTokens } from "@/lib/api";
import FloatingOrbs from "@/components/FloatingOrbs";
import GlassCard from "@/components/GlassCard";
import Button from "@/components/Button";

function getPasswordStrength(pw: string): number {
  let score = 0;
  if (pw.length >= 8) score++;
  if (/[A-Z]/.test(pw)) score++;
  if (/[0-9]/.test(pw)) score++;
  if (/[^A-Za-z0-9]/.test(pw)) score++;
  return score;
}

const strengthColors = ["#FF4D6D", "#FFB800", "#FFB800", "#00FF88"];
const strengthLabels = ["Weak", "Fair", "Good", "Strong"];

export default function RegisterPage() {
  const router = useRouter();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const strength = useMemo(() => getPasswordStrength(password), [password]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    setLoading(true);
    try {
      const res = await api.post("/auth/register", {
        email,
        password,
        full_name: fullName,
      });
      setTokens(res.data.access_token, res.data.refresh_token);
      router.push("/dashboard");
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: { message?: string } } } })?.response?.data?.detail?.message;
      setError(msg || "Registration failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-12 relative">
      <FloatingOrbs />

      <div className="relative z-10 w-full max-w-[480px]">
        {/* Logo */}
        <div className="text-center mb-6">
          <Link href="/" className="inline-flex items-center gap-2" aria-label="Back to home">
            <span className="font-syne font-bold text-xl text-ag-text">ResumeIQ</span>
            <span className="w-1.5 h-1.5 rounded-full bg-ag-accent" />
          </Link>
        </div>

        {/* Decorative step pill */}
        <div className="flex justify-center mb-6">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-white/[0.08] bg-surface/60 backdrop-blur-md">
            <span className="text-[10px] font-medium text-ag-text-secondary tracking-wider uppercase">
              Step 1 of 3
            </span>
          </div>
        </div>

        {/* Card container */}
        <GlassCard className="p-10 md:p-12" hover={false}>
          <p className="section-label mb-2">CREATE ACCOUNT</p>
          <h1 className="font-syne font-bold text-2xl text-ag-text mb-6">
            Start matching smarter
          </h1>

          <form onSubmit={handleSubmit} className="space-y-5">
            {error && (
              <div className="bg-ag-danger/10 border border-ag-danger/30 text-ag-danger text-sm rounded-xl px-4 py-3">
                {error}
              </div>
            )}

            {/* Full Name */}
            <div>
              <label className="block text-xs font-medium text-ag-text-secondary uppercase tracking-wider mb-2">
                Full Name
              </label>
              <input
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                required
                aria-label="Full name"
                className="w-full input-dark rounded-xl px-4 py-3 text-sm"
                placeholder="John Doe"
              />
            </div>

            {/* Email */}
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

            {/* Password + strength indicator */}
            <div>
              <label className="block text-xs font-medium text-ag-text-secondary uppercase tracking-wider mb-2">
                Password
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                minLength={8}
                aria-label="Password"
                className="w-full input-dark rounded-xl px-4 py-3 text-sm"
                placeholder="Min 8 characters"
              />
              {/* Strength bar */}
              {password.length > 0 && (
                <div className="mt-2">
                  <div className="flex gap-1">
                    {[0, 1, 2, 3].map((seg) => (
                      <div
                        key={seg}
                        className="flex-1 h-1 rounded-full transition-all duration-300"
                        style={{
                          background: seg < strength ? strengthColors[strength - 1] : "rgba(255,255,255,0.06)",
                        }}
                      />
                    ))}
                  </div>
                  <p
                    className="text-[10px] mt-1 font-medium"
                    style={{ color: strength > 0 ? strengthColors[strength - 1] : "#444466" }}
                  >
                    {strength > 0 ? strengthLabels[strength - 1] : ""}
                  </p>
                </div>
              )}
            </div>

            {/* Confirm Password */}
            <div>
              <label className="block text-xs font-medium text-ag-text-secondary uppercase tracking-wider mb-2">
                Confirm Password
              </label>
              <input
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
                minLength={8}
                aria-label="Confirm password"
                className="w-full input-dark rounded-xl px-4 py-3 text-sm"
                placeholder="Re-enter password"
              />
            </div>

            <Button
              type="submit"
              variant="primary"
              size="lg"
              disabled={loading}
              className="w-full"
            >
              {loading ? "Creating account…" : "Create Free Account →"}
            </Button>

            <p className="text-center text-sm text-ag-text-secondary">
              Already have an account?{" "}
              <Link href="/login" className="text-ag-accent hover:underline font-medium">
                Sign In
              </Link>
            </p>

            <p className="text-center text-[10px] text-ag-text-muted">
              By continuing, you agree to our Terms of Service
            </p>
          </form>
        </GlassCard>
      </div>
    </div>
  );
}
