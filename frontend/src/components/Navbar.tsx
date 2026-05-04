"use client";

import Link from "next/link";
import { useRouter, usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import { clearTokens, getAccessToken } from "@/lib/api";
import api from "@/lib/api";

const NAV_LINKS = [
  {
    href: "/dashboard",
    label: "Dashboard",
    icon: (
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/>
        <rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/>
      </svg>
    ),
  },
  {
    href: "/match/new",
    label: "New Analysis",
    icon: (
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
      </svg>
    ),
  },
  {
    href: "/dashboard/resumes",
    label: "Resumes",
    icon: (
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
        <polyline points="14 2 14 8 20 8"/>
      </svg>
    ),
  },
  {
    href: "/dashboard/matches",
    label: "History",
    icon: (
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>
      </svg>
    ),
  },
];

export default function Navbar() {
  const router = useRouter();
  const pathname = usePathname();
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [initials, setInitials] = useState("U");

  useEffect(() => {
    const token = getAccessToken();
    setIsLoggedIn(!!token);
  }, [pathname]);

  const hideOn = ["/", "/login", "/register"];
  if (hideOn.includes(pathname ?? "")) return null;
  if (!isLoggedIn) return null;

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

  return (
    <nav className="sticky top-0 z-50 bg-background border-b border-border/50 backdrop-blur-md">
      <div className="max-w-6xl mx-auto px-6 h-14 flex items-center justify-between gap-4">

        {/* Logo */}
        <Link href="/dashboard" className="flex items-center gap-2.5 flex-shrink-0 group">
          <div className="w-[30px] h-[30px] rounded-lg bg-blue-600 flex items-center justify-center text-white font-medium text-[13px] tracking-tight flex-shrink-0">
            IQ
          </div>
          <span className="font-medium text-[14px] text-foreground tracking-tight">
            ResumeIQ
          </span>
          <span className="text-[10px] font-medium text-blue-600 bg-blue-50 dark:bg-blue-950/60 dark:text-blue-400 rounded px-1.5 py-0.5 tracking-wide">
            BETA
          </span>
        </Link>

        {/* Nav links — desktop */}
        <div className="hidden md:flex items-center gap-0.5 flex-1 justify-center">
          {NAV_LINKS.map((link) => {
            const active = pathname === link.href;
            return (
              <Link
                key={link.href}
                href={link.href}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-[13px] transition-all duration-150 whitespace-nowrap ${
                  active
                    ? "bg-blue-50 dark:bg-blue-950/60 text-blue-600 dark:text-blue-400 font-medium"
                    : "text-muted-foreground hover:text-foreground hover:bg-muted/60"
                }`}
              >
                <span className={active ? "opacity-100" : "opacity-60"}>
                  {link.icon}
                </span>
                {link.label}
              </Link>
            );
          })}
        </div>

        {/* Right side */}
        <div className="flex items-center gap-2 flex-shrink-0">
          {/* Avatar */}
          <div className="w-[30px] h-[30px] rounded-full bg-blue-50 dark:bg-blue-950/60 border border-blue-200 dark:border-blue-800 flex items-center justify-center text-[12px] font-medium text-blue-600 dark:text-blue-400 flex-shrink-0">
            {initials}
          </div>

          {/* Divider */}
          <div className="w-px h-5 bg-border/60" />

          {/* Logout */}
          <button
            onClick={handleLogout}
            className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-[13px] text-muted-foreground hover:text-foreground hover:bg-muted/60 transition-all duration-150"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
              <polyline points="16 17 21 12 16 7"/>
              <line x1="21" y1="12" x2="9" y2="12"/>
            </svg>
            Sign out
          </button>
        </div>
      </div>

      {/* Mobile nav */}
      <div className="md:hidden flex gap-1 px-4 pb-2 overflow-x-auto scrollbar-none">
        {NAV_LINKS.map((link) => {
          const active = pathname === link.href;
          return (
            <Link
              key={link.href}
              href={link.href}
              className={`flex items-center gap-1.5 whitespace-nowrap px-3 py-1.5 rounded-lg text-xs flex-shrink-0 transition-all duration-150 ${
                active
                  ? "bg-blue-50 dark:bg-blue-950/60 text-blue-600 dark:text-blue-400 font-medium"
                  : "text-muted-foreground hover:text-foreground"
              }`}
            >
              <span className={active ? "opacity-100" : "opacity-60"}>
                {link.icon}
              </span>
              {link.label}
            </Link>
          );
        })}
      </div>
    </nav>
  );
}