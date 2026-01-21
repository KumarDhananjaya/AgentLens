import { memo } from 'react';
import { Handle, Position, type NodeProps } from '@xyflow/react';
import { Bot, Wrench, Play, CircleStop, Activity } from 'lucide-react';
import { motion } from 'framer-motion';

const nodeIcons: Record<string, any> = {
    input: { icon: <Play size={16} color="#4ade80" />, class: 'node-input' },
    output: { icon: <CircleStop size={16} color="#f87171" />, class: 'node-output' },
    agent: { icon: <Bot size={16} color="#60a5fa" />, class: 'node-agent' },
    tool: { icon: <Wrench size={16} color="#fbbf24" />, class: 'node-tool' },
    default: { icon: <Activity size={16} color="#94a3b8" />, class: '' },
};

const CustomNode = ({ data, type }: NodeProps) => {
    const config = nodeIcons[data.type as string] || nodeIcons.default;
    const isActive = data.active;

    return (
        <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{
                scale: isActive ? 1.05 : 1,
                opacity: 1,
                boxShadow: isActive ? "0 0 20px rgba(59, 130, 246, 0.5), 0 0 10px rgba(59, 130, 246, 0.3)" : "none",
                borderColor: isActive ? "rgba(59, 130, 246, 0.8)" : "var(--node-border)"
            }}
            transition={{ duration: 0.3 }}
            className={`node-container ${config.class} ${isActive ? 'active-node' : ''}`}
        >
            <Handle type="target" position={Position.Top} className="handle" />
            <div className="node-header">
                <div className="node-icon-wrapper">
                    {config.icon}
                </div>
                <div className="node-content">
                    <span className="node-label-small">
                        {data.type as string || type}
                    </span>
                    <span className="node-label-main">{data.label as string}</span>
                    {isActive && <motion.div
                        layoutId="active-pill"
                        className="absolute top-2 right-2 w-2 h-2 bg-blue-500 rounded-full animate-pulse"
                        style={{ position: 'absolute', top: '8px', right: '8px' }}
                    />}
                </div>
            </div>
            <Handle type="source" position={Position.Bottom} className="handle" />
        </motion.div>
    );
};

export default memo(CustomNode);
