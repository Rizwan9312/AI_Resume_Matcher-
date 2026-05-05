"use client";

import { useState, Suspense } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import api from "@/lib/api";

function ResetPasswordForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const token = searchParams.get("token");

  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  if (!token) {
    return (
      <div className="glass-card rounded-2xl p-8 text-center">
        <p className="text-destructive mb-4">Invalid or missing reset token.</p>
        <Link href="/forgot-password" className="text-primary hover:underline">Request a new one</Link>
      </div>
    );
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setMessage("");

    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    setLoading(true);
    try {
      const res = await api.post("/auth/reset-password", { token, new_password: password });
      setMessage(res.data.message || "Password successfully reset.");
      setTimeout(() => router.push("/login"), 2000);
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: { message?: string } } } })?.response?.data?.detail?.message;
      setError(msg || "Failed to reset password. The link might be expired.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="glass-card rounded-2xl p-8 space-y-5">
      {error && (
        <div className="bg-destructive/10 border border-destructive/30 text-destructive text-sm rounded-lg px-4 py-3">{error}</div>
      )}
      {message && (
        <div className="bg-emerald-500/10 border border-emerald-500/30 text-emerald-500 text-sm rounded-lg px-4 py-3">{message}</div>
      )}
      
      <div>
        <label className="block text-xs font-medium text-muted-foreground uppercase tracking-wider mb-2">New Password</label>
        <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required minLength={8}
          className="w-full bg-background border border-border rounded-lg px-4 py-3 text-sm focus:outline-none focus:border-primary transition" placeholder="••••••••" />
      </div>
      <div>
        <label className="block text-xs font-medium text-muted-foreground uppercase tracking-wider mb-2">Confirm Password</label>
        <input type="password" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} required minLength={8}
          className="w-full bg-background border border-border rounded-lg px-4 py-3 text-sm focus:outline-none focus:border-primary transition" placeholder="••••••••" />
      </div>
      <button type="submit" disabled={loading}
        className="w-full bg-primary text-primary-foreground py-3 rounded-lg font-semibold hover:opacity-90 transition disabled:opacity-40">
        {loading ? "Resetting..." : "Reset Password"}
      </button>
    </form>
  );
}

export default function ResetPasswordPage() {
  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="w-12 h-12 mx-auto rounded-xl bg-gradient-to-br from-blue-500 to-cyan-400 flex items-center justify-center text-white font-bold text-xl mb-4">R</div>
          <h1 className="text-2xl font-bold tracking-tight">Create New Password</h1>
          <p className="text-sm text-muted-foreground mt-2">Please enter your new password below</p>
        </div>
        <Suspense fallback={<div className="text-center text-muted-foreground">Loading...</div>}>
          <ResetPasswordForm />
        </Suspense>
      </div>
    </div>
  );
}
