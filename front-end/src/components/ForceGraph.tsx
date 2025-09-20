import React, { useEffect, useRef, useState } from "react";
import * as d3 from "d3";

export type NodeDatum = d3.SimulationNodeDatum & {
  id: string;
  group?: string | number;
  [key: string]: any;
};

export type LinkDatum = d3.SimulationLinkDatum<NodeDatum> & {
  source: string | NodeDatum;
  target: string | NodeDatum;
  value?: number;
  [key: string]: any;
};

type ForceGraphProps = {
  nodes: NodeDatum[];
  links: LinkDatum[];
  width?: number;
  height?: number;
  showLabels?: boolean;
  zoom?: boolean;
  nodeRadius?: number | ((d: NodeDatum) => number);
  // When true (default), node radius scales with degree (number of connections)
  sizeByDegree?: boolean;
  minRadius?: number; // min radius when sizing by degree
  maxRadius?: number; // max radius when sizing by degree
  // Fill parent container by observing its size
  fitParent?: boolean;
  nodeFill?: (d: NodeDatum) => string;
  linkStroke?: string;
  chargeStrength?: number;
  linkOpacity?: number;
  onNodeClick?: (d: NodeDatum) => void;
};


function computeComponents(nodes: NodeDatum[], links: LinkDatum[]) {
  const adj: Record<string, string[]> = {};
  nodes.forEach((n) => (adj[n.id] = []));
  links.forEach((l) => {
    const src = typeof l.source === "string" ? l.source : l.source.id;
    const tgt = typeof l.target === "string" ? l.target : l.target.id;
    adj[src].push(tgt);
    adj[tgt].push(src);
  });

  let compId = 0;
  const visited = new Set<string>();
  nodes.forEach((n) => {
    if (!visited.has(n.id)) {
      compId++;
      const stack = [n.id];
      while (stack.length) {
        const cur = stack.pop()!;
        if (visited.has(cur)) continue;
        visited.add(cur);
        const node = nodes.find((d) => d.id === cur);
        if (node) node.group = compId;
        adj[cur].forEach((nbr) => {
          if (!visited.has(nbr)) stack.push(nbr);
        });
      }
    }
  });

  return nodes;
}

const ForceGraph: React.FC<ForceGraphProps> = ({
  nodes,
  links,
  width = 900,
  height = 600,
  showLabels = false,
  zoom = true,
  nodeRadius = 6,
  sizeByDegree = true,
  minRadius = 3,
  maxRadius = 14,
  fitParent = true,
  chargeStrength = -30,
  nodeFill,
  linkStroke = "#FFF",
  linkOpacity = 1,
  onNodeClick,
}) => {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const [size, setSize] = useState<{ w: number; h: number }>({ w: width, h: height });

  useEffect(() => {
    if (fitParent && containerRef.current) {
      const el = containerRef.current;
      const ro = new ResizeObserver((entries) => {
        for (const e of entries) {
          const { width: w, height: h } = e.contentRect;
          // Avoid zero-size which can happen during layout
          setSize({ w: Math.max(10, Math.floor(w)), h: Math.max(10, Math.floor(h)) });
        }
      });
      ro.observe(el);
      return () => ro.disconnect();
    }
  }, [fitParent]);

  useEffect(() => {
    if (!containerRef.current) return;

    // Defensive copies (D3 mutates nodes/links with x,y,vx,vy)
    const N = computeComponents(nodes.map((d) => ({ ...d })), links);
    const L = links.map((d) => ({ ...d }));

    // Compute degree (number of connections) per node id
    const degree = new Map<string, number>();
    for (const l of L) {
      const s = typeof l.source === "string" ? l.source : String((l.source as NodeDatum).id);
      const t = typeof l.target === "string" ? l.target : String((l.target as NodeDatum).id);
      degree.set(s, (degree.get(s) ?? 0) + 1);
      degree.set(t, (degree.get(t) ?? 0) + 1);
    }
    const maxDeg = N.reduce((m, n) => Math.max(m, degree.get(String(n.id)) ?? 0), 0);
    const degScale = d3
      .scaleLinear()
      .domain([0, Math.max(1, maxDeg)])
      .range([minRadius, maxRadius]);

    const color = d3.scaleOrdinal(d3.schemeDark2);

    // Final radius function: prefer user function, else scale by degree (if enabled), else constant
    const r =
      typeof nodeRadius === "function"
        ? nodeRadius
        : (d: NodeDatum) => (sizeByDegree ? degScale(degree.get(String(d.id)) ?? 0) : (nodeRadius as number));

    // Root SVG
    const W = fitParent ? size.w : width;
    const H = fitParent ? size.h : height;
    if (!W || !H) return;

    const svg = d3
      .select(containerRef.current)
      .append("svg")
      .attr("width", "100%")
      .attr("height", "100%")
      // Centered coordinate system like the Observable disjoint example
      .attr("viewBox", `${-W / 2} ${-H / 2} ${W} ${H}`)
      .attr("preserveAspectRatio", "xMidYMid meet")
      .attr("style", "display:block; width:100%; height:100%; background: transparent;");

    // Zoomable group
    const g = svg.append("g");
    
    const zoomBehavior = d3
      .zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.1, 8])
      .on("zoom", (event) => g.attr("transform", event.transform.toString()));

    svg.call(zoomBehavior);

   
    const k = 1.5;        //zoom scale
    const tx = 0, ty = 0;  // set the x, y of initial viewport
    svg.call(zoomBehavior.transform, d3.zoomIdentity.translate(tx, ty).scale(k));

    //links
    const link = g
      .append("g")
      .attr("stroke", linkStroke)
      .attr("stroke-opacity", linkOpacity)
      .selectAll("line")
      .data(L)
      .join("line")
      .attr("stroke-width", (d) => Math.sqrt(d.value ?? 1));

    //nodes
    const node = g
      .append("g")
      .attr("stroke", "")
      .attr("stroke-width", 0.5)
      .selectAll("circle")
      .data(N)
      .join("circle")
      .on("click", (_, d) => onNodeClick?.(d)) // click hook
      .style("cursor", "pointer")
  .attr("r", (d) => r(d))
  .attr("fill", (d) => color(String(d.group!)));

    (node as d3.Selection<SVGCircleElement, NodeDatum, SVGGElement, unknown>)
      .call(
        d3
          .drag<SVGCircleElement, NodeDatum>()
          .on("start", (event, d) => {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
          })
          .on("drag", (event, d) => {
            d.fx = event.x;
            d.fy = event.y;
          })
          .on("end", (event, d) => {
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
          })
  );

    // Labels (optional)
    const label = showLabels
      ? g
          .append("g")
          .attr("font-family", "ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial")
          .attr("font-size", 12)
          .attr("fill", "#ddd")
          .attr("pointer-events", "none")
          .selectAll("text")
          .data(N)
          .join("text")
          .text((d) => String(d.id))
      : null;

    // Simulation
    const simulation = d3
    .forceSimulation(N)
      .force("link", d3.forceLink<NodeDatum, LinkDatum>(L).id((d) => d.id))
    .force("charge", d3.forceManyBody().strength(chargeStrength))
    // Disjoint behavior: light centering toward (0,0) due to centered viewBox
    .force("x", d3.forceX())
    .force("y", d3.forceY());

        simulation.on("tick", () => {
        link
            .attr("x1", (d) => (typeof d.source === "object" ? d.source.x ?? 0 : 0))
            .attr("y1", (d) => (typeof d.source === "object" ? d.source.y ?? 0 : 0))
            .attr("x2", (d) => (typeof d.target === "object" ? d.target.x ?? 0 : 0))
            .attr("y2", (d) => (typeof d.target === "object" ? d.target.y ?? 0 : 0));

        node
          .attr("cx", (d) => d.x ?? 0)
          .attr("cy", (d) => d.y ?? 0);

        if (label) {
            label
              .attr("x", (d) => (d.x ?? 0) + r(d) + 4)
              .attr("y", (d) => d.y ?? 0);
        }
        });

    // Cleanup
    return () => {
      simulation.stop();
      svg.remove();
    };
  }, [nodes, links, width, height, showLabels, zoom, nodeRadius, nodeFill, linkStroke, linkOpacity, onNodeClick, chargeStrength, sizeByDegree, minRadius, maxRadius, fitParent, size.w, size.h]);

  return <div ref={containerRef} className="w-full h-full" />;
};

export default ForceGraph;