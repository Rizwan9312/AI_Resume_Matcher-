import type { Metadata } from "next";
import { Syne, DM_Sans } from "next/font/google";
import "./globals.css";
import Navbar from "@/components/Navbar";

const syne = Syne({
  subsets: ["latin"],
  weight: ["400", "700", "800"],
  variable: "--font-syne",
  display: "swap",
});

const dmSans = DM_Sans({
  subsets: ["latin"],
  weight: ["400", "500"],
  variable: "--font-dm-sans",
  display: "swap",
});

export const metadata: Metadata = {
  title: "ResumeIQ — AI Resume Matcher",
  description:
    "AI-powered resume intelligence platform that scores, rewrites, and optimizes resumes against job descriptions.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`dark ${syne.variable} ${dmSans.variable}`}>
      <body className="min-h-screen font-sans">
        <Navbar />
        <main>{children}</main>
      </body>
    </html>
  );
}