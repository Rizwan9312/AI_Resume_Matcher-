import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        /* Variable-driven tokens — auto-adapt to light/dark */
        bg: "var(--background)",
        surface: "var(--surface)",
        "surface-2": "var(--surface-2)",
        "ag-accent": "var(--accent-primary)",
        "ag-cyan": "var(--accent-cyan)",
        "ag-success": "var(--color-success)",
        "ag-warning": "var(--color-warning)",
        "ag-danger": "var(--color-danger)",
        "ag-text": "var(--text-primary)",
        "ag-text-secondary": "var(--text-secondary)",
        "ag-text-muted": "var(--text-muted)",
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
