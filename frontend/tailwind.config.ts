import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        /* Legacy HSL-based tokens (kept for compatibility) */
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        card: "hsl(var(--card))",
        "card-foreground": "hsl(var(--card-foreground))",
        primary: "hsl(var(--primary))",
        "primary-foreground": "hsl(var(--primary-foreground))",
        secondary: "hsl(var(--secondary))",
        muted: "hsl(var(--muted))",
        "muted-foreground": "hsl(var(--muted-foreground))",
        accent: "hsl(var(--accent))",
        destructive: "hsl(var(--destructive))",
        border: "hsl(var(--border))",
        ring: "hsl(var(--ring))",

        /* Antigravity design tokens */
        bg: "#050508",
        surface: "#0D0D14",
        "surface-2": "#13131E",
        "ag-accent": "#6C63FF",
        "ag-cyan": "#00D4FF",
        "ag-success": "#00FF88",
        "ag-warning": "#FFB800",
        "ag-danger": "#FF4D6D",
        "ag-text": "#F0F0FF",
        "ag-text-secondary": "#8888AA",
        "ag-text-muted": "#444466",
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      fontFamily: {
        sans: ["var(--font-dm-sans)", "Inter", "system-ui", "sans-serif"],
        syne: ["var(--font-syne)", "sans-serif"],
        "dm-sans": ["var(--font-dm-sans)", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"],
      },
      boxShadow: {
        glow: "0 0 20px rgba(108,99,255,0.4)",
        "glow-lg": "0 0 40px rgba(108,99,255,0.3)",
        "glow-cyan": "0 0 20px rgba(0,212,255,0.3)",
        "glow-success": "0 0 20px rgba(0,255,136,0.3)",
      },
      animation: {
        float: "float 6s ease-in-out infinite",
        "float-slow": "float 8s ease-in-out infinite",
        "float-slower": "float 10s ease-in-out infinite",
      },
    },
  },
  plugins: [],
};

export default config;
