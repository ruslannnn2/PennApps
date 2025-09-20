import React from "react";
import ArticleCard, { type ArticleCardProps } from "./ArticleCard";

export type ClusterCardProps = {
  title?: string | null;
  summary?: string | null;
  articles?: Array<ArticleCardProps & { id?: number | string }>; // minimally needs title/source/summary
};

const ClusterCard: React.FC<ClusterCardProps> = ({ title, summary, articles = [] }) => {
  return (
    <div className="w-full space-y-4">
      <div className="rounded-xl border border-white/15 bg-black/20 p-4 text-blue-400">
        <h2 className="text-xl font-semibold mb-1">{title ?? "Untitled Cluster"}</h2>
        <p className="text-sm leading-relaxed text-white/90 whitespace-pre-line">
          {summary ?? "No summary available for this cluster."}
        </p>
      </div>

      {articles.length > 0 ? (
        <div className="space-y-3">
          {articles.map((a, idx) => (
            <ArticleCard key={a.id ?? idx} title={a.title} source={a.source} summary={a.summary} />
          ))}
        </div>
      ) : (
        <div className="text-white/60 text-sm italic">No articles found for this cluster.</div>
      )}
    </div>
  );
};

export default ClusterCard;
