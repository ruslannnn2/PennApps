import React from "react";

export type ArticleCardProps = {
  title?: string | null;
  source?: string | null;
  className?: string;
};

const CarouselCard: React.FC<ArticleCardProps> = ({ title, source, className }) => {
  return (
    <div
      className={[
        "rounded-xl bg-black/20 text-white/90",
        "px-4 py-3 shadow-md shadow-slate-600",
        "flex flex-col min-w-[240px] max-w-[360px]",
        " hover:bg-slate-800 hover:translate-y-[-5px] hover:shadow-slate-500 transition-all duration-300",
        className ?? "",
      ].join(" ")}
    >
      <h3 className="text-base font-semibold mb-1 line-clamp-2">
        {title ?? "Untitled Article"}
      </h3>
      <div className="text-xs text-blue-300 truncate">
        Source: {source ?? "Unknown"}
      </div>
    </div>
  );
};

export default CarouselCard;