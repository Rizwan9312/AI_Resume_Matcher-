import { ReactNode } from "react";

interface GlassCardProps {
  children?: ReactNode;
  className?: string;
  hover?: boolean;
}

export default function GlassCard({
  children,
  className = "",
  hover = true,
}: GlassCardProps) {
  return (
    <div
      className={`glass-card rounded-2xl ${hover ? "" : "no-lift"} ${className}`}
    >
      {children}
    </div>
  );
}
