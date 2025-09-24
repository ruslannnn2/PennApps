import { useEffect, useMemo, useState } from "react";
import * as d3 from "d3";
import GlassCard from "../components/GlassCard";
import ForceGraph, { type NodeDatum, type LinkDatum } from "../components/ForceGraph";
import Button from "../components/Button";
import logo from "../assets/logo.png";
import ArticleCard from "../components/ArticleCard";
import ClusterCard from "../components/ClusterCard";
import Carousel from "../components/Carousel";


type Cluster = { cluster_id: number; cluster_summary: string; cluster_title: string | null };
type Article = { article_id: number; article_summary?: string; cluster_id?: number; title?: string; text?: string; source?: string };

const API_BASE = "http://127.0.0.1:5000";

const Landing = () => {
    const [clusters, setClusters] = useState<Cluster[]>([]);
    const [articles, setArticles] = useState<Article[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
  const [focusedNode, setFocusedNode] = useState<NodeDatum | null>(null);
  const [selectedClusterId, setSelectedClusterId] = useState<number | null>(null);

    useEffect(() => {
      let cancelled = false;
      async function load() {
        try {
          setLoading(true);
          const [artRes, cluRes] = await Promise.all([
            fetch(`${API_BASE}/api/articles`),
            fetch(`${API_BASE}/api/clusters`),
          ]);

          const artJson = await artRes.json();
          const cluJson = await cluRes.json();
          if (cancelled) return;
          setArticles(artJson.articles ?? []);
          setClusters(cluJson.clusters ?? []);
        } catch (e: unknown) {
          const message = e instanceof Error ? e.message : "Failed to load data";
          if (!cancelled) setError(message);
        } finally {
          if (!cancelled) setLoading(false);
        }
      }
      load();
      return () => {
        cancelled = true;
      };
    }, []);

    // build nodes and its links
    const { nodes, links } = useMemo(() => {
      const n: NodeDatum[] = [];
      const l: LinkDatum[] = [];

      // map to find cluster info
      const clusterById = new Map<number, Cluster>();
      for (const c of clusters) clusterById.set(c.cluster_id, c);

      //create cluster nodes
      for (const c of clusters) {
        n.push({
          id: `cluster-${c.cluster_id}`,
          type: "cluster",
          cluster_id: c.cluster_id,
          title: c.cluster_title ?? undefined,
          article_summary: c.cluster_summary,
        });
      }

      //create article nodes and link to cluster node
      for (const a of articles) {
        const id = `article-${a.article_id}`;
        n.push({
          id,
          type: "article",
          article_id: a.article_id,
          article_summary: a.article_summary,
          cluster_id: a.cluster_id,
          title: a.title,
          text: a.text,
          source: a.source,
        });

        if (a.cluster_id != null && clusterById.has(a.cluster_id)) {
          l.push({
            source: id,
            target: `cluster-${a.cluster_id}`,
            value: 1,
          });
        }
      }

      return { nodes: n, links: l };
    }, [articles, clusters]);

    //prepare a color scale for clusters using schemeDark2, randomized assignment
    const clusterColor = useMemo(() => {
      const palette = d3.schemeDark2.slice();
      //shuffle palette for randomized assignment without repetition
      for (let i = palette.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [palette[i], palette[j]] = [palette[j], palette[i]];
      }
      const scale = d3.scaleOrdinal<number, string>(palette as string[]);
      return (cluster_id?: number) => (cluster_id == null ? "#999" : scale(cluster_id));
  }, []);

    return (
    <div className="bg-black min-h-screen flex items-center justify-center p-3">
      <div className="flex flex-col md:flex-row items-stretch md:items-stretch justify-center gap-4 w-full">
        {/*stretches to match middle card height */}
        <div className="w-[min(36vw,360px)]  h-[min(96vh,960px)] flex flex-col gap-4 min-h-0">
          {/*height evenly (both fill) */}
          <GlassCard className="flex-row min-h-0 items-center justify-center">
            <div className="flex items-center justify-center">
                <img src={logo} alt="logo" className="max-w-[50%] max-h-[50%] object-contain p-5"/>
            </div>
          </GlassCard>

          <GlassCard className="flex-1 min-h-0">
            <div className="p-4 flex flex-col gap-3 h-full no-scrollbar overflow-auto">
              <div className="flex flex-col gap-2 pr-1 no-scrollbar">
                {clusters.map((cluster) => {
                  const textColor = clusterColor(cluster.cluster_id) as string;
                  return (
                    <Button
                      key={cluster.cluster_id}
                      className={["mix-blend-multiply text-semibold bg-black/10"].join(" ")}
                      onClick={() => {
                        const node: NodeDatum = {
                          id: `cluster-${cluster.cluster_id}`,
                          type: "cluster",
                          cluster_id: cluster.cluster_id,
                          title: cluster.cluster_title ?? undefined,
                          article_summary: cluster.cluster_summary,
                        };
                        setFocusedNode(node);
                        setSelectedClusterId(cluster.cluster_id);
                      }}
                    >
                      <span
                        style={{
                          color: textColor,
                        }}
                      >
                        {cluster.cluster_title ?? `Cluster ${cluster.cluster_id}`}
                      </span>
                    </Button>
                  );
                })}
              </div>
            </div>
          </GlassCard>
        </div>
                
                <div className="flex-1 flex-col items-center justify-center ">
                    {/* Middle column with two stacked cards */}
                    <div className="w-[min(60vw,1020px)] h-[min(96vh,960px)] flex flex-col gap-4">
                        <GlassCard className="flex-[3] min-h-0 overflow-hidden">
                            {error ? (
                                <div className="p-4 text-red-400">{error}</div>
                            ) : loading ? (
                                <div className="p-4 text-gray-300">Loading graph…</div>
                            ) : (
                                <ForceGraph
                                    nodes={nodes}
                                    links={links}
                                    chargeStrength={-60}
                                    width={1100}
                                    height={1000}
                                    onNodeClick={(node) => {
                                      setFocusedNode(node);
                                      if (node.type === "cluster" && node.cluster_id != null) {
                                        setSelectedClusterId(node.cluster_id);
                                      }
                                    }}
                                    showLabels={false}
                                    zoom
                                    centerOnClusterId={selectedClusterId}
                                    centerScale={1.8}
                  // Articles always blue; selected cluster white; others schemeDark2
                  nodeFill={(d) =>
                    d.type === "article"
                      ? "#6C8AE4"
                      : (selectedClusterId != null && d.cluster_id === selectedClusterId
                          ? "#FFFFFF"
                          : clusterColor(d.cluster_id))
                  }
                  //cluster nodes slightly smaller than before, cluster nodes grow when clicked
                  nodeRadius={(d) => {
                    if (d.type === "cluster") {
                      const base = 12;
                      const selected = 18; // grow when selected
                      return d.cluster_id != null && d.cluster_id === selectedClusterId ? selected : base;
                    } else {
                      return 6;
                    }
                  }}  
                                    sizeByDegree={false}
                                />
                            )}
                        </GlassCard>
                        <GlassCard className="flex-[0.6] min-h-0 overflow-hidden">
                            <div className="w-full h-full">
                              <Carousel
                                items={articles.map((a) => ({ id: a.article_id, title: a.title ?? null, source: a.source ?? null }))}
                                durationSeconds={600}
                                onItemClick={(it) => {
                                  const art = articles.find((a) => a.article_id === it.id);
                                  if (!art) return;
                                  const node: NodeDatum = {
                                    id: `article-${art.article_id}`,
                                    type: "article",
                                    article_id: art.article_id,
                                    title: art.title,
                                    source: art.source,
                                    article_summary: art.article_summary,
                                    cluster_id: art.cluster_id,
                                  };
                                  setFocusedNode(node);
                                }}
                              />
                            </div>
                        </GlassCard>
                    </div>
                </div>

        {/*selection deets*/}
        <GlassCard className="w-[min(36vw,500px)] h-[min(96vh,960px)] min-h-0 overflow-hidden flex flex-col">
          <div className="p-4 space-y-4 h-full overflow-auto no-scrollbar">
            {!focusedNode ? (
              <div className="text-white/60  text-center">Select a node to see details.</div>
            ) : focusedNode.type === "article" ? (
              <ArticleCard
                title={focusedNode.title}
                source={(focusedNode as NodeDatum & { source?: string }).source ?? undefined}
                summary={focusedNode.article_summary}
              />
            ) : (
              (() => {
                const cid = focusedNode.cluster_id as number | undefined;
                const clusterMeta = clusters.find((c) => c.cluster_id === cid);
                const clusterArticles = articles
                  .filter((a) => a.cluster_id === cid)
                  .map((a) => ({ id: a.article_id, title: a.title, source: a.source ?? null, summary: a.article_summary ?? null }));
                return (
                  <ClusterCard
                    title={clusterMeta?.cluster_title ?? `Cluster ${cid ?? ""}`}
                    summary={clusterMeta?.cluster_summary ?? (focusedNode.article_summary ?? null)}
                    articles={clusterArticles}
                  />
                );
              })()
            )}
          </div>
        </GlassCard>
      </div>
  </div>
    );
};

export default Landing;