import * as React from "react";

type ButtonProps = React.ButtonHTMLAttributes<HTMLButtonElement> & {
  className?: string;
};

export default function Button({ className = "", children, ...props }: ButtonProps) {
  return (
    <button
      className={[
        "inline-flex items-center text-left gap-2 rounded-xl px-4 py-2 text-sm",
        "text-white bg-black/10 backdrop-blur-lg backdrop-saturate-150",
        " border-white/20 shadow hover:bg-slate-800 active:bg-white/20 transition-all duration-300 hover:translate-x-0.5",
        "hover:shadow-xs active:shadow-none shadow-slate-900",
        "focus:outline-none focus:ring-2 focus:ring-white/30 focus:ring-offset-2 focus:ring-offset-black/20 ",

        "disabled:opacity-50 disabled:pointer-events-none",
        className,
      ].join(" ")}
      {...props}
    >
      {children}
    </button>
  );
}