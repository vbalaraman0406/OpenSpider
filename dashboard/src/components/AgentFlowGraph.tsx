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
            subtasks?: Array<{ role: string; instruction: string }>
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

/** Safely truncate and sanitize text for Mermaid edge labels */
function sanitizeLabel(text: string, maxLen: number = 80): string {
    let safe = text
        .replace(/["'\\[\]{}|#&<>]/g, ' ')
        .replace(/\n/g, ' ')
        .replace(/\s+/g, ' ')
        .trim();
    if (safe.length > maxLen) {
        safe = safe.substring(0, maxLen) + '…';
    }
    return safe;
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
                curve: 'basis',
                padding: 20,
                nodeSpacing: 60,
                rankSpacing: 80
            }
        });
    }, []);

    useEffect(() => {
        if (!containerRef.current || events.length === 0) return;

        let graphDef = 'graph TD\n';
        graphDef += '  M["🧠 Manager"]:::manager\n';
        graphDef += '  classDef manager fill:#1e3a8a,stroke:#3b82f6,stroke-width:2px,color:#fff;\n';
        graphDef += '  classDef worker fill:#0f766e,stroke:#14b8a6,stroke-width:2px,color:#fff;\n';
        graphDef += '  classDef complete fill:#065f46,stroke:#34d399,stroke-width:2px,color:#fff;\n';
        graphDef += '  classDef pending fill:#3f3f46,stroke:#71717a,stroke-width:1px,stroke-dasharray: 5 5,color:#a1a1aa;\n';
        graphDef += '  classDef result fill:#1e1b4b,stroke:#818cf8,stroke-width:2px,color:#c7d2fe;\n';

        const planEvent = events.find(e => e.event === 'plan_generated');

        if (planEvent && planEvent.plan && planEvent.plan.plan) {
            let prevNodes = ['M'];

            planEvent.plan.plan.forEach((step, stepIdx) => {
                const stepNum = stepIdx + 1;
                let currentLayerNodes: string[] = [];

                if (step.type === 'task' && step.role) {
                    const taskId = `${stepNum}`;
                    const nodeName = `T${taskId}`;
                    currentLayerNodes.push(nodeName);

                    const startEvent = events.find(e => e.event === 'task_start' && e.taskId === taskId);
                    const completeEvent = events.find(e => e.event === 'task_complete' && e.taskId === taskId);

                    // Build node label with status
                    let stateLabel = '';
                    let className = 'pending';
                    if (completeEvent) {
                        stateLabel = '<br/><b><font color="#34d399">✓ COMPLETED</font></b>';
                        className = 'complete';
                    } else if (startEvent) {
                        stateLabel = '<br/><i><font color="#60a5fa">⏳ IN PROGRESS</font></i>';
                        className = 'worker';
                    }

                    const roleEmoji = step.role?.toLowerCase().includes('cod') ? '⚡' : step.role?.toLowerCase().includes('research') ? '🔮' : '🔧';
                    graphDef += `  ${nodeName}["${roleEmoji} ${step.role}${stateLabel}"]:::${className}\n`;

                    // === EDGE: Manager/Previous → Worker (show instruction) ===
                    const instruction = startEvent?.instruction || step.instruction || '';
                    prevNodes.forEach(prev => {
                        if (instruction) {
                            const label = sanitizeLabel(instruction, 60);
                            graphDef += `  ${prev} -->|"📋 ${label}"| ${nodeName}\n`;
                        } else {
                            graphDef += `  ${prev} -->|"Task ${taskId}"| ${nodeName}\n`;
                        }
                    });

                    // === RESULT NODE: show result data below the worker ===
                    if (completeEvent && completeEvent.result) {
                        const resultPreview = sanitizeLabel(completeEvent.result, 120);
                        const resultNodeName = `R${taskId}`;
                        graphDef += `  ${resultNodeName}["📄 ${resultPreview}"]:::result\n`;
                        graphDef += `  ${nodeName} -.->|"Result"| ${resultNodeName}\n`;
                    }

                } else if (step.type === 'parallel' && step.subtasks) {
                    graphDef += `  subgraph PG${stepNum} ["⚡ Parallel: ${step.name || 'Data Fetch'}"]\n`;
                    graphDef += `    direction TB\n`;

                    step.subtasks.forEach((subtask, subIdx) => {
                        const taskId = `${stepNum}-${subIdx + 1}`;
                        const nodeName = `P${stepNum}_${subIdx + 1}`;
                        currentLayerNodes.push(nodeName);

                        const startEvent = events.find(e => e.event === 'task_start' && e.taskId === taskId);
                        const completeEvent = events.find(e => e.event === 'task_complete' && e.taskId === taskId);

                        let stateLabel = '';
                        let className = 'pending';
                        if (completeEvent) {
                            stateLabel = '<br/><b><font color="#34d399">✓ COMPLETED</font></b>';
                            className = 'complete';
                        } else if (startEvent) {
                            stateLabel = '<br/><i><font color="#60a5fa">⏳ IN PROGRESS</font></i>';
                            className = 'worker';
                        }

                        const subRoleEmoji = subtask.role?.toLowerCase().includes('cod') ? '⚡' : subtask.role?.toLowerCase().includes('research') ? '🔮' : '🔧';
                        graphDef += `    ${nodeName}["${subRoleEmoji} ${subtask.role}${stateLabel}"]:::${className}\n`;

                        // Result nodes for parallel tasks
                        if (completeEvent && completeEvent.result) {
                            const resultPreview = sanitizeLabel(completeEvent.result, 80);
                            const resultNodeName = `PR${stepNum}_${subIdx + 1}`;
                            graphDef += `    ${resultNodeName}["📄 ${resultPreview}"]:::result\n`;
                            graphDef += `    ${nodeName} -.->|"Result"| ${resultNodeName}\n`;
                        }
                    });

                    graphDef += `  end\n`;

                    // Draw edges from previous layer to parallel items with instructions
                    prevNodes.forEach(prev => {
                        step.subtasks!.forEach((subtask, subIdx) => {
                            const nodeName = `P${stepNum}_${subIdx + 1}`;
                            const instruction = subtask.instruction || '';
                            if (instruction) {
                                const label = sanitizeLabel(instruction, 50);
                                graphDef += `  ${prev} -->|"📋 ${label}"| ${nodeName}\n`;
                            } else {
                                graphDef += `  ${prev} --> ${nodeName}\n`;
                            }
                        });
                    });
                }

                if (currentLayerNodes.length > 0) {
                    prevNodes = currentLayerNodes;
                }
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
                <div className="flex items-center gap-3">
                    <span className="text-xs font-mono font-medium text-emerald-400 bg-emerald-950/60 px-3 py-1 rounded-full border border-emerald-700/40 flex items-center gap-1.5">
                        <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                        {events.filter(e => e.event === 'task_complete').length} / {events.filter(e => e.event === 'task_start').length} Tasks Done
                    </span>
                    <span className="text-xs font-mono font-medium text-slate-400 bg-slate-900 px-3 py-1 rounded-full border border-slate-700/50">
                        {events.length} Events
                    </span>
                </div>
            </header>

            <div className="flex-1 w-full h-full overflow-auto relative p-8 fade-in flex items-center justify-center bg-transparent">
                <div ref={containerRef} className="w-full flex justify-center custom-mermaid-container transition-all"></div>
            </div>
        </div>
    );
}
