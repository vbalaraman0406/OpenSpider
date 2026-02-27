import { useState, useEffect, useRef } from 'react';
import { Activity, Terminal, CheckCircle2, Server, Key, Bot, Send, MessageSquare, Radio, Smartphone, MessagesSquare, Users, Globe, Play, Square, Settings, RefreshCw, LayoutDashboard, ListTree, FolderGit2, Wrench, FileText, Search, Download, X } from 'lucide-react';

interface ChannelConfig {
    id: string;
    name: string;
    icon: React.ElementType;
    status: 'running' | 'offline' | 'configured';
    lastProbe?: string;
    lastStart?: string;
    authAge?: string;
    description: string;
}

function ChannelCard({ channel }: { channel: ChannelConfig }) {
    const isRunning = channel.status === 'running';
    const isOffline = channel.status === 'offline';

    return (
        <div className="bg-slate-900/40 backdrop-blur-xl rounded-2xl border border-white/5 p-6 flex flex-col relative overflow-hidden group hover:bg-slate-900/60 transition-all duration-300 shadow-xl hover:shadow-2xl hover:shadow-blue-500/5">
            {/* Subtle Gradient Glow inside card */}
            <div className="absolute top-0 inset-x-0 h-px w-full bg-gradient-to-r from-transparent via-white/10 to-transparent"></div>

            <div className="flex justify-between items-start mb-6">
                <div className="flex items-center gap-4">
                    <div className={`p-3 rounded-xl flex items-center justify-center shrink-0 ${isRunning ? 'bg-blue-500/10 text-blue-400 border border-blue-500/20' : 'bg-slate-800/50 text-slate-400 border border-slate-700/50'}`}>
                        <channel.icon className="w-6 h-6" />
                    </div>
                    <div>
                        <h3 className="text-lg font-semibold text-white tracking-tight">{channel.name}</h3>
                        <p className="text-xs text-slate-400 font-medium tracking-wide mt-1 line-clamp-1">{channel.description}</p>
                    </div>
                </div>
            </div>

            <div className="flex items-center justify-between mb-8 pb-4 border-b border-slate-800/60">
                <span className="text-sm font-medium text-slate-300">Live Status</span>
                <span className={`px-3 py-1 rounded-full text-xs font-semibold uppercase tracking-wider flex items-center gap-2 border ${isRunning ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20 shadow-[0_0_15px_rgba(16,185,129,0.1)]' : isOffline ? 'bg-red-500/10 text-red-400 border-red-500/20' : 'bg-slate-800 text-slate-400 border-slate-700'}`}>
                    <span className={`w-1.5 h-1.5 rounded-full ${isRunning ? 'bg-emerald-400 animate-pulse' : isOffline ? 'bg-red-500' : 'bg-slate-500'}`}></span>
                    {channel.status}
                </span>
            </div>

            <div className="grid grid-cols-2 gap-x-4 gap-y-3 mb-8">
                <div className="flex flex-col">
                    <span className="text-[10px] uppercase tracking-widest text-slate-500 font-semibold mb-1">Last Probe</span>
                    <span className="text-sm font-mono text-slate-300">{channel.lastProbe || 'N/A'}</span>
                </div>
                <div className="flex flex-col">
                    <span className="text-[10px] uppercase tracking-widest text-slate-500 font-semibold mb-1">Session Age</span>
                    <span className="text-sm font-mono text-slate-300">{channel.authAge || 'N/A'}</span>
                </div>
            </div>

            <div className="mt-auto flex items-center justify-between gap-3 pt-2">
                <div className="flex gap-2">
                    {isRunning ? (
                        <button title="Stop Service" className="p-2.5 rounded-lg bg-slate-800/50 hover:bg-red-500/20 text-slate-400 hover:text-red-400 transition-colors border border-transparent hover:border-red-500/30">
                            <Square className="w-4 h-4 fill-current" />
                        </button>
                    ) : (
                        <button title="Start Service" className="p-2.5 rounded-lg bg-slate-800/50 hover:bg-emerald-500/20 text-slate-400 hover:text-emerald-400 transition-colors border border-transparent hover:border-emerald-500/30">
                            <Play className="w-4 h-4 fill-current" />
                        </button>
                    )}
                    <button title="Reload Config" className="p-2.5 rounded-lg bg-slate-800/50 hover:bg-slate-700 text-slate-400 hover:text-white transition-colors border border-transparent hover:border-slate-600">
                        <RefreshCw className="w-4 h-4" />
                    </button>
                </div>

                <button className={`px-4 py-2.5 rounded-lg text-sm font-semibold transition-colors flex items-center gap-2 ${isRunning ? 'bg-blue-600 hover:bg-blue-500 text-white shadow-md shadow-blue-900/20' : 'bg-slate-800 hover:bg-slate-700 text-white'}`}>
                    <Settings className="w-4 h-4" />
                    Configure
                </button>
            </div>
        </div>
    );
}

const mockChannels: ChannelConfig[] = [
    { id: 'wa', name: 'WhatsApp', icon: Smartphone, status: 'running', lastProbe: '2m ago', authAge: '14d 2h', description: 'Primary agent interface for direct user SMS.' }
];

interface LogMessage {
    type: string;
    data: string;
    timestamp: string;
}

function OverviewView() {
    return (
        <div className="flex-1 p-10 overflow-y-auto fade-in">
            <div className="max-w-6xl mx-auto">
                <header className="mb-10">
                    <h2 className="text-3xl font-bold text-white tracking-tight">System Overview</h2>
                    <p className="text-slate-400 mt-2 text-sm max-w-2xl leading-relaxed">
                        Gateway status, entry points, and a fast health read.
                    </p>
                </header>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    {/* Gateway Access */}
                    <div className="bg-slate-900/40 backdrop-blur-xl rounded-2xl border border-white/5 p-6 shadow-xl relative overflow-hidden group hover:bg-slate-900/60 transition-all">
                        <div className="absolute top-0 inset-x-0 h-px w-full bg-gradient-to-r from-transparent via-indigo-500/30 to-transparent"></div>
                        <h3 className="text-lg font-semibold text-white mb-2 tracking-tight">Gateway Access</h3>
                        <p className="text-sm text-slate-400 mb-6">Where the dashboard connects and how it authenticates.</p>

                        <div className="grid grid-cols-2 gap-5 mb-5">
                            <div>
                                <label className="block text-[10px] uppercase tracking-widest text-slate-500 font-bold mb-2">WebSocket URL</label>
                                <input type="text" value="ws://127.0.0.1:4000" readOnly className="w-full bg-slate-950/50 border border-slate-800 rounded-lg px-4 py-2.5 text-sm font-mono text-slate-300 focus:outline-none focus:ring-1 focus:ring-indigo-500/50" />
                            </div>
                            <div>
                                <label className="block text-[10px] uppercase tracking-widest text-slate-500 font-bold mb-2">Gateway Token</label>
                                <input type="password" value="****************" readOnly className="w-full bg-slate-950/50 border border-slate-800 rounded-lg px-4 py-2.5 text-sm font-mono text-slate-300 focus:outline-none focus:ring-1 focus:ring-indigo-500/50" />
                            </div>
                        </div>
                        <div className="grid grid-cols-2 gap-5 mb-8">
                            <div>
                                <label className="block text-[10px] uppercase tracking-widest text-slate-500 font-bold mb-2">Password (not stored)</label>
                                <input type="password" placeholder="system or shared password" disabled className="w-full bg-slate-950/30 border border-slate-800/50 rounded-lg px-4 py-2.5 text-sm text-slate-500 cursor-not-allowed" />
                            </div>
                            <div>
                                <label className="block text-[10px] uppercase tracking-widest text-slate-500 font-bold mb-2">Default Session Key</label>
                                <input type="text" value="main" readOnly className="w-full bg-slate-950/50 border border-slate-800 rounded-lg px-4 py-2.5 text-sm font-mono text-slate-300 focus:outline-none focus:ring-1 focus:ring-indigo-500/50" />
                            </div>
                        </div>

                        <div className="flex gap-3">
                            <button className="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-sm font-medium transition-colors shadow-lg shadow-indigo-900/20">Connect</button>
                            <button className="px-5 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-sm font-medium transition-colors border border-slate-700">Refresh</button>
                        </div>
                    </div>

                    {/* Snapshot */}
                    <div className="bg-slate-900/40 backdrop-blur-xl rounded-2xl border border-white/5 p-6 shadow-xl relative overflow-hidden group hover:bg-slate-900/60 transition-all">
                        <div className="absolute top-0 inset-x-0 h-px w-full bg-gradient-to-r from-transparent via-emerald-500/30 to-transparent"></div>
                        <h3 className="text-lg font-semibold text-white mb-2 tracking-tight">Snapshot</h3>
                        <p className="text-sm text-slate-400 mb-6">Latest gateway handshake information.</p>

                        <div className="grid grid-cols-2 gap-4">
                            <div className="bg-slate-950/50 rounded-xl border border-slate-800/60 p-5">
                                <div className="text-[10px] uppercase tracking-widest text-slate-500 font-bold mb-2">Status</div>
                                <div className="text-2xl font-bold tracking-tight text-emerald-400 flex items-center gap-2">
                                    <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse relative top-0.5"></span>
                                    Online
                                </div>
                            </div>
                            <div className="bg-slate-950/50 rounded-xl border border-slate-800/60 p-5">
                                <div className="text-[10px] uppercase tracking-widest text-slate-500 font-bold mb-2">Uptime</div>
                                <div className="text-2xl font-bold tracking-tight text-slate-200">2d 4h</div>
                            </div>
                            <div className="bg-slate-950/50 rounded-xl border border-slate-800/60 p-5">
                                <div className="text-[10px] uppercase tracking-widest text-slate-500 font-bold mb-2">Tick Interval</div>
                                <div className="text-2xl font-bold tracking-tight text-slate-200 font-mono">1000ms</div>
                            </div>
                            <div className="bg-slate-950/50 rounded-xl border border-slate-800/60 p-5">
                                <div className="text-[10px] uppercase tracking-widest text-slate-500 font-bold mb-2">Channels Refresh</div>
                                <div className="text-2xl font-bold tracking-tight text-slate-200 font-mono">2m ago</div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* 3 Stats Bar */}
                <div className="grid grid-cols-3 gap-6 mt-8 pb-20">
                    <div className="bg-slate-900/40 backdrop-blur-xl rounded-2xl border border-white/5 p-6 shadow-xl relative overflow-hidden group hover:bg-slate-900/60 transition-all">
                        <div className="text-[10px] uppercase tracking-widest text-slate-500 font-bold mb-3">Instances</div>
                        <div className="text-5xl font-bold tracking-tight text-white mb-3">1</div>
                        <div className="text-sm text-slate-400 font-medium leading-relaxed">Presence beacons tracking active gateways in the last 5 minutes.</div>
                    </div>
                    <div className="bg-slate-900/40 backdrop-blur-xl rounded-2xl border border-white/5 p-6 shadow-xl relative overflow-hidden group hover:bg-slate-900/60 transition-all">
                        <div className="text-[10px] uppercase tracking-widest text-slate-500 font-bold mb-3">Sessions</div>
                        <div className="text-5xl font-bold tracking-tight text-white mb-3">3</div>
                        <div className="text-sm text-slate-400 font-medium leading-relaxed">Recent unique session keys currently being managed by the gateway.</div>
                    </div>
                    <div className="bg-slate-900/40 backdrop-blur-xl rounded-2xl border border-white/5 p-6 shadow-xl relative overflow-hidden group hover:bg-slate-900/60 transition-all opacity-70">
                        <div className="text-[10px] uppercase tracking-widest text-slate-500 font-bold mb-3">Cron</div>
                        <div className="text-5xl font-bold tracking-tight text-slate-600 mb-3">n/a</div>
                        <div className="text-sm text-slate-500 font-medium leading-relaxed">Next wake disabled. No recurring jobs are currently scheduled.</div>
                    </div>
                </div>

            </div>
        </div>
    );
}

function SessionsView() {
    return (
        <div className="flex-1 p-10 overflow-y-auto fade-in">
            <div className="max-w-6xl mx-auto">
                <header className="mb-8 flex justify-between items-end">
                    <div>
                        <h2 className="text-3xl font-bold text-white tracking-tight">Active Sessions</h2>
                        <p className="text-slate-400 mt-2 text-sm max-w-2xl leading-relaxed">
                            Inspect active conversation sessions and adjust per-session overrides.
                        </p>
                    </div>
                    <button className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg text-sm font-medium transition-colors border border-slate-700 flex items-center gap-2">
                        <RefreshCw className="w-4 h-4" />
                        Refresh
                    </button>
                </header>

                <div className="bg-slate-900/40 backdrop-blur-xl rounded-2xl border border-white/5 pb-2 shadow-xl overflow-hidden">
                    <div className="p-4 border-b border-slate-800/60 bg-slate-900/80 flex items-center gap-6">
                        <div className="flex items-center gap-3">
                            <label className="text-xs font-semibold text-slate-400">Active within (min)</label>
                            <input type="text" placeholder="120" className="w-16 bg-slate-950 border border-slate-800 rounded px-2 py-1 text-sm text-slate-300 focus:outline-none focus:border-amber-500/50" />
                        </div>
                        <div className="flex items-center gap-3">
                            <label className="text-xs font-semibold text-slate-400">Limit</label>
                            <input type="text" placeholder="100" className="w-16 bg-slate-950 border border-slate-800 rounded px-2 py-1 text-sm text-slate-300 focus:outline-none focus:border-amber-500/50" />
                        </div>
                        <div className="flex items-center gap-2 ml-4">
                            <input type="checkbox" className="rounded bg-slate-950 border-slate-800 text-amber-500 focus:ring-amber-500/30" />
                            <label className="text-xs font-semibold text-slate-400">Include global</label>
                        </div>
                        <div className="flex items-center gap-2">
                            <input type="checkbox" className="rounded bg-slate-950 border-slate-800 text-amber-500 focus:ring-amber-500/30" />
                            <label className="text-xs font-semibold text-slate-400">Include unknown</label>
                        </div>
                    </div>

                    <div className="overflow-x-auto">
                        <table className="w-full text-left text-sm whitespace-nowrap">
                            <thead className="bg-slate-950/30 text-slate-500 text-[10px] uppercase tracking-widest font-semibold border-b border-slate-800/60">
                                <tr>
                                    <th className="px-6 py-4">Key</th>
                                    <th className="px-6 py-4">Label</th>
                                    <th className="px-6 py-4">Kind</th>
                                    <th className="px-6 py-4">Updated</th>
                                    <th className="px-6 py-4 text-right">Tokens</th>
                                    <th className="px-6 py-4 text-center">Thinking</th>
                                    <th className="px-6 py-4 text-center">Verbose</th>
                                    <th className="px-6 py-4 text-center">Reasoning</th>
                                    <th className="px-6 py-4 text-right">Actions</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-slate-800/60 text-slate-300">
                                <tr className="hover:bg-slate-800/30 transition-colors">
                                    <td className="px-6 py-4 font-mono text-amber-400">main</td>
                                    <td className="px-6 py-4"><span className="bg-slate-800 px-2 py-1 rounded text-xs">gemini-2.5-flash</span></td>
                                    <td className="px-6 py-4">Gateway</td>
                                    <td className="px-6 py-4 text-slate-400 text-xs">2 mins ago</td>
                                    <td className="px-6 py-4 text-right font-mono">1,024</td>
                                    <td className="px-6 py-4 text-center"><input type="checkbox" className="rounded bg-slate-950 border-slate-800 text-amber-500 focus:ring-amber-500" /></td>
                                    <td className="px-6 py-4 text-center"><input type="checkbox" className="rounded bg-slate-950 border-slate-800 text-amber-500 focus:ring-amber-500" /></td>
                                    <td className="px-6 py-4 text-center"><input type="checkbox" className="rounded bg-slate-950 border-slate-800 text-amber-500 focus:ring-amber-500" /></td>
                                    <td className="px-6 py-4 text-right">
                                        <button className="text-xs text-red-400 hover:text-red-300 transition-colors px-2 py-1 border border-red-500/20 rounded hover:bg-red-500/10">Clear</button>
                                    </td>
                                </tr>
                                <tr className="hover:bg-slate-800/30 transition-colors">
                                    <td className="px-6 py-4 font-mono text-amber-400">worker-a</td>
                                    <td className="px-6 py-4"><span className="bg-slate-800 px-2 py-1 rounded text-xs">claude-3-opus</span></td>
                                    <td className="px-6 py-4">Worker</td>
                                    <td className="px-6 py-4 text-slate-400 text-xs">15 mins ago</td>
                                    <td className="px-6 py-4 text-right font-mono">8,401</td>
                                    <td className="px-6 py-4 text-center"><input type="checkbox" className="rounded bg-slate-950 border-slate-800 text-amber-500 focus:ring-amber-500" /></td>
                                    <td className="px-6 py-4 text-center"><input type="checkbox" className="rounded bg-slate-950 border-slate-800 text-amber-500 focus:ring-amber-500" /></td>
                                    <td className="px-6 py-4 text-center"><input type="checkbox" className="rounded bg-slate-950 border-slate-800 text-amber-500 focus:ring-amber-500" defaultChecked /></td>
                                    <td className="px-6 py-4 text-right">
                                        <button className="text-xs text-red-400 hover:text-red-300 transition-colors px-2 py-1 border border-red-500/20 rounded hover:bg-red-500/10">Clear</button>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    );
}

function AgentsView() {
    const mockAgents = [
        {
            id: 'gateway',
            name: 'Gateway Architect',
            role: 'Handles default routing.',
            status: 'emerald',
            initial: 'G',
            color: 'fuchsia',
            model: 'gemini-2.5-flash-thinking-exp',
            prompt: 'You are the primary gateway agent for OpenSpider. Analyze all incoming requests across all channels and determine if you can answer them or if you need to dispatch a specialized worker agent.',
            skills: ['web_search', 'calculator', 'worker_dispatch']
        },
        {
            id: 'analyst',
            name: 'Data Analyst',
            role: 'Python chart generator.',
            status: 'slate',
            initial: 'D',
            color: 'blue',
            model: 'claude-3-5-sonnet-20241022',
            prompt: 'You are a data analysis agent. You write python to analyze CSVs and plot charts.',
            skills: ['run_python', 'read_file']
        }
    ];

    const [selectedAgentId, setSelectedAgentId] = useState('gateway');
    const selectedAgent = mockAgents.find(a => a.id === selectedAgentId) || mockAgents[0];

    return (
        <div className="flex-1 p-10 overflow-y-auto fade-in h-full flex flex-col">
            <header className="mb-8 shrink-0 flex justify-between items-end">
                <div>
                    <h2 className="text-3xl font-bold text-white tracking-tight">Agents Workspace</h2>
                    <p className="text-slate-400 mt-2 text-sm max-w-2xl leading-relaxed">
                        Manage agent profiles, specific system prompts, and tool access permissions.
                    </p>
                </div>
                <button className="px-4 py-2 bg-fuchsia-600 hover:bg-fuchsia-500 text-white rounded-lg text-sm font-medium transition-colors shadow-lg shadow-fuchsia-900/20" onClick={() => alert('Create Agent dialog would open here')}>
                    Create Agent
                </button>
            </header>

            <div className="flex-1 min-h-0 flex gap-6">
                <div className="w-[300px] flex flex-col gap-3 shrink-0">
                    <div className="relative">
                        <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
                        <input type="text" placeholder="Search agents..." className="w-full bg-slate-900/50 border border-slate-800 rounded-lg pl-9 pr-4 py-2.5 text-sm text-slate-300 focus:outline-none focus:ring-1 focus:ring-fuchsia-500/50" />
                    </div>

                    <div className="flex-1 overflow-y-auto space-y-2 pr-2">
                        {mockAgents.map(agent => (
                            <button
                                key={agent.id}
                                onClick={() => setSelectedAgentId(agent.id)}
                                className={`w-full text-left p-4 rounded-xl border transition-all flex items-center justify-between group ${selectedAgentId === agent.id
                                    ? `border-${agent.color}-500/30 bg-${agent.color}-500/10`
                                    : 'border-white/5 bg-slate-900/40 hover:bg-slate-800/60'
                                    }`}
                            >
                                <div>
                                    <h4 className={`text-sm font-semibold transition-colors ${selectedAgentId === agent.id ? `text-${agent.color}-400` : 'text-slate-300 group-hover:text-white'}`}>
                                        {agent.name}
                                    </h4>
                                    <p className={`text-xs mt-1 ${selectedAgentId === agent.id ? 'text-slate-400' : 'text-slate-500'}`}>
                                        {agent.role}
                                    </p>
                                </div>
                                <span className={`w-2 h-2 rounded-full bg-${agent.status}-400`}></span>
                            </button>
                        ))}
                    </div>
                </div>

                <div className="flex-1 bg-slate-900/40 backdrop-blur-xl rounded-2xl border border-white/5 p-8 shadow-xl relative overflow-hidden group hover:bg-slate-900/60 transition-all">
                    <div className={`absolute top-0 inset-x-0 h-px w-full bg-gradient-to-r from-transparent via-${selectedAgent.color}-500/30 to-transparent`}></div>
                    <div className="flex items-center gap-4 mb-8">
                        <div className={`w-16 h-16 rounded-2xl bg-${selectedAgent.color}-500/20 border border-${selectedAgent.color}-500/30 flex items-center justify-center text-${selectedAgent.color}-400 text-2xl font-bold`}>
                            {selectedAgent.initial}
                        </div>
                        <div>
                            <h2 className="text-2xl font-bold text-white tracking-tight">{selectedAgent.name}</h2>
                            <p className="text-slate-400 text-sm mt-1">Model: {selectedAgent.model}</p>
                        </div>
                    </div>

                    <div className="space-y-6">
                        <div>
                            <label className="block text-[10px] uppercase tracking-widest text-slate-500 font-bold mb-3">System Prompt Details</label>
                            <textarea
                                className={`w-full h-32 bg-slate-950/50 border border-slate-800 rounded-lg px-4 py-3 text-sm font-mono text-slate-300 focus:outline-none focus:ring-1 focus:ring-${selectedAgent.color}-500/50 resize-none`}
                                value={selectedAgent.prompt}
                                readOnly
                            />
                        </div>

                        <div>
                            <label className="block text-[10px] uppercase tracking-widest text-slate-500 font-bold mb-3">Capabilities (Skills context)</label>
                            <div className="flex flex-wrap gap-2">
                                {selectedAgent.skills.map(skill => (
                                    <span key={skill} className="px-3 py-1.5 bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 rounded-lg text-xs font-semibold">
                                        {skill}
                                    </span>
                                ))}
                                <button className="px-3 py-1.5 border border-dashed border-slate-700 text-slate-500 rounded-lg text-xs font-semibold hover:border-slate-500 hover:text-slate-300 transition-colors" onClick={() => alert('Add skill dialog would open here')}>
                                    + Add Skill
                                </button>
                            </div>
                        </div>
                    </div>

                    <div className="mt-auto pt-8 flex justify-end gap-3">
                        <button className="px-5 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-sm font-medium transition-colors border border-slate-700">Discard</button>
                        <button className={`px-5 py-2.5 bg-${selectedAgent.color}-600 hover:bg-${selectedAgent.color}-500 text-white rounded-lg text-sm font-medium transition-colors shadow-lg shadow-${selectedAgent.color}-900/20`}>Save Changes</button>
                    </div>
                </div>
            </div>
        </div>
    );
}

function SkillsView() {
    const [isAddModalOpen, setIsAddModalOpen] = useState(false);

    return (
        <div className="flex-1 p-10 overflow-y-auto fade-in relative">
            <div className="max-w-6xl mx-auto h-full flex flex-col">
                <header className="mb-8 flex justify-between items-end shrink-0">
                    <div>
                        <h2 className="text-3xl font-bold text-white tracking-tight">Dynamic Skills</h2>
                        <p className="text-slate-400 mt-2 text-sm max-w-2xl leading-relaxed">
                            View and manage functional capabilities loaded into the agent context windows.
                        </p>
                    </div>
                    <div className="flex items-center gap-4">
                        <div className="relative">
                            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
                            <input type="text" placeholder="Filter skills..." className="w-64 bg-slate-900/50 border border-slate-800 rounded-lg pl-9 pr-4 py-2 text-sm text-slate-300 focus:outline-none focus:ring-1 focus:ring-cyan-500/50" />
                        </div>
                        <button className="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg text-sm font-medium transition-colors shadow-lg shadow-cyan-900/20" onClick={() => setIsAddModalOpen(true)}>
                            + Add Skill
                        </button>
                    </div>
                </header>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 flex-1 min-h-0 overflow-y-auto pb-10">
                    <div className="bg-slate-900/40 backdrop-blur-xl rounded-2xl border border-white/5 p-6 shadow-xl relative overflow-hidden group hover:bg-slate-900/60 transition-all">
                        <div className="absolute top-0 inset-x-0 h-px w-full bg-gradient-to-r from-transparent via-cyan-500/30 to-transparent"></div>
                        <div className="flex items-center gap-3 mb-4">
                            <div className="p-2.5 rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                                <Globe className="w-5 h-5" />
                            </div>
                            <h3 className="text-lg font-semibold text-white tracking-tight">web_search</h3>
                        </div>
                        <p className="text-sm text-slate-400 mb-6 line-clamp-2">Performs a Google Search and returns the snippet and URL results.</p>

                        <div className="flex items-center justify-between mt-auto">
                            <span className="text-[10px] uppercase tracking-widest text-slate-500 font-bold bg-slate-950/50 px-2.5 py-1 rounded border border-slate-800/60 text-emerald-400">System Required</span>
                            <button className="text-xs font-semibold text-slate-400 hover:text-cyan-400 transition-colors" onClick={() => alert('Skill details panel would open here')}>Details</button>
                        </div>
                    </div>

                    <div className="bg-slate-900/40 backdrop-blur-xl rounded-2xl border border-white/5 p-6 shadow-xl relative overflow-hidden group hover:bg-slate-900/60 transition-all">
                        <div className="absolute top-0 inset-x-0 h-px w-full bg-gradient-to-r from-transparent via-cyan-500/30 to-transparent"></div>
                        <div className="flex items-center gap-3 mb-4">
                            <div className="p-2.5 rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                                <Terminal className="w-5 h-5" />
                            </div>
                            <h3 className="text-lg font-semibold text-white tracking-tight">run_python</h3>
                        </div>
                        <p className="text-sm text-slate-400 mb-6 line-clamp-2">Executes python code in an isolated sandbox environment.</p>

                        <div className="flex items-center justify-between mt-auto">
                            <span className="text-[10px] uppercase tracking-widest text-slate-500 font-bold bg-slate-950/50 px-2.5 py-1 rounded border border-slate-800/60">Managed</span>
                            <button className="text-xs font-semibold text-slate-400 hover:text-cyan-400 transition-colors" onClick={() => alert('Skill details panel would open here')}>Details</button>
                        </div>
                    </div>
                </div>
            </div>

            {/* Glassmorphic Modal Overlay */}
            {isAddModalOpen && (
                <div className="absolute inset-0 z-50 flex items-center justify-center p-10 fade-in">
                    {/* Darker Blur Backdrop */}
                    <div
                        className="absolute inset-0 bg-slate-950/80 backdrop-blur-md"
                        onClick={() => setIsAddModalOpen(false)}
                    />

                    {/* Modal Window */}
                    <div className="bg-slate-900/90 border border-cyan-500/30 rounded-2xl shadow-[0_0_50px_rgba(6,182,212,0.1)] w-full max-w-2xl relative z-10 overflow-hidden flex flex-col max-h-[85vh]">
                        {/* Top Gradient Bar */}
                        <div className="absolute top-0 inset-x-0 h-1 w-full bg-gradient-to-r from-cyan-500 to-blue-500"></div>

                        <header className="px-6 py-5 border-b border-slate-800/60 flex items-center justify-between shrink-0">
                            <div className="flex items-center gap-3">
                                <div className="p-2 rounded-lg bg-cyan-500/20 text-cyan-400">
                                    <ListTree className="w-5 h-5" />
                                </div>
                                <div>
                                    <h3 className="text-lg font-bold text-white tracking-tight">Add Dynamic Skill</h3>
                                    <p className="text-xs text-slate-400">Create a new Python or Node capability</p>
                                </div>
                            </div>
                            <button
                                onClick={() => setIsAddModalOpen(false)}
                                className="p-2 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition-colors"
                            >
                                <X className="w-5 h-5" />
                            </button>
                        </header>

                        <div className="p-6 overflow-y-auto flex flex-col gap-6">
                            <div>
                                <label className="block text-[10px] uppercase tracking-widest text-slate-500 font-bold mb-2">Skill Name</label>
                                <input type="text" placeholder="e.g. format_date" className="w-full bg-slate-950/50 border border-slate-800 rounded-lg px-4 py-2.5 text-sm font-mono text-slate-300 focus:outline-none focus:ring-1 focus:ring-cyan-500/50" />
                            </div>

                            <div>
                                <label className="block text-[10px] uppercase tracking-widest text-slate-500 font-bold mb-2">Description</label>
                                <input type="text" placeholder="Explains what this tool does to the LLM" className="w-full bg-slate-950/50 border border-slate-800 rounded-lg px-4 py-2.5 text-sm text-slate-300 focus:outline-none focus:ring-1 focus:ring-cyan-500/50" />
                            </div>

                            <div className="flex-1 flex flex-col min-h-[200px]">
                                <div className="flex items-center justify-between mb-2">
                                    <label className="block text-[10px] uppercase tracking-widest text-slate-500 font-bold">Execution Code</label>
                                    <span className="text-[10px] font-mono text-slate-500 bg-slate-800 px-2 py-0.5 rounded">Python 3.10</span>
                                </div>
                                <textarea
                                    className="w-full flex-1 bg-slate-950/80 border border-slate-800 rounded-lg px-4 py-3 text-sm font-mono text-cyan-300 focus:outline-none focus:border-cyan-500/50 resize-none leading-relaxed"
                                    defaultValue={"def execute(args):\n    # Context: worker execution sandbox\n    return {\"status\": \"success\"}\n"}
                                />
                            </div>
                        </div>

                        <footer className="px-6 py-4 bg-slate-950/50 border-t border-slate-800/60 flex justify-end gap-3 shrink-0">
                            <button
                                onClick={() => setIsAddModalOpen(false)}
                                className="px-4 py-2 text-sm font-medium text-slate-300 hover:text-white transition-colors"
                            >
                                Cancel
                            </button>
                            <button className="px-5 py-2 bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg text-sm font-medium transition-colors shadow-lg shadow-cyan-900/20">
                                Save Skill
                            </button>
                        </footer>
                    </div>
                </div>
            )}
        </div>
    );
}

function LogsView({ logs }: { logs: LogMessage[] }) {
    return (
        <div className="flex-1 p-10 overflow-y-auto fade-in flex flex-col max-h-screen">
            <div className="flex-1 flex flex-col min-h-0 bg-slate-900/40 backdrop-blur-xl rounded-2xl border border-white/5 shadow-xl relative overflow-hidden group">
                <div className="absolute top-0 inset-x-0 h-px w-full bg-gradient-to-r from-transparent via-slate-500/30 to-transparent z-10"></div>

                <header className="px-6 py-5 border-b border-slate-800/60 shrink-0 flex items-center justify-between bg-slate-900/80">
                    <div className="flex items-center gap-4">
                        <h2 className="text-xl font-bold text-white tracking-tight">JSONL Telemetry</h2>
                        <div className="h-6 w-px bg-slate-800"></div>
                        <div className="flex items-center gap-2">
                            <input type="checkbox" className="rounded bg-slate-950 border-slate-800 text-blue-500 focus:ring-blue-500/30" defaultChecked />
                            <label className="text-xs font-semibold text-slate-400">Auto-follow</label>
                        </div>
                    </div>

                    <div className="flex items-center gap-4">
                        <div className="flex p-1 bg-slate-950 rounded-lg border border-slate-800">
                            <button className="px-3 py-1 text-[10px] uppercase tracking-widest font-bold text-slate-500 hover:text-white transition-colors">Trace</button>
                            <button className="px-3 py-1 text-[10px] uppercase tracking-widest font-bold text-slate-500 hover:text-white transition-colors">Debug</button>
                            <button className="px-3 py-1 text-[10px] uppercase tracking-widest font-bold bg-blue-500/20 text-blue-400 rounded hover:bg-blue-500/30 transition-colors shadow-sm">Info</button>
                            <button className="px-3 py-1 text-[10px] uppercase tracking-widest font-bold text-amber-500 hover:text-amber-400 hover:bg-amber-500/10 rounded transition-colors">Warn</button>
                            <button className="px-3 py-1 text-[10px] uppercase tracking-widest font-bold text-red-500 hover:text-red-400 hover:bg-red-500/10 rounded transition-colors">Error</button>
                        </div>
                        <div className="relative w-48">
                            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
                            <input type="text" placeholder="Search logs..." className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-9 pr-4 py-1.5 text-sm font-mono text-slate-300 focus:outline-none focus:border-blue-500/50" />
                        </div>
                        <button className="p-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg transition-colors border border-slate-700" title="Refresh">
                            <RefreshCw className="w-4 h-4" />
                        </button>
                        <button className="p-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg transition-colors border border-slate-700" title="Export visible">
                            <Download className="w-4 h-4" />
                        </button>
                    </div>
                </header>

                <div className="flex-1 bg-slate-950/80 p-6 overflow-y-auto font-mono text-[13px] leading-relaxed text-slate-300">
                    {logs.length === 0 ? (
                        <div className="text-slate-500 opacity-60 text-center mt-20">Awaiting stream...</div>
                    ) : logs.map((l, i) => (
                        <div key={i} className="mb-1.5 break-all hover:bg-slate-800/50 px-2 py-0.5 rounded transition-colors">
                            <span className="text-slate-500 mr-4 select-none">{new Date(l.timestamp).toISOString().split('T')[1].replace('Z', '')}</span>
                            <span className={
                                l.data.includes('Error') || l.data.includes('Failed') ? 'text-red-400' :
                                    l.data.includes('Usage') ? 'text-blue-400' :
                                        l.data.includes('Worker') ? 'text-fuchsia-400' : 'text-slate-300'
                            }>
                                {l.data}
                            </span>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}

export default function App() {
    type TabName = 'overview' | 'channels' | 'sessions' | 'chat' | 'agents' | 'skills' | 'logs';
    const [activeTab, setActiveTab] = useState<TabName>('chat');
    const [logs, setLogs] = useState<LogMessage[]>([]);
    const [config, setConfig] = useState({ provider: 'Loading...', status: 'connecting' });
    const [skills, setSkills] = useState<string[]>([]);
    const [chatInput, setChatInput] = useState('');
    const [isTyping, setIsTyping] = useState(false);
    const scrollRef = useRef<HTMLDivElement>(null);
    const wsRef = useRef<WebSocket | null>(null);

    useEffect(() => {
        // Fetch initial config
        fetch('/api/config')
            .then(r => r.json())
            .then(data => setConfig(prev => ({ ...prev, provider: data.provider })))
            .catch(e => console.error("Could not fetch config API", e));

        fetch('/api/skills')
            .then(r => r.json())
            .then(data => setSkills(data.skills))
            .catch(e => console.error("Could not fetch skills API", e));

        // Connect WebSocket for live logs
        const host = window.location.port === '5173' ? 'localhost:4000' : window.location.host;
        const wsUrl = window.location.protocol === 'https:'
            ? `wss://${host}`
            : `ws://${host}`;
        const ws = new WebSocket(wsUrl);

        ws.onmessage = (event) => {
            try {
                const msg = JSON.parse(event.data);
                if (msg.type === 'log') {
                    setLogs(prev => [...prev.slice(-499), msg]); // Keep last 500 logs
                } else if (msg.type === 'chat_response') {
                    setLogs(prev => [...prev.slice(-499), { type: 'chat', data: `[Agent] ${msg.data}`, timestamp: msg.timestamp }]);
                    setIsTyping(false);
                } else if (msg.type === 'usage') {
                    const u = msg.data.usage;
                    setLogs(prev => [...prev.slice(-499), { type: 'usage', data: `[API Token Usage] Model: ${msg.data.model} | In: ${u.promptTokens} | Out: ${u.completionTokens} | Total: ${u.totalTokens}`, timestamp: msg.timestamp }]);
                }
            } catch (e) { }
        };

        ws.onopen = () => setConfig(prev => ({ ...prev, status: 'connected' }));
        ws.onclose = () => setConfig(prev => ({ ...prev, status: 'disconnected' }));

        wsRef.current = ws;

        return () => ws.close();
    }, []);

    const sendChatMessage = () => {
        if (!chatInput.trim() || !wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) return;

        const payload = { type: 'chat', text: chatInput };
        wsRef.current.send(JSON.stringify(payload));

        setLogs(prev => [...prev, { type: 'chat', data: `[You] ${chatInput}`, timestamp: new Date().toISOString() }]);
        setChatInput('');
        setIsTyping(true);
    };

    const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
        if (e.key === 'Enter') sendChatMessage();
    };

    // Auto-scroll logs
    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [logs]);

    return (
        <div className="h-screen bg-slate-950 flex font-sans text-slate-300 overflow-hidden">
            {/* Left Sidebar Navigation */}
            <aside className="w-[280px] bg-slate-900 border-r border-slate-800 flex flex-col z-20 shadow-xl shrink-0">
                <div className="p-6 flex items-center gap-3 border-b border-slate-800/60 pb-8 pt-8">
                    <div className="flex items-center justify-center p-2 bg-slate-950 rounded-xl border border-cyan-500/20 shadow-[0_0_20px_rgba(6,182,212,0.15)] ring-1 ring-white/5">
                        <img src="/openspider-logo.png" alt="OpenSpider Logo" className="w-10 h-10 object-contain drop-shadow-md" />
                    </div>
                    <div className="flex flex-col">
                        <h1 className="text-xl font-bold text-white tracking-tight leading-tight">OpenSpider</h1>
                        <p className="text-[11px] text-slate-400 font-semibold uppercase tracking-widest mt-0.5">Dashboard</p>
                    </div>
                </div>

                <nav className="flex-1 px-4 py-8 overflow-y-auto space-y-6">
                    {/* Control Group */}
                    <div className="space-y-1">
                        <div className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-3 px-2">Control</div>
                        <button
                            onClick={() => setActiveTab('overview')}
                            className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 ${activeTab === 'overview' ? 'bg-indigo-600/10 text-indigo-400 ring-1 ring-indigo-500/30 shadow-[0_4px_20px_-4px_rgba(99,102,241,0.2)]' : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'}`}
                        >
                            <LayoutDashboard className="w-4 h-4" />
                            Overview
                        </button>
                        <button
                            onClick={() => setActiveTab('channels')}
                            className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 ${activeTab === 'channels' ? 'bg-emerald-600/10 text-emerald-400 ring-1 ring-emerald-500/30 shadow-[0_4px_20px_-4px_rgba(16,185,129,0.2)]' : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'}`}
                        >
                            <Radio className="w-4 h-4" />
                            Channels
                        </button>
                        <button
                            onClick={() => setActiveTab('sessions')}
                            className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 ${activeTab === 'sessions' ? 'bg-amber-600/10 text-amber-400 ring-1 ring-amber-500/30 shadow-[0_4px_20px_-4px_rgba(245,158,11,0.2)]' : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'}`}
                        >
                            <ListTree className="w-4 h-4" />
                            Sessions
                        </button>
                    </div>

                    {/* Agent Group */}
                    <div className="space-y-1">
                        <div className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-3 px-2">Agent</div>
                        <button
                            onClick={() => setActiveTab('chat')}
                            className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 ${activeTab === 'chat' ? 'bg-blue-600/10 text-blue-400 ring-1 ring-blue-500/30 shadow-[0_4px_20px_-4px_rgba(37,99,235,0.2)]' : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'}`}
                        >
                            <MessageSquare className="w-4 h-4" />
                            Agent Chat
                        </button>
                        <button
                            onClick={() => setActiveTab('agents')}
                            className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 ${activeTab === 'agents' ? 'bg-fuchsia-600/10 text-fuchsia-400 ring-1 ring-fuchsia-500/30 shadow-[0_4px_20px_-4px_rgba(217,70,239,0.2)]' : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'}`}
                        >
                            <FolderGit2 className="w-4 h-4" />
                            Agents Workspace
                        </button>
                        <button
                            onClick={() => setActiveTab('skills')}
                            className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 ${activeTab === 'skills' ? 'bg-cyan-600/10 text-cyan-400 ring-1 ring-cyan-500/30 shadow-[0_4px_20px_-4px_rgba(6,182,212,0.2)]' : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'}`}
                        >
                            <Wrench className="w-4 h-4" />
                            Dynamic Skills
                        </button>
                    </div>

                    {/* Settings Group */}
                    <div className="space-y-1">
                        <div className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-3 px-2">Settings</div>
                        <button
                            onClick={() => setActiveTab('logs')}
                            className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 ${activeTab === 'logs' ? 'bg-slate-600/20 text-white ring-1 ring-slate-500/30 shadow-[0_4px_20px_-4px_rgba(100,116,139,0.2)]' : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'}`}
                        >
                            <FileText className="w-4 h-4" />
                            System Logs
                        </button>
                    </div>
                </nav>

                <div className="p-6 border-t border-slate-800/60 bg-slate-900/30 space-y-4">
                    <div className="flex flex-col">
                        <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">LLM Provider</span>
                        <div className="flex items-center gap-2">
                            <Bot className="w-4 h-4 text-blue-400" />
                            <span className="text-sm font-mono text-slate-300 truncate">{config.provider.toUpperCase()}</span>
                        </div>
                    </div>
                    <div className="h-px w-full bg-slate-800/60"></div>
                    <div className="flex items-center justify-between">
                        <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Engine</span>
                        <div className="flex items-center gap-2 bg-slate-950 px-2 py-1 rounded-md border border-slate-800">
                            <div className={`w-2 h-2 rounded-full ${config.status === 'connected' ? 'bg-emerald-500 animate-pulse shadow-[0_0_8px_rgba(16,185,129,0.5)]' : 'bg-red-500'}`}></div>
                            <span className="text-[11px] text-slate-300 font-medium capitalize tracking-wide">{config.status}</span>
                        </div>
                    </div>
                </div>
            </aside>

            {/* Main Content Area */}
            <main className="flex-1 flex flex-col h-screen overflow-hidden relative bg-slate-950/50">
                {activeTab === 'chat' && (
                    <div className="flex-1 p-8 flex gap-8 overflow-hidden max-w-[1600px] w-full mx-auto h-full fade-in">

                        {/* Left Column: Logs */}
                        < section className="flex-1 flex flex-col bg-slate-900/50 rounded-xl border border-slate-800/60 overflow-hidden shadow-lg backdrop-blur-sm" >
                            <div className="p-4 border-b border-slate-800/60 flex items-center gap-2 bg-slate-900">
                                <Terminal className="w-5 h-5 text-slate-400" />
                                <h2 className="font-semibold text-slate-200">Live Agent Communications</h2>
                            </div>
                            <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 font-mono text-sm space-y-2">
                                {logs.length === 0 ? (
                                    <div className="text-slate-500 flex flex-col items-center justify-center h-full opacity-60">
                                        <Activity className="w-12 h-12 mb-4 animate-pulse" />
                                        <span>Awaiting agent activity or chat messages...</span>
                                    </div>
                                ) : logs.map((log, i) => (
                                    <div key={i} className="flex gap-3 hover:bg-slate-800/30 p-1.5 rounded transition-colors group">
                                        <span className="text-slate-500 shrink-0 select-none text-xs mt-0.5">
                                            {new Date(log.timestamp).toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                                        </span>
                                        <span className={`break-all leading-relaxed ${log.data.includes('[You]') ? 'text-white font-semibold' :
                                            log.data.includes('[Agent]') ? 'text-indigo-300 font-semibold' :
                                                log.data.includes('[Manager]') ? 'text-amber-300' :
                                                    log.data.includes('[Worker') ? 'text-emerald-300' :
                                                        log.data.includes('[WhatsApp]') ? 'text-blue-300' :
                                                            log.data.includes('[API Token Usage]') ? 'text-fuchsia-400 font-medium' :
                                                                log.data.includes('Error') ? 'text-red-400 font-semibold' : 'text-slate-300'
                                            }`}>
                                            {log.data}
                                        </span>
                                    </div>
                                ))
                                }
                            </div >

                            {/* Chat Input */}
                            <div className="p-4 border-t border-slate-800/60 bg-slate-900 flex items-center gap-3">
                                <input
                                    title="Chat Input"
                                    type="text"
                                    value={chatInput}
                                    onChange={(e) => setChatInput(e.target.value)}
                                    onKeyDown={handleKeyDown}
                                    placeholder="Assign a task to OpenSpider..."
                                    className="flex-1 bg-slate-950 border border-slate-800 rounded-lg px-4 py-2.5 text-sm font-medium text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition-all"
                                    disabled={config.status !== 'connected' || isTyping}
                                />
                                <button
                                    title="Send Message"
                                    type="button"
                                    onClick={sendChatMessage}
                                    disabled={!chatInput.trim() || config.status !== 'connected' || isTyping}
                                    className="bg-blue-600 hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed text-white p-2.5 rounded-lg transition-colors flex items-center justify-center shrink-0"
                                >
                                    <Send className="w-5 h-5" />
                                </button>
                            </div>
                        </section >

                        {/* Right Column: Diagnostics */}
                        < aside className="w-[380px] flex flex-col gap-6" >

                            {/* Dynamic Skills */}
                            < div className="bg-slate-900/50 rounded-xl border border-slate-800/60 p-5 shadow-lg backdrop-blur-sm" >
                                <h3 className="font-semibold text-slate-200 flex items-center gap-2 mb-4">
                                    <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                                    Dynamic Skills
                                </h3>
                                <div className="space-y-3">
                                    <p className="text-xs text-slate-400 leading-relaxed mb-4">Files and code segments dynamically generated by the Worker Agents.</p>
                                    {skills.length === 0 ? (
                                        <div className="p-3 bg-slate-900 rounded-lg border border-slate-800/60 text-xs text-slate-500 text-center text-balance">
                                            No skills installed yet. The agent will compose them dynamically.
                                        </div>
                                    ) : (
                                        <ul className="space-y-2 max-h-[300px] overflow-y-auto pr-2">
                                            {skills.map(skill => (
                                                <li key={skill} className="text-sm font-mono text-slate-300 bg-slate-800/50 px-3 py-2 rounded-lg border border-slate-700/50 flex items-center justify-between group">
                                                    <span>{skill}</span>
                                                    <span className="text-[10px] uppercase tracking-wider text-slate-500 opacity-0 group-hover:opacity-100 transition-opacity">Loaded</span>
                                                </li>
                                            ))}
                                        </ul>
                                    )}
                                </div>
                            </div >

                            {/* System Info */}
                            < div className="bg-slate-900/50 rounded-xl border border-slate-800/60 p-5 shadow-lg backdrop-blur-sm" >
                                <h3 className="font-semibold text-slate-200 flex items-center gap-2 mb-4">
                                    <Server className="w-5 h-5 text-purple-400" />
                                    System Diagnostics
                                </h3>
                                <div className="space-y-4">
                                    <div className="flex justify-between items-center bg-slate-800/30 p-3 rounded-lg border border-slate-800/60">
                                        <span className="text-sm text-slate-400">Node Environment</span>
                                        <span className="text-sm text-slate-200 font-medium font-mono text-emerald-400 text-[13px]">Active</span>
                                    </div>
                                    <div className="flex justify-between items-center bg-slate-800/30 p-3 rounded-lg border border-slate-800/60">
                                        <span className="text-sm text-slate-400">Memory Usage</span>
                                        <span className="text-sm text-slate-200 font-medium font-mono text-[13px]">{'<'} 100 MB</span>
                                    </div>
                                    <div className="flex justify-between items-center bg-slate-800/30 p-3 rounded-lg border border-slate-800/60">
                                        <span className="text-sm text-slate-400">WhatsApp Gateway</span>
                                        <span className="text-sm text-slate-200 font-medium font-mono text-[13px] text-blue-400">Listening</span>
                                    </div>
                                </div>
                            </div >
                        </aside >
                    </div>
                )}

                {activeTab === 'channels' && (
                    <div className="flex-1 p-10 overflow-y-auto fade-in">
                        <div className="max-w-6xl mx-auto">
                            <header className="mb-10">
                                <h2 className="text-3xl font-bold text-white tracking-tight">Channels Management</h2>
                                <p className="text-slate-400 mt-2 text-sm max-w-2xl leading-relaxed">
                                    Configure and monitor external communication vectors for OpenSpider. Channels act as the sensory inputs and outputs for your autonomous agents.
                                </p>
                            </header>

                            {/* Channels Grid */}
                            <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6 pb-20">
                                {mockChannels.map(channel => (
                                    <ChannelCard key={channel.id} channel={channel} />
                                ))}
                            </div>
                        </div>
                    </div>
                )}

                {activeTab === 'overview' && <OverviewView />}
                {activeTab === 'sessions' && <SessionsView />}
                {activeTab === 'agents' && <AgentsView />}
                {activeTab === 'skills' && <SkillsView />}
                {activeTab === 'logs' && <LogsView logs={logs} />}
            </main >
        </div >
    );
}
