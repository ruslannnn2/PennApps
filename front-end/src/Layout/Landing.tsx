import GlassCard from "../components/GlassCard";
import ForceGraph, { type NodeDatum, type LinkDatum } from "../components/forcegraph";
import graph from "../data/graph.json"; // { nodes: [...], links: [...] }
import Button from "../components/Button";
import logo from "../../public/logo.png";


type Cluster = { cluster_id: number; cluster_summary: string; cluster_title: string | null };
type ClusterApiResponse = { clusters: Cluster[]; total: number };

const data = graph as { nodes: NodeDatum[]; links: LinkDatum[] };

const nodes = data.nodes;
const links = data.links


const res = await fetch("http://127.0.0.1:5000/api/clusters");
const { clusters } = await res.json();
const clusterIds = clusters.map(c => c.cluster_id);
const cluster_summarys = clusters.map(c => c.cluster_summary);
console.log(clusters);

const Landing = () => {
    return (
    <div className="bg-black min-h-screen flex items-center justify-center p-3">
      <div className="flex flex-col md:flex-row items-stretch md:items-stretch justify-center gap-4 w-full">
        {/* stretches to match middle card height */}
        <div className="w-[min(36vw,360px)]  h-[min(96vh,960px)] flex flex-col gap-4 min-h-0">
          {/* Split height evenly (both fill) */}
          <GlassCard className="flex-row min-h-0 items-center justify-center">
            <div className="flex items-center justify-center">
                <img src={logo} alt="logo" className="max-w-[50%] max-h-[50%] object-contain p-5"/>
            </div>
          </GlassCard>

          <GlassCard className="flex-1 min-h-0">
            <div className="p-4 flex flex-col gap-3 h-full no-scrollbar">
              <div className="flex flex-col gap-2 pr-1 no-scrollbar">
                {cluster_summarys.map((summary) => (
                  <Button className="mix-blend-multiply btn-shine" key={summary} onClick={() => console.log(`Clicked cluster ${summary}`)}>
                    {summary}
                  </Button>
                ))}
              </div>
            </div>
          </GlassCard>
        </div>

        <GlassCard className="w-[min(60vw,1020px)] h-[min(96vh,960px)] flex-1 overflow-hidden">
          <ForceGraph
            nodes={nodes}
            links={links}
            chargeStrength={-30}
            width={1100}
            height={1000}
            onNodeClick={(node) => console.log(`Clicked node ${node.id}`)}
            showLabels={false}
            zoom
          />
        </GlassCard>

        {/* RIGHT CARD (optional) */}
        <GlassCard className="w-[min(36vw,420px)] h-[min(96vh,960px)]" />
      </div>
    </div>
// ...existing code...
    );
};

export default Landing;