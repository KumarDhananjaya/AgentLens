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

    useEffect(() => {
        // Connect to WebSocket for real-time updates
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        // In development, Vite proxied to backend, so window.location.host usually works if proxy configured.
        // If served by backend, it definitely works.
        const wsUrl = `${protocol}//${window.location.host}/agentlens/ws`;

        let ws: WebSocket | null = null;
        let reconnectTimer: any;

        const connect = () => {
            ws = new WebSocket(wsUrl);

            ws.onopen = () => {
                console.log('Connected to AgentLens Runtime');
            };

            ws.onmessage = (event) => {
                try {
                    const message = JSON.parse(event.data);

                    if (message.type === 'chain_start' && message.node_id) {
                        setNodes((nds) => nds.map(n => ({
                            ...n,
                            data: {
                                ...n.data,
                                active: n.id === message.node_id
                            }
                        })));
                    }
                    else if (message.type === 'chain_end') {
                        // Clear active state on chain end (or handling specific run_id if complex)
                        // For simple visualization, clearing all active states on chain execution end (graph end) is safer,
                        // but for node-level, we might want to keep it active until next node starts?
                        // LangGraph runs are granular.

                        // If we want to "pulse" travel, we can clear active after a delay?
                        // Or just let the next chain_start clear it (since we filter by id).

                        // Current logic: un-highlight everything when a chain ends? 
                        // No, user might want to see the last step.
                        // But 'chain_end' usually means a node finished.

                        // Let's toggle off for the specific node if we knew the ID, but chain_end doesn't always have node_id in the event payload yet. 
                        // We can assume for now we just clear active states if it's a high-level chain end, or just rely on new start events.

                        // Better UX: keep active until next activation. 
                        // But if execution stops, we don't want it permanently glowing.

                        setTimeout(() => {
                            setNodes((nds) => nds.map(n => ({
                                ...n,
                                data: { ...n.data, active: false }
                            })));
                        }, 500);
                    }
                } catch (e) {
                    console.error('Error parsing WS message', e);
                }
            };

            ws.onclose = () => {
                console.log('WS Disconnected, retrying...');
                reconnectTimer = setTimeout(connect, 3000);
            };

            ws.onerror = (err) => {
                console.log("WS Error", err);
                ws?.close();
            };
        };

        connect();

        return () => {
            if (ws) {
                ws.onclose = null; // Prevent reconnect on unmount
                ws.close();
            }
            if (reconnectTimer) clearTimeout(reconnectTimer);
        };
    }, [setNodes]);

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
