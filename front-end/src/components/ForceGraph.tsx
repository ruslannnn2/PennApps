import React, { useEffect, useRef, useState } from "react";
import * as d3 from "d3";

export type NodeDatum = d3.SimulationNodeDatum & {
  id: string;
  article_summary?: string;
  cluster_id?: number;
  text?: string;
  title?: string;
  article_id?: number;
  source?: string;
  // component id assigned by computeComponents
  group?: number;
  // app-level classification for rendering
  type?: "cluster" | "article" | string;
};

export type LinkDatum = d3.SimulationLinkDatum<NodeDatum> & {
  source: string | NodeDatum;
  target: string | NodeDatum;
  value?: number;
};

type ForceGraphProps = {
  nodes: NodeDatum[];
  links: LinkDatum[];
  width?: number;
  height?: number;
  showLabels?: boolean;
  zoom?: boolean;
  nodeRadius?: number | ((d: NodeDatum) => number);
  //when true (default), node radius scales with degree (number of connections)
  sizeByDegree?: boolean;
  minRadius?: number; // min radius when sizing by degree
  maxRadius?: number; // max radius when sizing by degree
  //fill parent container by observing its size
  fitParent?: boolean;
  nodeFill?: (d: NodeDatum) => string;
  nodeStroke?: (d: NodeDatum) => string | null | undefined;
  nodeStrokeWidth?: (d: NodeDatum) => number | null | undefined;
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
  nodeStroke,
  nodeStrokeWidth,
  linkStroke = "#FFF",
  linkOpacity = 1,
  onNodeClick,
}) => {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const [size, setSize] = useState<{ w: number; h: number }>({ w: width, h: height });
  // persistent refs for selections and simulation
  const nodeSelRef = useRef<d3.Selection<SVGCircleElement, NodeDatum, SVGGElement, unknown> | null>(null);
  const linkSelRef = useRef<d3.Selection<SVGLineElement, LinkDatum, SVGGElement, unknown> | null>(null);
  const labelSelRef = useRef<d3.Selection<SVGTextElement, NodeDatum, SVGGElement, unknown> | null>(null);
  const simulationRef = useRef<d3.Simulation<NodeDatum, LinkDatum> | null>(null);
  const degreeMapRef = useRef<Map<string, number>>(new Map());
  const degScaleRef = useRef<d3.ScaleLinear<number, number>>(d3.scaleLinear<number, number>().domain([0, 1]).range([minRadius, maxRadius]));
  const defaultColorRef = useRef<d3.ScaleOrdinal<string, string>>(d3.scaleOrdinal(d3.schemeDark2));
  const onNodeClickRef = useRef<ForceGraphProps["onNodeClick"]>(onNodeClick);
  useEffect(() => { onNodeClickRef.current = onNodeClick; }, [onNodeClick]);

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

  // Mount/rebuild only when structural inputs change
  useEffect(() => {
    if (!containerRef.current) return;

    const N = computeComponents(nodes.map((d) => ({ ...d })), links);
    const L = links.map((d) => ({ ...d }));

    // degree + scale
    const degree = new Map<string, number>();
    for (const l of L) {
      const s = typeof l.source === "string" ? l.source : String((l.source as NodeDatum).id);
      const t = typeof l.target === "string" ? l.target : String((l.target as NodeDatum).id);
      degree.set(s, (degree.get(s) ?? 0) + 1);
      degree.set(t, (degree.get(t) ?? 0) + 1);
    }
    degreeMapRef.current = degree;
    const maxDeg = N.reduce((m, n) => Math.max(m, degree.get(String(n.id)) ?? 0), 0);
    degScaleRef.current = d3.scaleLinear<number, number>().domain([0, Math.max(1, maxDeg)]).range([minRadius, maxRadius]);

    const W = fitParent ? size.w : width;
    const H = fitParent ? size.h : height;
    if (!W || !H) return;

    const svg = d3
      .select(containerRef.current)
      .append("svg")
      .attr("width", "100%")
      .attr("height", "100%")
      .attr("viewBox", `${-W / 2} ${-H / 2} ${W} ${H}`)
      .attr("preserveAspectRatio", "xMidYMid meet")
      .attr("style", "display:block; width:100%; height:100%; background: transparent;");

    const g = svg.append("g");

    const zoomBehavior = d3
      .zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.1, 8])
      .on("zoom", (event) => g.attr("transform", event.transform.toString()));

    if (zoom) svg.call(zoomBehavior);
    svg.call(zoomBehavior.transform, d3.zoomIdentity.translate(0, 0).scale(1));

    const link = g
      .append("g")
      .attr("stroke", linkStroke)
      .attr("stroke-opacity", linkOpacity)
      .selectAll("line")
      .data(L)
      .join("line")
      .attr("stroke-width", (d) => Math.sqrt(d.value ?? 1));
    linkSelRef.current = link as d3.Selection<SVGLineElement, LinkDatum, SVGGElement, unknown>;

    const node = g
      .append("g")
      .selectAll("circle")
      .data(N)
      .join("circle")
      .on("click", (_, d) => onNodeClickRef.current?.(d))
      .style("cursor", "pointer");
    nodeSelRef.current = node as d3.Selection<SVGCircleElement, NodeDatum, SVGGElement, unknown>;

    // initial visual attrs
    const r =
      typeof nodeRadius === "function"
        ? nodeRadius
        : (d: NodeDatum) => (sizeByDegree ? degScaleRef.current(degreeMapRef.current.get(String(d.id)) ?? 0) : (nodeRadius as number));
    node
      .attr("r", (d) => r(d))
      .attr("fill", (d) => defaultColorRef.current(String(d.group!)))
      .attr("stroke", "")
      .attr("stroke-width", 0.5);

    (nodeSelRef.current as d3.Selection<SVGCircleElement, NodeDatum, SVGGElement, unknown>).call(
      d3
        .drag<SVGCircleElement, NodeDatum>()
        .on("start", (event, d) => {
          const sim = simulationRef.current!;
          if (!event.active) sim.alphaTarget(0.3).restart();
          d.fx = d.x;
          d.fy = d.y;
        })
        .on("drag", (event, d) => {
          d.fx = event.x;
          d.fy = event.y;
        })
        .on("end", (event, d) => {
          const sim = simulationRef.current!;
          if (!event.active) sim.alphaTarget(0);
          d.fx = null;
          d.fy = null;
        })
    );

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
    if (label) {
      labelSelRef.current = label as d3.Selection<SVGTextElement, NodeDatum, SVGGElement, unknown>;
    } else {
      labelSelRef.current = null;
    }

    const simulation = d3
      .forceSimulation(N)
      .force("link", d3.forceLink<NodeDatum, LinkDatum>(L).id((d) => d.id))
      .force("charge", d3.forceManyBody().strength(chargeStrength))
      .force("x", d3.forceX())
      .force("y", d3.forceY());

    simulation.on("tick", () => {
      link
        .attr("x1", (d) => (typeof d.source === "object" ? d.source.x ?? 0 : 0))
        .attr("y1", (d) => (typeof d.source === "object" ? d.source.y ?? 0 : 0))
        .attr("x2", (d) => (typeof d.target === "object" ? d.target.x ?? 0 : 0))
        .attr("y2", (d) => (typeof d.target === "object" ? d.target.y ?? 0 : 0));

      nodeSelRef.current!.attr("cx", (d) => d.x ?? 0).attr("cy", (d) => d.y ?? 0);

      if (labelSelRef.current) {
        const getR = (d: NodeDatum) =>
          typeof nodeRadius === "function"
            ? (nodeRadius as (d: NodeDatum) => number)(d)
            : sizeByDegree
            ? degScaleRef.current(degreeMapRef.current.get(String(d.id)) ?? 0)
            : (nodeRadius as number);
        labelSelRef.current
          .attr("x", (d) => (d.x ?? 0) + getR(d) + 4)
          .attr("y", (d) => d.y ?? 0);
      }
    });

    simulationRef.current = simulation;

    return () => {
      simulation.stop();
      svg.remove();
      simulationRef.current = null;
      nodeSelRef.current = null;
      linkSelRef.current = null;
      labelSelRef.current = null;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [nodes, links, width, height, showLabels, zoom, linkStroke, linkOpacity, chargeStrength, sizeByDegree, minRadius, maxRadius, fitParent, size.w, size.h]);

  // Lightweight updates: visual styling
  useEffect(() => {
    const node = nodeSelRef.current;
    if (!node) return;
    node
      .attr("fill", (d) => (nodeFill ? nodeFill(d) : defaultColorRef.current(String(d.group!))))
      .attr("stroke", (d) => nodeStroke?.(d) ?? "")
      .attr("stroke-width", (d) => ((nodeStrokeWidth?.(d) ?? 0.5) as number));
  }, [nodeFill, nodeStroke, nodeStrokeWidth]);

  // Lightweight updates: radius
  useEffect(() => {
    const node = nodeSelRef.current;
    if (!node) return;
    degScaleRef.current.range([minRadius, maxRadius]);
    const r =
      typeof nodeRadius === "function"
        ? nodeRadius
        : (d: NodeDatum) => (sizeByDegree ? degScaleRef.current(degreeMapRef.current.get(String(d.id)) ?? 0) : (nodeRadius as number));
    node.attr("r", (d) => r(d));
    if (labelSelRef.current) {
      const getR = (d: NodeDatum) =>
        typeof nodeRadius === "function"
          ? (nodeRadius as (d: NodeDatum) => number)(d)
          : sizeByDegree
          ? degScaleRef.current(degreeMapRef.current.get(String(d.id)) ?? 0)
          : (nodeRadius as number);
      labelSelRef.current.attr("x", (d) => (d.x ?? 0) + getR(d) + 4);
    }
  }, [nodeRadius, sizeByDegree, minRadius, maxRadius]);

  return <div ref={containerRef} className="w-full h-full" />;
};

export default ForceGraph;