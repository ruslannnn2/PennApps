import React from "react";

export type ArticleCardProps = {
  title?: string | null;
  source?: string | null;
  summary?: string | null;
};

const ArticleCard: React.FC<ArticleCardProps> = ({ title, source, summary }) => {
  return (
    <div className="w-full rounded-xl shadow-md shadow-slate-600 bg-black/20 p-4 text-white/90">
      <h3 className="text-lg font-semibold mb-1">{title ?? "Untitled Article"}</h3>
      {source ? (
        <div className="text-xs text-blue-400 mb-3">Source: {source}</div>
      ) : (
        <div className="text-xs text-gray mb-3">Source: Unknown</div>
      )}
      <p className="text-sm leading-relaxed whitespace-pre-line text-white/60">
        {summary ?? "No summary available."}
      </p>
    </div>
  );
};

export default ArticleCard;
