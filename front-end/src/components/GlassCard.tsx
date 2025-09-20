import React from "react";



type GlassCardProps = {
  className?: string;
  children?: React.ReactNode;
};

export default function GlassCard({ className = "", children }: GlassCardProps) {
  return (
    <div
      className={[
        "relative rounded-xl p-[1px]",
        "bg-radial from-slate-950 to-black/30 from-5%",
        className,
      ].join(" ")}
    >
      <div
        className={[
          "relative h-full w-full rounded-xl bg-clip-padding",
          "bg-white/4 backdrop-blur-xl backdrop-saturate-90",
          "inset-shadow-sm inset-shadow-slate-500/50 shadow-sm shadow-slate-600",

        ].join(" ")}
      >
        <div
          className={[
            "pointer-events-none absolute inset-0 rounded-md",
            "before:content-[''] before:absolute before:inset-x-10 before:top-6",
            "before:h-16 before:rounded-md before:bg-white/15 before:blur-xl before:opacity-15",
          ].join(" ")}
        />

        {/*content slot */}
        <div className="relative z-10 h-full w-full text-white/90">
          {children}
        </div>
      </div>
    </div>
  );
}
