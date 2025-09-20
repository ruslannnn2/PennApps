// src/components/NetworkStats.tsx
import React from 'react';
import { GraphData } from './ForceGraph';

interface NetworkStatsProps {
  data: GraphData | null;
  title?: string;
}

const NetworkStats: React.FC<NetworkStatsProps> = ({ 
  data, 
  title = "📊 Network Summary" 
}) => {
  if (!data) {
    return (
      <section className="network-stats">
        <h2>{title}</h2>
        <p>No data available</p>
      </section>
    );
  }

  const nodeCount = data.nodes.length;
  const linkCount = data.links.length;
  const groupCount = [...new Set(data.nodes.map(n => n.group))].length;
  
  // Calculate network density
  const maxPossibleLinks = nodeCount * (nodeCount - 1) / 2;
  const density = ((linkCount / maxPossibleLinks) * 100).toFixed(1);

  // Find most connected node
  const linkCounts = data.nodes.map(node => {
    const connections = data.links.filter(link => 
      link.source === node.id || link.target === node.id
    ).length;
    return { node: node.id, connections };
  });
  const mostConnected = linkCounts.reduce((prev, current) => 
    prev.connections > current.connections ? prev : current
  );

  return (
    <section className="network-stats">
      <h2>{title}</h2>
      <div className="stats-grid">
        <div className="stat-item">
          <span className="stat-number">{nodeCount}</span>
          <span className="stat-label">Nodes</span>
        </div>
        <div className="stat-item">
          <span className="stat-number">{linkCount}</span>
          <span className="stat-label">Connections</span>
        </div>
        <div className="stat-item">
          <span className="stat-number">{groupCount}</span>
          <span className="stat-label">Categories</span>
        </div>
        <div className="stat-item">
          <span className="stat-number">{density}%</span>
          <span className="stat-label">Density</span>
        </div>
      </div>
      <div className="additional-stats">
        <p><strong>Most Connected:</strong> {mostConnected.node} ({mostConnected.connections} connections)</p>
      </div>
    </section>
  );
};

export default NetworkStats;