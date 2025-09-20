import * as React from "react";

type ButtonProps = React.ButtonHTMLAttributes<HTMLButtonElement> & {
  className?: string;
};

export default function Button({ className = "", children, ...props }: ButtonProps) {
  return (
    <button
      className={[
        "inline-flex items-center text-left gap-2 rounded-xl px-4 py-2 text-md",
        "bg-black/10 backdrop-blur-lg backdrop-saturate-150",
        " border-white/20 shadow hover:bg-slate-800 active:bg-white/20 transition-all duration-300 hover:translate-x-2",
        "hover:shadow-xs active:shadow-slate-500 shadow-slate-600",
        className,
      ].join(" ")}
      {...props}
    >
      {children}
    </button>
  );
}