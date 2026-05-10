"use client";

export default function FloatingOrbs() {
  return (
    <div aria-hidden="true" className="pointer-events-none fixed inset-0 z-0 overflow-hidden">
      {/* Large indigo orb — top-left */}
      <div
        className="animate-float absolute rounded-full"
        style={{
          width: "600px",
          height: "600px",
          top: "-10%",
          left: "-5%",
          background: "radial-gradient(circle, rgba(108,99,255,0.15) 0%, transparent 70%)",
          filter: "blur(80px)",
        }}
      />

      {/* Cyan orb — center-right */}
      <div
        className="animate-float-slow absolute rounded-full"
        style={{
          width: "400px",
          height: "400px",
          top: "30%",
          right: "-5%",
          background: "radial-gradient(circle, rgba(0,212,255,0.10) 0%, transparent 70%)",
          filter: "blur(60px)",
        }}
      />

      {/* Small indigo orb — bottom-right */}
      <div
        className="animate-float-slower absolute rounded-full"
        style={{
          width: "350px",
          height: "350px",
          bottom: "-5%",
          right: "15%",
          background: "radial-gradient(circle, rgba(108,99,255,0.08) 0%, transparent 70%)",
          filter: "blur(60px)",
        }}
      />
    </div>
  );
}
