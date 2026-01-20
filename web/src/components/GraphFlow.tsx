import { useCallback, useEffect } from 'react';
import {
    ReactFlow,
    Controls,
    Background,
    useNodesState,
    useEdgesState,
    addEdge,
    type Connection,
    type Edge,
    BackgroundVariant,
    Panel,
    type Node,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';

import CustomNode from './CustomNode';
import { getLayoutedElements } from '../utils/layout';
import { Network, Maximize, RefreshCcw } from 'lucide-react';

const nodeTypes = {
    input: CustomNode,
    output: CustomNode,
    agent: CustomNode,
    tool: CustomNode,
    default: CustomNode,
};

const GraphFlow = () => {
    const [nodes, setNodes, onNodesChange] = useNodesState<Node>([]);
    const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>([]);

    const onConnect = useCallback(
        (params: Connection | Edge) => setEdges((eds) => addEdge(params, eds)),
        [setEdges]
    );

    const fetchGraph = async () => {
        try {
            const response = await fetch('/agentlens/schema');
            const data = await response.json();

            const { nodes: layoutedNodes, edges: layoutedEdges } = getLayoutedElements(
                data.nodes,
                data.edges
            );

            setNodes(layoutedNodes);
            setEdges(layoutedEdges);
        } catch (error) {
            console.error('Failed to fetch graph data:', error);

            const mockData = {
                nodes: [
                    { id: '__start__', type: 'input', data: { label: 'START', type: 'input' } },
                    { id: 'agent', type: 'agent', data: { label: 'Primary Agent', type: 'agent' } },
                    { id: 'tool_1', type: 'tool', data: { label: 'Search Tool', type: 'tool' } },
                    { id: '__end__', type: 'output', data: { label: 'END', type: 'output' } },
                ],
                edges: [
                    { id: 'e1', source: '__start__', target: 'agent', animated: true },
                    { id: 'e2', source: 'agent', target: 'tool_1', label: 'searching', animated: true },
                    { id: 'e3', source: 'tool_1', target: 'agent', animated: true },
                    { id: 'e4', source: 'agent', target: '__end__', animated: true },
                ]
            };

            const { nodes: layoutedNodes, edges: layoutedEdges } = getLayoutedElements(
                mockData.nodes as any,
                mockData.edges as any
            );
            setNodes(layoutedNodes);
            setEdges(layoutedEdges);
        }
    };

    useEffect(() => {
        fetchGraph();
    }, []);

    const onLayout = useCallback(
        (direction: string) => {
            const { nodes: layoutedNodes, edges: layoutedEdges } = getLayoutedElements(
                nodes,
                edges,
                direction
            );

            setNodes([...layoutedNodes]);
            setEdges([...layoutedEdges]);
        },
        [nodes, edges, setNodes, setEdges]
    );

    return (
        <div className="app-container">
            <ReactFlow
                nodes={nodes}
                edges={edges}
                onNodesChange={onNodesChange}
                onEdgesChange={onEdgesChange}
                onConnect={onConnect}
                nodeTypes={nodeTypes}
                fitView
                colorMode="dark"
            >
                <Background
                    variant={BackgroundVariant.Dots}
                    gap={20}
                    size={1}
                    color="#1e293b"
                />
                <Controls />

                <Panel position="top-right" className="panel-glass">
                    <button onClick={() => fetchGraph()} className="btn-secondary">
                        <RefreshCcw size={16} /> Sync
                    </button>
                    <button onClick={() => onLayout('TB')} className="btn-secondary">
                        <Network size={16} /> Vertical
                    </button>
                    <button onClick={() => onLayout('LR')} className="btn-secondary">
                        <Maximize size={16} className="rotate-90" /> Horizontal
                    </button>
                </Panel>

                <Panel position="top-left">
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                        <h1 className="title-gradient">AgentLens</h1>
                        <p style={{ fontSize: '10px', color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.2em', fontWeight: 'bold' }}>
                            Autonomous Agent Visualizer
                        </p>
                    </div>
                </Panel>
            </ReactFlow>
        </div>
    );
};

export default GraphFlow;
