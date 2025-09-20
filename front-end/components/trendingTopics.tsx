// src/components/TrendingTopics.tsx
import React from 'react';

interface TrendingTopicsProps {
  topics: string[];
  title?: string;
  onTopicClick?: (topic: string) => void;
}

const TrendingTopics: React.FC<TrendingTopicsProps> = ({ 
  topics, 
  title = "🔥 Trending Topics",
  onTopicClick 
}) => {
  return (
    <section className="trending-section">
      <h2>{title}</h2>
      <div className="trending-topics">
        {topics.map((topic: string, index: number) => (
          <span 
            key={index} 
            className={`topic-tag ${onTopicClick ? 'clickable' : ''}`}
            onClick={() => onTopicClick && onTopicClick(topic)}
          >
            {topic}
          </span>
        ))}
      </div>
    </section>
  );
};

export default TrendingTopics;