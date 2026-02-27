import React, { useEffect, useRef } from 'react';
import mermaid from 'mermaid';
import { Activity } from 'lucide-react';

export type AgentFlowEvent = {
    type: 'agent_flow';
    event: 'plan_generated' | 'task_start' | 'task_complete';
    plan?: {
        plan: Array<{
            type: 'task' | 'parallel';
            name?: string;
            role?: string;
            instruction?: string;
            subtasks?: Array<{ role: string; instruction: string }>;
        }>
    };
    taskId?: string;
    role?: string;
    instruction?: string;
    result?: string;
    timestamp?: string;
};

interface AgentFlowGraphProps {
    events: AgentFlowEvent[];
}

export default function AgentFlowGraph({ events }: AgentFlowGraphProps) {
    const containerRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        mermaid.initialize({
            startOnLoad: false,
            theme: 'dark',
            securityLevel: 'loose',
            fontFamily: 'monospace',
            flowchart: {
                htmlLabels: true,
                curve: 'basis'
            }
        });
    }, []);

    useEffect(() => {
        if (!containerRef.current || events.length === 0) return;

        let graphDef = 'graph TD\n';
        graphDef += '  M["🤖 Manager Agent"]:::manager\n';
        graphDef += '  classDef manager fill:#1e3a8a,stroke:#3b82f6,stroke-width:2px,color:#fff;\n';
        graphDef += '  classDef worker fill:#0f766e,stroke:#14b8a6,stroke-width:2px,color:#fff;\n';
        graphDef += '  classDef pending fill:#3f3f46,stroke:#71717a,stroke-width:1px,stroke-dasharray: 5 5,color:#a1a1aa;\n';

        const planEvent = events.find(e => e.event === 'plan_generated');

        if (planEvent && planEvent.plan && planEvent.plan.plan) {
            let prevNodes = ['M']; // Keep track of the preceding layer of nodes to link edges

            planEvent.plan.plan.forEach((step, stepIdx) => {
                const stepNum = stepIdx + 1;
                let currentLayerNodes: string[] = [];

                if (step.type === 'task' && step.role) {
                    const taskId = `${stepNum}`;
                    const nodeName = `T${taskId}`;
                    currentLayerNodes.push(nodeName);

                    const startEvent = events.find(e => e.event === 'task_start' && e.taskId === taskId);
                    const completeEvent = events.find(e => e.event === 'task_complete' && e.taskId === taskId);

                    let stateLabel = completeEvent ? '<br/><b><font color="#34d399">[COMPLETED]</font></b>' :
                        startEvent ? '<br/><i><font color="#60a5fa">[IN PROGRESS]</font></i>' : '';
                    let className = completeEvent || startEvent ? 'worker' : 'pending';

                    graphDef += `  ${nodeName}["Sub-Agent: ${step.role}${stateLabel}"]:::${className}\n`;

                } else if (step.type === 'parallel' && step.subtasks) {
                    graphDef += `  subgraph PG${stepNum} ["Parallel: ${step.name || 'Data Fetch'}"]\n`;
                    graphDef += `    direction TB\n`;

                    step.subtasks.forEach((subtask, subIdx) => {
                        const taskId = `${stepNum}-${subIdx + 1}`;
                        const nodeName = `P${stepNum}_${subIdx + 1}`;
                        currentLayerNodes.push(nodeName);

                        const startEvent = events.find(e => e.event === 'task_start' && e.taskId === taskId);
                        const completeEvent = events.find(e => e.event === 'task_complete' && e.taskId === taskId);

                        let stateLabel = completeEvent ? '<br/><b><font color="#34d399">[COMPLETED]</font></b>' :
                            startEvent ? '<br/><i><font color="#60a5fa">[IN PROGRESS]</font></i>' : '';
                        let className = completeEvent || startEvent ? 'worker' : 'pending';

                        graphDef += `    ${nodeName}["Sub-Agent: ${subtask.role}${stateLabel}"]:::${className}\n`;
                    });

                    graphDef += `  end\n`;
                }

                // Draw edges from all nodes in the previous layer to all nodes in the current layer
                prevNodes.forEach(prev => {
                    currentLayerNodes.forEach(curr => {
                        let edgeLabel = prev === 'M' ? 'Task 1' : 'Context Hand-off';

                        // Extract context preview if the previous node was a completed task
                        if (prev !== 'M') {
                            // prev could be 'T2' or 'P2_1'
                            const isParallel = prev.startsWith('P');
                            const prevTaskId = isParallel ? prev.substring(1).replace('_', '-') : prev.substring(1);

                            const prevCompleteEvent = events.find(e => e.event === 'task_complete' && e.taskId === prevTaskId);
                            if (prevCompleteEvent && prevCompleteEvent.result) {
                                // Clean up the result for safe Mermaid rendering
                                // We strip quotes, brackets, and specific unescaped control characters
                                // But permit HTML brackets so Mermaid can parse <br/>
                                let safeResult = prevCompleteEvent.result
                                    .replace(/["'\\[\\]{}]/g, ' ')
                                    .replace(/\\n/g, '<br/>')
                                    .replace(/\n/g, '<br/>')
                                    .substring(0, 100)
                                    .trim();

                                if (prevCompleteEvent.result.length > 100) safeResult += '...';
                                edgeLabel = `<b>Context</b>:<br/><i>${safeResult}</i>`;
                            }
                        }

                        // Clean up label if parallel fan-out is large to prevent UI clutter
                        if (currentLayerNodes.length > 1 || prevNodes.length > 1) {
                            if (prev === 'M') edgeLabel = '';
                            else edgeLabel = 'Merged Context';
                        }

                        if (edgeLabel) {
                            graphDef += `  ${prev} -->|"${edgeLabel}"| ${curr}\n`;
                        } else {
                            graphDef += `  ${prev} --> ${curr}\n`;
                        }
                    });
                });

                prevNodes = currentLayerNodes; // Push forward the execution sequence
            });
        }

        const renderGraph = async () => {
            try {
                const uniqueId = `mermaid-svg-${Date.now()}`;
                const { svg } = await mermaid.render(uniqueId, graphDef);
                if (containerRef.current) {
                    containerRef.current.innerHTML = svg;
                }
            } catch (err) {
                console.error("Mermaid Render Error", err);
            }
        };

        renderGraph();
    }, [events]);

    if (events.length === 0) {
        return (
            <div className="flex-1 flex flex-col items-center justify-center p-10 h-full bg-slate-900/50 rounded-xl border border-slate-800/60 mt-6 relative overflow-hidden shrink-0">
                <Activity className="w-12 h-12 mb-4 animate-pulse text-slate-600" />
                <p className="text-slate-400">Awaiting Agent Execution Flow...</p>
                <p className="text-xs text-slate-500 mt-2">Trigger an autonomous agent chain in the chat to see real-time task sequencing.</p>
            </div>
        );
    }

    return (
        <div className="flex-1 flex flex-col w-full h-full min-h-[500px] mt-6 bg-slate-950/80 rounded-2xl border border-slate-800/80 backdrop-blur-xl shadow-2xl relative overflow-hidden group">
            <div className="absolute top-0 inset-x-0 h-px w-full bg-gradient-to-r from-transparent via-cyan-500/30 to-transparent z-10"></div>

            <header className="px-6 py-4 border-b border-slate-800/60 bg-slate-900/50 flex items-center justify-between z-10 shadow-sm backdrop-blur-md">
                <h3 className="font-bold text-white tracking-tight flex items-center gap-2">
                    <Activity className="w-4 h-4 text-cyan-400" />
                    Agent Execution Flow
                </h3>
                <span className="text-xs font-mono font-medium text-slate-400 bg-slate-900 px-3 py-1 rounded-full border border-slate-700/50">
                    {events.length} Flow Events Mapped
                </span>
            </header>

            <div className="flex-1 w-full h-full overflow-auto relative p-8 fade-in flex items-center justify-center bg-transparent">
                <div ref={containerRef} className="w-full flex justify-center custom-mermaid-container transition-all"></div>
            </div>
        </div>
    );
}
