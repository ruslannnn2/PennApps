import GlassCard from "../components/GlassCard";
import ForceGraph, { type NodeDatum, type LinkDatum } from "../components/forcegraph";
import graph from "../data/graph.json"; // { nodes: [...], links: [...] }

const data = graph as { nodes: NodeDatum[]; links: LinkDatum[] };

const nodes = data.nodes;
const links = data.links


const Landing = () => {
    return (
        <div className="bg-radial from-black from-40% to-gray-950 min-h-screen flex items-center justify-center p-3">

            <div className="flex flex-col md:flex-row items-center justify-center gap-4 w-full">
                <GlassCard className="w-[min(36vw,360px)] h-[min(96vh,960px)]">

                </GlassCard>
                <GlassCard className="w-[min(60vw,1020px)] h-[min(96vh,960px)] flex-1 items-justify-center overflow-hidden">
                    <ForceGraph
                        nodes={nodes}
                        links={links}
                        chargeStrength={-30}
                        width={1100}
                        height={1000}
                        onNodeClick={(node) => console.log(`Clicked node ${node.id}`)}
                        showLabels={false}
                        zoom={true}
                    />
                </GlassCard>
                <GlassCard className="w-[min(36vw,420px)] h-[min(96vh,960px)]">

                </GlassCard>
            </div>

        </div>
    );
};

export default Landing;