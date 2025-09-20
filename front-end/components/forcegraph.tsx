// src/components/ForceGraph.tsx
import { useEffect, useRef } from 'react';
import * as d3 from 'd3';

export interface GraphNode {
  id: string;
  group: number;
  x?: number;
  y?: number;
  fx?: number | null;
  fy?: number | null;
}

export interface GraphLink {
  source: string | GraphNode;
  target: string | GraphNode;
  value: number;
}

export interface GraphData {
  nodes: GraphNode[];
  links: GraphLink[];
}

interface ForceGraphProps {
  data: GraphData;
  width?: number;
  height?: number;
}

const ForceGraph: React.FC<ForceGraphProps> = ({ 
  data, 
  width = 928, 
  height = 600 
}) => {
  const chartRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (data && chartRef.current) {
      createForceChart(data);
    }
  }, [data, width, height]);

  const createForceChart = (data: GraphData): void => {
    if (!chartRef.current) return;

    // Clear previous chart
    d3.select(chartRef.current).selectAll("*").remove();

    // Specify the color scale
    const color = d3.scaleOrdinal(d3.schemeCategory10);

    // The force simulation mutates links and nodes, so create a copy
    const links = data.links.map(d => ({...d}));
    const nodes = data.nodes.map(d => ({...d}));

    // Create a simulation with several forces
    const simulation = d3.forceSimulation(nodes)
        .force("link", d3.forceLink(links).id((d: any) => d.id))
        .force("charge", d3.forceManyBody())
        .force("center", d3.forceCenter(width / 2, height / 2))
        .on("tick", ticked);

    // Create the SVG container
    const svg = d3.select(chartRef.current)
        .append("svg")
        .attr("width", width)
        .attr("height", height)
        .attr("viewBox", [0, 0, width, height])
        .attr("style", "max-width: 100%; height: auto;");

    // Add a line for each link
    const link = svg.append("g")
        .attr("stroke", "#999")
        .attr("stroke-opacity", 0.6)
      .selectAll("line")
      .data(links)
      .join("line")
        .attr("stroke-width", (d: any) => Math.sqrt(d.value));

    // Add a circle for each node
    const node = svg.append("g")
        .attr("stroke", "#fff")
        .attr("stroke-width", 1.5)
      .selectAll("circle")
      .data(nodes)
      .join("circle")
        .attr("r", 5)
        .attr("fill", (d: any) => color(d.group));

    // Add tooltips (hover text)
    node.append("title")
        .text((d: any) => d.id);

    // Add visible text labels
    const labels = svg.append("g")
        .selectAll("text")
        .data(nodes)
        .join("text")
        .attr("text-anchor", "middle")
        .attr("dy", "0.35em")
        .style("font-size", "12px")
        .style("font-family", "Arial, sans-serif")
        .style("fill", "#333")
        .style("pointer-events", "none")
        .text((d: any) => d.id);

    // Add a drag behavior
    node.call(d3.drag<SVGCircleElement, any>()
          .on("start", dragstarted)
          .on("drag", dragged)
          .on("end", dragended));

    // Set the position attributes of links and nodes each time the simulation ticks
    function ticked() {
      link
          .attr("x1", (d: any) => d.source.x)
          .attr("y1", (d: any) => d.source.y)
          .attr("x2", (d: any) => d.target.x)
          .attr("y2", (d: any) => d.target.y);

      node
          .attr("cx", (d: any) => d.x)
          .attr("cy", (d: any) => d.y);

      // Update label positions
      labels
          .attr("x", (d: any) => d.x)
          .attr("y", (d: any) => d.y);
    }

    // Reheat the simulation when drag starts, and fix the subject position
    function dragstarted(event: any) {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      event.subject.fx = event.subject.x;
      event.subject.fy = event.subject.y;
    }

    // Update the subject (dragged node) position during drag
    function dragged(event: any) {
      event.subject.fx = event.x;
      event.subject.fy = event.y;
    }

    // Restore the target alpha so the simulation cools after dragging ends
    function dragended(event: any) {
      if (!event.active) simulation.alphaTarget(0);
      event.subject.fx = null;
      event.subject.fy = null;
    }
  };

  return (
    <div 
      ref={chartRef} 
      className="force-graph-container"
      style={{ 
        border: '1px solid #ddd', 
        borderRadius: '8px', 
        background: '#f9f9f9',
        display: 'flex',
        justifyContent: 'center',
        padding: '20px'
      }}
    />
  );
};

export default ForceGraph;