import React from "react";



type GlassCardProps = {
  className?: string;
  children?: React.ReactNode;
};

export default function GlassCard({ className = "", children }: GlassCardProps) {
  return (
    <div
      className={[
        "relative rounded-3xl p-[1px]",
        "bg-radial from-black/10 to-gray/10",
        className,
      ].join(" ")}
    >
      <div
        className={[
          "relative h-full w-full rounded-[calc(1.5rem-1px)] bg-clip-padding",
          "bg-white/5 backdrop-blur-xl backdrop-saturate-150",
          "ring-1 ring-white/35 shadow-xl shadow-black/20",
        ].join(" ")}
      >
        <div
          className={[
            "pointer-events-none absolute inset-0 rounded-[inherit]",
            "before:content-[''] before:absolute before:inset-x-10 before:top-6",
            "before:h-16 before:rounded-2xl before:bg-white/15 before:blur-xl before:opacity-15",
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
