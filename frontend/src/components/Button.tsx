import { ButtonHTMLAttributes, ReactNode } from "react";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "ghost" | "danger";
  size?: "sm" | "md" | "lg";
  children: ReactNode;
}

const variants = {
  primary:
    "bg-gradient-to-r from-[#6C63FF] to-[#00D4FF] text-white shadow-glow hover:shadow-glow-lg hover:brightness-110",
  ghost:
    "bg-transparent border border-[var(--border-color)] text-[var(--text-primary)] hover:bg-[var(--border-subtle)] hover:border-[var(--glass-hover-border)]",
  danger:
    "bg-[#FF4D6D] text-white hover:bg-[#FF4D6D]/90",
};

const sizes = {
  sm: "px-4 py-1.5 text-sm rounded-lg",
  md: "px-6 py-2.5 text-sm rounded-xl",
  lg: "px-8 py-3.5 text-base rounded-xl font-semibold",
};

export default function Button({
  variant = "primary",
  size = "md",
  children,
  className = "",
  disabled,
  ...props
}: ButtonProps) {
  return (
    <button
      className={`inline-flex items-center justify-center gap-2 font-medium transition-all duration-300 cursor-pointer
        ${variants[variant]}
        ${sizes[size]}
        ${disabled ? "opacity-40 cursor-not-allowed pointer-events-none" : ""}
        ${className}
      `}
      disabled={disabled}
      {...props}
    >
      {children}
    </button>
  );
}
