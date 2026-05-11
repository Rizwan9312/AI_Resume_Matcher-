"use client";

import Link from "next/link";
import { useRouter, usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import { clearTokens, getAccessToken } from "@/lib/api";
import api from "@/lib/api";
import ThemeToggle from "./ThemeToggle";

export default function Navbar() {
  const router = useRouter();
  const pathname = usePathname();
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  useEffect(() => {
    const token = getAccessToken();
    setIsLoggedIn(!!token);
  }, [pathname]);

  // Hide on landing, auth pages, and when not logged in
  const hideOn = ["/", "/login", "/register", "/forgot-password", "/reset-password"];
  if (hideOn.includes(pathname ?? "")) return null;
  if (!isLoggedIn) return null;

  // On dashboard pages, the sidebar handles nav — show a minimal top bar
  const isDashboard = pathname?.startsWith("/dashboard");

  const handleLogout = async () => {
    try {
      await api.post("/auth/logout", {});
    } catch (_err) {
      // clear regardless
    } finally {
      clearTokens();
      router.push("/login");
    }
  };

  // For non-dashboard pages (match, rewrite), show a compact top nav
  return (
    <nav className="sticky top-0 z-50 border-b border-[var(--border-color)] bg-[var(--nav-bg)] backdrop-blur-2xl">
      <div className="max-w-6xl mx-auto px-6 h-14 flex items-center justify-between gap-4">
        {/* Logo */}
        <Link
          href="/dashboard"
          className="flex items-center gap-2 flex-shrink-0 group"
          aria-label="Go to Dashboard"
        >
          <span className="font-syne font-bold text-[15px] text-ag-text tracking-tight">
            ResumeIQ
          </span>
          <span className="w-1.5 h-1.5 rounded-full bg-ag-accent" />
          <span className="text-[10px] font-medium text-ag-accent bg-ag-accent/10 rounded px-1.5 py-0.5 tracking-wide">
            BETA
          </span>
        </Link>

        {/* Nav links — desktop */}
        <div className="hidden md:flex items-center gap-1 flex-1 justify-center">
          {[
            { href: "/dashboard", label: "Dashboard" },
            { href: "/match/new", label: "New Analysis" },
            { href: "/dashboard/resumes", label: "Resumes" },
            { href: "/dashboard/jobs", label: "Jobs" },
            { href: "/dashboard/matches", label: "History" },
          ].map((link) => {
            const active = pathname === link.href;
            return (
              <Link
                key={link.href}
                href={link.href}
                className={`px-3 py-1.5 rounded-lg text-[13px] transition-all duration-200 whitespace-nowrap ${
                  active
                    ? "bg-ag-accent/10 text-ag-accent font-medium"
                    : "text-ag-text-secondary hover:text-ag-text hover:bg-[var(--border-subtle)]"
                }`}
              >
                {link.label}
              </Link>
            );
          })}
        </div>

        {/* Right side */}
        <div className="flex items-center gap-3 flex-shrink-0">
          <ThemeToggle />
          <div className="w-[28px] h-[28px] rounded-full bg-ag-accent/10 border border-ag-accent/20 flex items-center justify-center text-[11px] font-medium text-ag-accent flex-shrink-0">
            U
          </div>
          <button
            onClick={handleLogout}
            className="text-[13px] text-ag-text-secondary hover:text-ag-text transition px-2 py-1 rounded-lg hover:bg-[var(--border-subtle)]"
            aria-label="Sign out"
          >
            Sign out
          </button>
        </div>
      </div>

      {/* Mobile nav */}
      <div className="md:hidden flex gap-1 px-4 pb-2 overflow-x-auto scrollbar-none">
        {[
          { href: "/dashboard", label: "Dashboard" },
          { href: "/match/new", label: "New Analysis" },
          { href: "/dashboard/resumes", label: "Resumes" },
          { href: "/dashboard/matches", label: "History" },
        ].map((link) => {
          const active = pathname === link.href;
          return (
            <Link
              key={link.href}
              href={link.href}
              className={`whitespace-nowrap px-3 py-1.5 rounded-lg text-xs flex-shrink-0 transition-all duration-200 ${
                active
                  ? "bg-ag-accent/10 text-ag-accent font-medium"
                  : "text-ag-text-secondary hover:text-ag-text"
              }`}
            >
              {link.label}
            </Link>
          );
        })}
      </div>
    </nav>
  );
}