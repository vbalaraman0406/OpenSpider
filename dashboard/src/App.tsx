import { useState, useEffect, useRef } from 'react';
import { Activity, Terminal, CheckCircle2, Server, Key, Bot, Send, MessageSquare, Radio, Smartphone, MessagesSquare, Users, Globe, Play, Square, Settings, RefreshCw, LayoutDashboard, ListTree, FolderGit2, Wrench, FileText, Search, Download, X, Trash, GitMerge, Timer, Plus, Clock, AlertTriangle } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import AgentFlowGraph, { AgentFlowEvent } from './components/AgentFlowGraph';
import { UsageView } from './components/UsageView';
import { WhatsAppSecurity } from './components/WhatsAppSecurity';
import { ProcessMonitor } from './components/ProcessMonitor';

const safeFormatTime = (ts: any) => {
    if (!ts) return '--:--:--';
    try {
        const d = new Date(ts);
        if (isNaN(d.getTime())) return '--:--:--';
        return d.toISOString().split('T')[1].replace('Z', '');
    } catch {
        return '--:--:--';
    }
};

const safeFormatTimestamp = (ts: any) => {
    if (!ts) return '--:--:--';
    try {
        const d = new Date(ts);
        if (isNaN(d.getTime())) return '--:--:--';
        return d.toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' });
    } catch {
        return '--:--:--';
    }
};

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

function ChannelCard({ channel, onConfigure }: { channel: ChannelConfig, onConfigure: () => void }) {
    const isRunning = channel.status === 'running';
    const isOffline = channel.status === 'offline';

    return (
        <div className="bg-slate-900/40 backdrop-blur-xl rounded-2xl border border-white/5 p-6 flex flex-col relative group hover:bg-slate-900/60 transition-all duration-300 shadow-xl hover:shadow-2xl hover:shadow-blue-500/5">
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

                <button
                    onClick={onConfigure}
                    className={`px-4 py-2.5 rounded-lg text-sm font-semibold transition-colors flex items-center gap-2 ${isRunning ? 'bg-blue-600 hover:bg-blue-500 text-white shadow-md shadow-blue-900/20' : 'bg-slate-800 hover:bg-slate-700 text-white'}`}
                >
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

function SessionsView({ provider }: { provider: string }) {
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
                                    <td className="px-6 py-4"><span className="bg-slate-800 px-2 py-1 rounded text-xs">{provider}</span></td>
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
                                    <td className="px-6 py-4"><span className="bg-slate-800 px-2 py-1 rounded text-xs">{provider}</span></td>
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

function AgentsView({ agents, onRefresh, provider, skills }: { agents: any[], onRefresh: () => void, provider: string, skills: string[] }) {

    const [selectedAgentId, setSelectedAgentId] = useState('gateway');

    // Auto-select the first available agent if the current selection is invalid (e.g., initial load)
    useEffect(() => {
        if (agents.length > 0 && !agents.find(a => a.id === selectedAgentId)) {
            setSelectedAgentId(agents[0].id);
        }
    }, [agents, selectedAgentId]);

    const selectedAgent = agents.find(a => a.id === selectedAgentId) || agents[0] || {
        id: 'error', name: 'No Agents Found', role: '', status: 'red', initial: '?', color: 'red', model: '', prompt: '', skills: [], pillars: {}
    };

    const [activeTab, setActiveTab] = useState<'identity' | 'soul' | 'userContext' | 'capabilities'>('identity');
    const [editedPillars, setEditedPillars] = useState<any>({});
    const [isSaving, setIsSaving] = useState(false);

    useEffect(() => {
        if (selectedAgent && selectedAgent.pillars) {
            setEditedPillars({
                identity: selectedAgent.pillars.identity || '',
                soul: selectedAgent.pillars.soul || '',
                userContext: selectedAgent.pillars.userContext || '',
                capabilities: selectedAgent.pillars.capabilities || ''
            });
        }
    }, [selectedAgent.id]);

    let activeCaps: any = {};
    try {
        activeCaps = JSON.parse(editedPillars.capabilities || '{}');
    } catch (e) { }

    const handleNameChange = (newName: string) => {
        const newCaps = { ...activeCaps, name: newName };
        setEditedPillars({ ...editedPillars, capabilities: JSON.stringify(newCaps, null, 2) });
    };

    const handleRoleChange = (newRole: string) => {
        const newCaps = { ...activeCaps, role: newRole };
        setEditedPillars({ ...editedPillars, capabilities: JSON.stringify(newCaps, null, 2) });
    };

    const handleSaveAgent = async () => {
        setIsSaving(true);
        try {
            const res = await fetch(`/api/agents/${selectedAgent.id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(editedPillars)
            });
            if (res.ok) {
                onRefresh();
            } else {
                alert('Failed to save agent persona');
            }
        } catch (e: any) { alert(e.message); }
        finally { setIsSaving(false); }
    };

    const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
    const [createAgentName, setCreateAgentName] = useState('');
    const [createAgentRole, setCreateAgentRole] = useState('');
    const [createAgentColor, setCreateAgentColor] = useState('emerald');
    const [createAgentPrompt, setCreateAgentPrompt] = useState('');

    const [isAddSkillModalOpen, setIsAddSkillModalOpen] = useState(false);
    const [skillToAdd, setSkillToAdd] = useState(skills.length > 0 ? skills[0] : '');

    return (
        <div className="flex-1 p-10 overflow-y-auto fade-in h-full flex flex-col">
            <header className="mb-8 shrink-0 flex justify-between items-end">
                <div>
                    <h2 className="text-3xl font-bold text-white tracking-tight">Agents Workspace</h2>
                    <p className="text-slate-400 mt-2 text-sm max-w-2xl leading-relaxed">
                        Manage agent profiles, specific system prompts, and tool access permissions.
                    </p>
                </div>
                <button className="px-4 py-2 bg-fuchsia-600 hover:bg-fuchsia-500 text-white rounded-lg text-sm font-medium transition-colors shadow-lg shadow-fuchsia-900/20" onClick={() => setIsCreateModalOpen(true)}>
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
                        {agents.map(agent => (
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
                        <div className="flex-1 min-w-0">
                            <input
                                type="text"
                                value={activeCaps.name || selectedAgent.name}
                                onChange={e => handleNameChange(e.target.value)}
                                className="text-2xl font-bold bg-transparent text-white tracking-tight border-b border-transparent hover:border-slate-800 focus:border-fuchsia-500 focus:outline-none transition-colors w-full px-1 -ml-1 rounded truncate"
                                placeholder="Agent Name"
                            />
                            <div className="flex items-center gap-3 mt-1.5 w-full">
                                <span className="text-slate-500 text-[10px] uppercase tracking-widest font-bold shrink-0">Role:</span>
                                <input
                                    type="text"
                                    value={activeCaps.role || selectedAgent.role}
                                    onChange={e => handleRoleChange(e.target.value)}
                                    className="text-slate-400 text-sm bg-transparent border-b border-transparent hover:border-slate-800 focus:border-fuchsia-500 focus:outline-none transition-colors flex-1 px-1 -ml-1 rounded truncate"
                                    placeholder="e.g. Chief Orchestrator"
                                />
                                <span className="text-slate-500 text-[10px] uppercase tracking-widest font-bold border-l border-slate-800 pl-3 shrink-0">Model:</span>
                                <span className="text-slate-400 text-xs font-mono shrink-0">{selectedAgent.model}</span>
                            </div>
                        </div>
                    </div>

                    <div className="space-y-6">
                        <div>
                            <div className="flex gap-2 mb-3 border-b border-slate-800/60 pb-2">
                                {['identity', 'soul', 'userContext', 'capabilities'].map(tab => (
                                    <button
                                        key={tab}
                                        onClick={() => setActiveTab(tab as any)}
                                        className={`px-4 py-2 text-xs font-bold uppercase tracking-widest rounded-t-lg transition-colors ${activeTab === tab ? `text-${selectedAgent.color}-400 border-b-2 border-${selectedAgent.color}-500` : 'text-slate-500 hover:text-slate-300'}`}
                                    >
                                        {tab === 'userContext' ? 'User Context' : tab}
                                    </button>
                                ))}
                            </div>
                            <textarea
                                className={`w-full h-64 bg-slate-950/50 border border-slate-800 rounded-lg px-4 py-3 text-sm font-mono text-slate-300 focus:outline-none focus:ring-1 focus:ring-${selectedAgent.color}-500/50 resize-none`}
                                value={editedPillars[activeTab] || ''}
                                onChange={e => setEditedPillars({ ...editedPillars, [activeTab]: e.target.value })}
                            />
                        </div>

                        <div>
                            <label className="block text-[10px] uppercase tracking-widest text-slate-500 font-bold mb-3">Capabilities (Skills context)</label>
                            <div className="flex flex-wrap gap-2">
                                {selectedAgent.skills.map((skill: string) => (
                                    <span key={skill} className="px-3 py-1.5 bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 rounded-lg text-xs font-semibold">
                                        {skill}
                                    </span>
                                ))}
                                <button className="px-3 py-1.5 border border-dashed border-slate-700 text-slate-500 rounded-lg text-xs font-semibold hover:border-slate-500 hover:text-slate-300 transition-colors" onClick={() => setIsAddSkillModalOpen(true)}>
                                    + Add Skill
                                </button>
                            </div>
                        </div>
                    </div>

                    <div className="mt-auto pt-8 flex items-center justify-between">
                        <div>
                            {selectedAgent.id !== 'manager' && (
                                <button
                                    onClick={() => {
                                        const nextStatus = (activeCaps.status === 'stopped') ? 'running' : 'stopped';
                                        setEditedPillars({ ...editedPillars, capabilities: JSON.stringify({ ...activeCaps, status: nextStatus }, null, 2) });
                                    }}
                                    className={`px-4 py-2 rounded-lg text-xs font-bold uppercase tracking-widest transition-colors border ${activeCaps.status === 'stopped'
                                        ? 'bg-emerald-500/10 text-emerald-400 hover:bg-emerald-500/20 border-emerald-500/30 shadow-[0_0_15px_rgba(16,185,129,0.15)]'
                                        : 'bg-red-500/10 text-red-400 hover:bg-red-500/20 border-red-500/30'
                                        }`}
                                >
                                    {activeCaps.status === 'stopped' ? '▶ Start Agent' : '⏹ Stop Agent'}
                                </button>
                            )}
                        </div>
                        <div className="flex gap-3">
                            <button
                                onClick={() => setEditedPillars(selectedAgent.pillars || {})}
                                className="px-5 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-sm font-medium transition-colors border border-slate-700"
                            >
                                Discard
                            </button>
                            <button
                                onClick={handleSaveAgent}
                                disabled={isSaving}
                                className={`px-5 py-2.5 bg-${selectedAgent.color}-600 hover:bg-${selectedAgent.color}-500 text-white rounded-lg text-sm font-medium transition-colors shadow-lg shadow-${selectedAgent.color}-900/20 disabled:opacity-50`}
                            >
                                {isSaving ? 'Saving...' : 'Save Changes'}
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            {/* Create Agent Modal Overlay */}
            {
                isCreateModalOpen && (
                    <div className="absolute inset-0 z-50 flex items-center justify-center p-10 fade-in">
                        <div className="absolute inset-0 bg-slate-950/80 backdrop-blur-md" onClick={() => setIsCreateModalOpen(false)} />
                        <div className="bg-slate-900/90 border border-fuchsia-500/30 rounded-2xl shadow-[0_0_50px_rgba(217,70,239,0.1)] w-full max-w-2xl relative z-10 overflow-hidden flex flex-col max-h-[85vh]">
                            <div className="absolute top-0 inset-x-0 h-1 w-full bg-gradient-to-r from-fuchsia-500 to-purple-500"></div>
                            <header className="px-6 py-5 border-b border-slate-800/60 flex items-center justify-between shrink-0">
                                <div className="flex items-center gap-3">
                                    <div className="p-2 rounded-lg bg-fuchsia-500/20 text-fuchsia-400">
                                        <Users className="w-5 h-5" />
                                    </div>
                                    <div>
                                        <h3 className="text-lg font-bold text-white tracking-tight">Create Agent</h3>
                                        <p className="text-xs text-slate-400">Configure a new AI worker profile</p>
                                    </div>
                                </div>
                                <button onClick={() => setIsCreateModalOpen(false)} className="p-2 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition-colors">
                                    <X className="w-5 h-5" />
                                </button>
                            </header>

                            <div className="p-6 overflow-y-auto flex flex-col gap-6">
                                <div className="grid grid-cols-2 gap-6">
                                    <div>
                                        <label className="block text-[10px] uppercase tracking-widest text-slate-500 font-bold mb-2">Agent Name</label>
                                        <input type="text" value={createAgentName} onChange={e => setCreateAgentName(e.target.value)} placeholder="e.g. Code Reviewer" className="w-full bg-slate-950/50 border border-slate-800 rounded-lg px-4 py-2.5 text-sm text-slate-300 focus:outline-none focus:ring-1 focus:ring-fuchsia-500/50" />
                                    </div>
                                    <div>
                                        <label className="block text-[10px] uppercase tracking-widest text-slate-500 font-bold mb-2">Role Summary</label>
                                        <input type="text" value={createAgentRole} onChange={e => setCreateAgentRole(e.target.value)} placeholder="e.g. Analyzes PRs for bugs" className="w-full bg-slate-950/50 border border-slate-800 rounded-lg px-4 py-2.5 text-sm text-slate-300 focus:outline-none focus:ring-1 focus:ring-fuchsia-500/50" />
                                    </div>
                                </div>

                                <div className="grid grid-cols-2 gap-6">
                                    <div>
                                        <label className="block text-[10px] uppercase tracking-widest text-slate-500 font-bold mb-2">Primary Model</label>
                                        <div className="w-full bg-slate-950/30 border border-slate-800/50 rounded-lg px-4 py-2.5 text-sm text-slate-500 flex items-center gap-2 cursor-not-allowed">
                                            <Bot className="w-4 h-4 text-slate-500" />
                                            System Default ({provider})
                                        </div>
                                    </div>
                                    <div>
                                        <label className="block text-[10px] uppercase tracking-widest text-slate-500 font-bold mb-2">Theme Color</label>
                                        <select value={createAgentColor} onChange={e => setCreateAgentColor(e.target.value)} className="w-full bg-slate-950/50 border border-slate-800 rounded-lg px-4 py-2.5 text-sm text-slate-300 focus:outline-none focus:ring-1 focus:ring-fuchsia-500/50 appearance-none">
                                            <option value="emerald">Emerald</option>
                                            <option value="blue">Blue</option>
                                            <option value="fuchsia">Fuchsia</option>
                                            <option value="amber">Amber</option>
                                            <option value="rose">Rose</option>
                                        </select>
                                    </div>
                                </div>

                                <div className="flex-1 flex flex-col min-h-[150px]">
                                    <label className="block text-[10px] uppercase tracking-widest text-slate-500 font-bold mb-2">System Prompt</label>
                                    <textarea
                                        value={createAgentPrompt} onChange={e => setCreateAgentPrompt(e.target.value)}
                                        placeholder="You are a helpful coding assistant..."
                                        className="w-full flex-1 bg-slate-950/80 border border-slate-800 rounded-lg px-4 py-3 text-sm font-mono text-fuchsia-300 focus:outline-none focus:border-fuchsia-500/50 resize-none leading-relaxed"
                                    />
                                </div>
                            </div>

                            <footer className="px-6 py-4 bg-slate-950/50 border-t border-slate-800/60 flex justify-end gap-3 shrink-0">
                                <button onClick={() => setIsCreateModalOpen(false)} className="px-4 py-2 text-sm font-medium text-slate-300 hover:text-white transition-colors">Cancel</button>
                                <button onClick={async () => {
                                    try {
                                        const res = await fetch('/api/agents', {
                                            method: 'POST',
                                            headers: { 'Content-Type': 'application/json' },
                                            body: JSON.stringify({
                                                name: createAgentName,
                                                role: createAgentRole,
                                                model: provider,
                                                color: createAgentColor,
                                                prompt: createAgentPrompt,
                                                initial: createAgentName.charAt(0).toUpperCase()
                                            })
                                        });
                                        if (res.ok) {
                                            const data = await res.json();
                                            setIsCreateModalOpen(false);
                                            setCreateAgentName('');
                                            setCreateAgentRole('');
                                            setCreateAgentPrompt('');
                                            setSelectedAgentId(data.agent.id);
                                            onRefresh();
                                        } else {
                                            alert('Failed to save agent');
                                        }
                                    } catch (e: any) { alert(e.message); }
                                }} className="px-5 py-2 bg-fuchsia-600 hover:bg-fuchsia-500 text-white rounded-lg text-sm font-medium transition-colors shadow-lg shadow-fuchsia-900/20">Save Agent</button>
                            </footer>
                        </div>
                    </div>
                )
            }

            {/* Add Skill Modal Overlay */}
            {
                isAddSkillModalOpen && (
                    <div className="absolute inset-0 z-50 flex items-center justify-center p-10 fade-in">
                        <div className="absolute inset-0 bg-slate-950/80 backdrop-blur-md" onClick={() => setIsAddSkillModalOpen(false)} />
                        <div className="bg-slate-900/90 border border-cyan-500/30 rounded-2xl shadow-[0_0_50px_rgba(6,182,212,0.1)] w-full max-w-md relative z-10 overflow-hidden flex flex-col">
                            <header className="px-6 py-4 border-b border-slate-800/60 flex items-center justify-between">
                                <h3 className="text-lg font-bold text-white tracking-tight">Assign Tool</h3>
                                <button onClick={() => setIsAddSkillModalOpen(false)} className="p-2 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition-colors"><X className="w-5 h-5" /></button>
                            </header>

                            <div className="p-6">
                                <label className="block text-[10px] uppercase tracking-widest text-slate-500 font-bold mb-2">Skill Name</label>
                                {skills.length === 0 ? (
                                    <div className="w-full bg-slate-950/50 border border-slate-800 rounded-lg px-4 py-2.5 text-sm font-mono text-slate-500">
                                        No dynamic skills available to assign.
                                    </div>
                                ) : (
                                    <select
                                        value={skillToAdd}
                                        onChange={e => setSkillToAdd(e.target.value)}
                                        className="w-full bg-slate-950/50 border border-slate-800 rounded-lg px-4 py-2.5 text-sm font-mono text-slate-300 focus:outline-none focus:ring-1 focus:ring-cyan-500/50 appearance-none"
                                    >
                                        {skills.map(skill => (
                                            <option key={skill} value={skill}>{skill}</option>
                                        ))}
                                    </select>
                                )}
                            </div>

                            <footer className="px-6 py-4 bg-slate-950/50 border-t border-slate-800/60 flex justify-end gap-3">
                                <button onClick={() => setIsAddSkillModalOpen(false)} className="px-4 py-2 text-sm font-medium text-slate-300 hover:text-white transition-colors">Cancel</button>
                                <button onClick={async () => {
                                    if (!skillToAdd) return;
                                    try {
                                        const res = await fetch(`/api/agents/${selectedAgent.id}/skills`, {
                                            method: 'POST',
                                            headers: { 'Content-Type': 'application/json' },
                                            body: JSON.stringify({ skill: skillToAdd })
                                        });
                                        if (res.ok) {
                                            setIsAddSkillModalOpen(false);
                                            setSkillToAdd('');
                                            onRefresh();
                                        } else {
                                            const err = await res.json();
                                            alert(`Failed to assign skill: ${err.error}`);
                                        }
                                    } catch (e: any) { alert(e.message); }
                                }} className="px-5 py-2 bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg text-sm font-medium transition-colors">Assign</button>
                            </footer>
                        </div>
                    </div>
                )
            }
        </div >
    );
}

interface SkillsViewProps {
    skills: string[];
    onRefresh: () => Promise<void> | void;
    isGenerating: boolean;
    setIsGenerating: (generating: boolean) => void;
}

function SkillsView({ skills, onRefresh, isGenerating, setIsGenerating }: SkillsViewProps) {
    const [isAddModalOpen, setIsAddModalOpen] = useState(false);
    const [skillName, setSkillName] = useState('');
    const [skillDesc, setSkillDesc] = useState('');
    const [skillInstruct, setSkillInstruct] = useState('');
    const [skillToDelete, setSkillToDelete] = useState<string | null>(null);

    const [detailsModalSkill, setDetailsModalSkill] = useState<{ name: string, content: string } | null>(null);
    const [isFetchingDetails, setIsFetchingDetails] = useState(false);

    const handleViewDetails = async (name: string) => {
        setIsFetchingDetails(true);
        try {
            if (name === 'web_search') {
                setDetailsModalSkill({ name, content: "# Built-in System Skill\n\nThis skill is natively provided by the OpenSpider runtime and proxy-forwards search queries to an external provider." });
                return;
            }

            const res = await fetch(`/api/skills/${name}`);
            const data = await res.json();
            if (data.content) {
                setDetailsModalSkill({ name, content: data.content });
            } else {
                alert(`Error: ${data.error || 'Failed to fetch'}`);
            }
        } catch (e: any) {
            alert(`Error: ${e.message}`);
        } finally {
            setIsFetchingDetails(false);
        }
    };

    const handleSaveSkill = async () => {
        if (!skillName || !skillInstruct) return alert('Name and instructions are required');

        // Optimistic UI update: Close modal immediately, don't trap the user
        setIsAddModalOpen(false);
        setSkillName('');
        setSkillDesc('');
        setSkillInstruct('');
        setIsGenerating(true);

        try {
            const res = await fetch('/api/skills/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name: skillName, description: skillDesc, instructions: skillInstruct })
            });
            const data = await res.json();
            if (!data.success) {
                alert(`Error: ${data.error}`);
            }
        } catch (e: any) {
            alert(`Error: ${e.message}`);
        } finally {
            await onRefresh(); // Explicitly await refresh so UI re-renders BEFORE dropping banner
            setIsGenerating(false);
        }
    };

    const handleDeleteSkill = (e: React.MouseEvent, name: string) => {
        e.stopPropagation();
        setSkillToDelete(name);
    };

    const confirmDeleteSkill = async () => {
        if (!skillToDelete) return;
        try {
            const res = await fetch(`/api/skills/${skillToDelete}`, { method: 'DELETE' });
            const data = await res.json();
            if (data.success) {
                setSkillToDelete(null);
                onRefresh();
            } else {
                alert(`Error deleting skill: ${data.error}`);
            }
        } catch (e: any) {
            alert(`Error: ${e.message}`);
        }
    };

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

                {/* Show a global loading indicator if background generation is happening */}
                {isGenerating && (
                    <div className="mb-6 bg-cyan-900/30 border border-cyan-800/50 rounded-xl p-4 flex items-center gap-4 animate-pulse">
                        <div className="w-8 h-8 rounded-full bg-cyan-500/20 flex items-center justify-center">
                            <Bot className="w-4 h-4 text-cyan-400 animate-bounce" />
                        </div>
                        <div>
                            <h4 className="text-sm font-medium text-cyan-200">Generating Skill Script...</h4>
                            <p className="text-xs text-cyan-400/70">The LLM is writing complex Python execution code. This can take up to 30 seconds.</p>
                        </div>
                    </div>
                )}

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 flex-1 min-h-0 overflow-y-auto pb-10">
                    {skills.map(skillName => (
                        <div key={skillName} className="bg-slate-900/40 backdrop-blur-xl rounded-2xl border border-white/5 p-6 shadow-xl relative overflow-hidden group hover:bg-slate-900/60 transition-all">
                            <div className="absolute top-0 inset-x-0 h-px w-full bg-gradient-to-r from-transparent via-cyan-500/30 to-transparent"></div>
                            <div className="flex items-center gap-3 mb-4">
                                <div className="p-2.5 rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                                    <Terminal className="w-5 h-5" />
                                </div>
                                <h3 className="text-lg font-semibold text-white tracking-tight">{skillName}</h3>
                            </div>
                            <p className="text-sm text-slate-400 mb-6 line-clamp-2">Dynamically loaded system tool.</p>

                            <div className="flex items-center justify-between mt-auto">
                                <span className="text-[10px] uppercase tracking-widest text-slate-500 font-bold bg-slate-950/50 px-2.5 py-1 rounded border border-slate-800/60">Local File</span>
                                <div className="flex items-center gap-3">
                                    <button className="text-xs font-semibold text-rose-400 hover:text-rose-300 transition-colors" onClick={(e) => handleDeleteSkill(e, skillName)}>
                                        Delete
                                    </button>
                                    <button className="text-xs font-semibold text-slate-400 hover:text-cyan-400 transition-colors" onClick={() => handleViewDetails(skillName)}>
                                        {isFetchingDetails ? '...' : 'Details'}
                                    </button>
                                </div>
                            </div>
                        </div>
                    ))}

                    {/* Add built-in core skills as well */}
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
                            <button className="text-xs font-semibold text-slate-400 hover:text-cyan-400 transition-colors" onClick={() => handleViewDetails('web_search')}>Details</button>
                        </div>
                    </div>
                </div>
            </div>

            {/* Skill Details Modal Overlay */}
            {detailsModalSkill && (
                <div className="absolute inset-0 z-50 flex items-center justify-center p-10 fade-in">
                    <div
                        className="absolute inset-0 bg-slate-950/80 backdrop-blur-md"
                        onClick={() => setDetailsModalSkill(null)}
                    />
                    <div className="bg-slate-900/90 border border-cyan-500/30 rounded-2xl shadow-[0_0_50px_rgba(6,182,212,0.1)] w-full max-w-4xl relative z-10 overflow-hidden flex flex-col max-h-[85vh]">
                        <div className="absolute top-0 inset-x-0 h-1 w-full bg-gradient-to-r from-cyan-500 to-blue-500"></div>
                        <header className="px-6 py-5 border-b border-slate-800/60 flex items-center justify-between shrink-0">
                            <div className="flex items-center gap-3">
                                <div className="p-2 rounded-lg bg-cyan-500/20 text-cyan-400">
                                    <Terminal className="w-5 h-5" />
                                </div>
                                <div>
                                    <h3 className="text-lg font-bold text-white tracking-tight">{detailsModalSkill.name}</h3>
                                    <p className="text-xs text-slate-400">Local Tool Execution Script</p>
                                </div>
                            </div>
                            <button
                                onClick={() => setDetailsModalSkill(null)}
                                className="p-2 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition-colors"
                            >
                                <X className="w-5 h-5" />
                            </button>
                        </header>
                        <div className="p-6 overflow-y-auto flex-1 bg-[#0d1117]">
                            <pre className="font-mono text-xs text-slate-300 leading-relaxed overflow-x-auto">
                                <code>{detailsModalSkill.content}</code>
                            </pre>
                        </div>
                        <footer className="px-6 py-4 bg-slate-950/50 border-t border-slate-800/60 flex justify-end shrink-0">
                            <button
                                onClick={() => setDetailsModalSkill(null)}
                                className="px-5 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-lg text-sm font-medium transition-colors"
                            >
                                Close
                            </button>
                        </footer>
                    </div>
                </div>
            )}

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
                                <input type="text" value={skillName} onChange={e => setSkillName(e.target.value)} placeholder="e.g. format_date" className="w-full bg-slate-950/50 border border-slate-800 rounded-lg px-4 py-2.5 text-sm font-mono text-slate-300 focus:outline-none focus:ring-1 focus:ring-cyan-500/50" />
                            </div>

                            <div>
                                <label className="block text-[10px] uppercase tracking-widest text-slate-500 font-bold mb-2">Description</label>
                                <input type="text" value={skillDesc} onChange={e => setSkillDesc(e.target.value)} placeholder="Explains what this tool does to the LLM" className="w-full bg-slate-950/50 border border-slate-800 rounded-lg px-4 py-2.5 text-sm text-slate-300 focus:outline-none focus:ring-1 focus:ring-cyan-500/50" />
                            </div>

                            <div className="flex-1 flex flex-col min-h-[200px]">
                                <div className="flex items-center justify-between mb-2">
                                    <label className="block text-[10px] uppercase tracking-widest text-slate-500 font-bold">Natural Language Instructions</label>
                                    <span className="text-[10px] font-mono text-slate-500 bg-slate-800 px-2 py-0.5 rounded">AI Assisted</span>
                                </div>
                                <textarea
                                    value={skillInstruct} onChange={e => setSkillInstruct(e.target.value)}
                                    placeholder="Describe exactly what this skill should do in plain English..."
                                    className="w-full flex-1 bg-slate-950/80 border border-slate-800 rounded-lg px-4 py-3 text-sm font-mono text-cyan-300 focus:outline-none focus:border-cyan-500/50 resize-none leading-relaxed"
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
                            <button onClick={handleSaveSkill} disabled={isGenerating} className={`px-5 py-2 hover:bg-cyan-500 text-white rounded-lg text-sm font-medium transition-colors shadow-lg shadow-cyan-900/20 ${isGenerating ? 'bg-cyan-800 cursor-not-allowed' : 'bg-cyan-600'}`}>
                                {isGenerating ? 'Generating...' : 'Save Skill'}
                            </button>
                        </footer>
                    </div>
                </div>
            )}

            {/* Delete Confirmation Modal */}
            {skillToDelete && (
                <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex items-center justify-center p-4 fade-in" onClick={() => setSkillToDelete(null)}>
                    <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-md shadow-2xl overflow-hidden flex flex-col scale-in" onClick={e => e.stopPropagation()}>
                        <header className="px-6 py-4 border-b border-slate-800/60 flex items-center gap-3 bg-red-950/20">
                            <div className="p-2 rounded-lg bg-red-500/10 text-red-500 border border-red-500/20">
                                <Trash className="w-5 h-5" />
                            </div>
                            <h3 className="text-lg font-bold text-white">Delete Skill</h3>
                        </header>
                        <div className="p-6">
                            <p className="text-slate-300 leading-relaxed">Are you sure you want to permanently delete the custom tool <span className="text-white font-semibold">"{skillToDelete}"</span>?</p>
                            <p className="text-sm text-slate-500 mt-3 bg-black/20 p-3 rounded-lg border border-white/5">This action cannot be undone and will remove both the execution script and its capabilities metadata.</p>
                        </div>
                        <footer className="px-6 py-4 bg-slate-900 border-t border-slate-800 flex justify-end gap-3">
                            <button
                                onClick={() => setSkillToDelete(null)}
                                className="px-4 py-2 text-sm font-medium text-slate-300 hover:text-white bg-slate-800 hover:bg-slate-700 rounded-lg transition-colors border border-slate-700"
                            >
                                Cancel
                            </button>
                            <button
                                onClick={confirmDeleteSkill}
                                className="px-4 py-2 bg-red-600 hover:bg-red-500 text-white rounded-lg text-sm font-medium transition-colors shadow-lg shadow-red-900/20"
                            >
                                Delete {skillToDelete}
                            </button>
                        </footer>
                    </div>
                </div>
            )}
        </div>
    );
}

function LogsView({ logs }: { logs: LogMessage[] }) {
    const endOfLogsRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        endOfLogsRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [logs]);

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
                            <span className="text-slate-500 mr-4 select-none">{safeFormatTime(l.timestamp)}</span>
                            <span className={
                                l.data.includes('Error') || l.data.includes('Failed') ? 'text-red-400' :
                                    l.data.includes('Usage') ? 'text-blue-400' :
                                        l.data.includes('Worker') ? 'text-fuchsia-400' : 'text-slate-300'
                            }>
                                {l.data}
                            </span>
                        </div>
                    ))}
                    <div ref={endOfLogsRef} />
                </div>
            </div>
        </div>
    );
}

function CronView({ agents }: { agents: any[] }) {
    const [jobs, setJobs] = useState<any[]>([]);
    const [showModal, setShowModal] = useState(false);
    const [formData, setFormData] = useState({ description: '', prompt: '', intervalHours: '24', agentId: 'gateway', status: 'enabled' });

    useEffect(() => {
        fetchJobs();
    }, []);

    const fetchJobs = async () => {
        try {
            const res = await fetch('/api/cron');
            const data = await res.json();
            setJobs(data);
        } catch (e) {
            console.error("Failed to fetch cron jobs", e);
        }
    };

    const handleDelete = async (id: string) => {
        try {
            await fetch(`/api/cron/${id}`, { method: 'DELETE' });
            fetchJobs();
        } catch (e) { }
    };

    const toggleStatus = async (job: any) => {
        try {
            const newStatus = job.status === 'enabled' ? 'disabled' : 'enabled';
            await fetch(`/api/cron/${job.id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ status: newStatus })
            });
            fetchJobs();
        } catch (e) { }
    };

    const handleRunForcefully = async (id: string) => {
        try {
            await fetch(`/api/cron/${id}/run`, { method: 'POST' });
            // We just optimistically refetch to update the last run time
            setTimeout(fetchJobs, 1000);
        } catch (e) { }
    };

    const handleCreate = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            await fetch('/api/cron', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });
            setShowModal(false);
            setFormData({ description: '', prompt: '', intervalHours: '24', agentId: 'gateway', status: 'enabled' });
            fetchJobs();
        } catch (e) { }
    };

    const formatTimeDelta = (ms: number) => {
        if (ms < 0) return 'n/a';
        const hours = Math.floor(ms / (1000 * 60 * 60));
        const days = Math.floor(hours / 24);
        if (days > 0) return `${days}d`;
        if (hours > 0) return `${hours}h`;
        const mins = Math.floor(ms / (1000 * 60));
        return `${mins}m`;
    };

    return (
        <div className="flex-1 p-10 overflow-y-auto fade-in">
            <div className="max-w-5xl mx-auto">
                <header className="mb-10 flex justify-between items-center">
                    <div>
                        <h2 className="text-3xl font-bold text-white tracking-tight flex items-center gap-3">
                            <Clock className="w-8 h-8 text-rose-500" />
                            Autonomous Cron Jobs
                        </h2>
                        <p className="text-slate-400 mt-2 text-sm max-w-2xl leading-relaxed">
                            Deploy tasks that wake up OpenSpider agents at scheduled intervals. Keep your system running 24/7.
                        </p>
                    </div>
                    <button
                        onClick={() => setShowModal(true)}
                        className="flex items-center gap-2 px-5 py-2.5 bg-rose-600 hover:bg-rose-500 text-white rounded-xl text-sm font-semibold transition-all shadow-[0_0_20px_rgba(225,29,72,0.3)] hover:shadow-[0_0_30px_rgba(225,29,72,0.5)] border border-rose-500/50"
                    >
                        <Plus className="w-4 h-4" />
                        Deploy Job
                    </button>
                </header>

                <div className="space-y-4">
                    {jobs.length === 0 ? (
                        <div className="bg-slate-900/40 backdrop-blur-xl rounded-2xl border border-white/5 p-10 text-center text-slate-500 shadow-xl">
                            No autonomous jobs currently running.
                        </div>
                    ) : jobs.map((job: any) => {
                        const isEnabled = job.status !== 'disabled';
                        const neverRun = job.lastRunTimestamp === 0;

                        const intervalMs = job.intervalHours * 60 * 60 * 1000;
                        const timeSinceLast = Date.now() - job.lastRunTimestamp;
                        const timeUntilNext = intervalMs - timeSinceLast;

                        return (
                            <div key={job.id} className="bg-slate-900/60 backdrop-blur-xl rounded-2xl border border-white/5 p-6 flex flex-col gap-4 shadow-xl hover:bg-slate-900/80 transition-all">

                                {/* Header Details */}
                                <div className="flex justify-between items-start">
                                    <div>
                                        <h3 className="text-xl font-bold text-white tracking-tight mb-1">{job.description}</h3>
                                        <div className="text-xs text-slate-500 font-mono flex gap-2">
                                            <span>Cron Every {job.intervalHours} Hours</span>
                                        </div>
                                    </div>

                                    {/* Execution Metrics (Right Aligned) */}
                                    <div className="text-right text-xs space-y-2">
                                        <div className="flex justify-between gap-6 items-center">
                                            <span className="text-slate-500 font-bold tracking-widest uppercase">Status</span>
                                            {isEnabled ?
                                                <span className="bg-emerald-500/10 text-emerald-400 px-2 py-0.5 rounded-full border border-emerald-500/20 font-mono">ok</span> :
                                                <span className="bg-slate-800 text-slate-400 px-2 py-0.5 rounded-full border border-slate-700 font-mono">n/a</span>
                                            }
                                        </div>
                                        <div className="flex justify-between gap-6 items-center">
                                            <span className="text-slate-500 font-bold tracking-widest uppercase">Next</span>
                                            <span className="text-slate-300 font-mono">{isEnabled ? `in ${formatTimeDelta(timeUntilNext)}` : 'n/a'}</span>
                                        </div>
                                        <div className="flex justify-between gap-6 items-center">
                                            <span className="text-slate-500 font-bold tracking-widest uppercase">Last</span>
                                            <span className="text-slate-400 font-mono">{neverRun ? 'never' : `${formatTimeDelta(timeSinceLast)} ago`}</span>
                                        </div>
                                    </div>
                                </div>

                                {/* Prompt Block */}
                                <div className="mt-2 text-sm text-slate-400 leading-relaxed max-w-3xl">
                                    <span className="text-[10px] uppercase font-bold text-slate-500 tracking-widest block mb-1">Prompt</span>
                                    {job.prompt}
                                </div>

                                {/* Action Bar */}
                                <div className="mt-4 flex justify-between items-center pt-4 border-t border-slate-800/60">
                                    <div className="flex gap-2">
                                        <span className={`px-3 py-1 text-[11px] uppercase tracking-widest font-bold rounded-full border ${isEnabled ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : 'bg-slate-800 text-slate-500 border-slate-700'
                                            }`}>
                                            {isEnabled ? 'enabled' : 'disabled'}
                                        </span>
                                        <span className="px-3 py-1 bg-slate-800/50 text-slate-400 text-[11px] uppercase tracking-widest font-bold rounded-full border border-slate-700/50">
                                            {job.agentId}
                                        </span>
                                    </div>
                                    <div className="flex gap-2">
                                        <button className="px-4 py-1.5 text-xs font-semibold text-slate-300 hover:text-white bg-slate-800/50 hover:bg-slate-700 rounded-lg border border-slate-700 transition-colors">Clone</button>
                                        <button onClick={() => toggleStatus(job)} className="px-4 py-1.5 text-xs font-semibold text-slate-300 hover:text-white bg-slate-800/50 hover:bg-slate-700 rounded-lg border border-slate-700 transition-colors">{isEnabled ? 'Disable' : 'Enable'}</button>
                                        <button onClick={() => handleRunForcefully(job.id)} className="px-4 py-1.5 text-xs font-semibold text-slate-300 hover:text-white bg-slate-800/50 hover:bg-slate-700 rounded-lg border border-slate-700 transition-colors">Run</button>
                                        <button onClick={() => handleDelete(job.id)} className="px-4 py-1.5 text-xs font-semibold text-red-400 hover:text-white hover:bg-red-500/80 bg-red-500/10 rounded-lg border border-red-500/20 transition-colors">Remove</button>
                                    </div>
                                </div>
                            </div>
                        );
                    })}
                </div>
            </div>

            {/* Create Job Modal */}
            {showModal && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm fade-in">
                    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 w-full max-w-xl shadow-2xl relative overflow-hidden">
                        <div className="absolute top-0 inset-x-0 h-px w-full bg-gradient-to-r from-transparent via-rose-500/50 to-transparent"></div>
                        <div className="flex justify-between items-center mb-6">
                            <h3 className="text-xl font-bold text-white flex items-center gap-2">
                                <Clock className="w-5 h-5 text-rose-500" />
                                Deploy Autonomous Job
                            </h3>
                            <button onClick={() => setShowModal(false)} className="text-slate-500 hover:text-white transition-colors">
                                <X className="w-5 h-5" />
                            </button>
                        </div>
                        <form onSubmit={handleCreate} className="space-y-4">
                            <div>
                                <label className="block text-[10px] uppercase tracking-widest text-slate-500 font-bold mb-2">Internal Description</label>
                                <input required type="text" value={formData.description} onChange={e => setFormData({ ...formData, description: e.target.value })} placeholder="e.g. Daily Hackernews Digest" className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-sm text-slate-200 focus:ring-1 focus:ring-rose-500 focus:border-rose-500 outline-none" />
                            </div>
                            <div>
                                <label className="block text-[10px] uppercase tracking-widest text-slate-500 font-bold mb-2">Assigned Agent</label>
                                <select value={formData.agentId} onChange={e => setFormData({ ...formData, agentId: e.target.value })} className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-sm text-slate-200 focus:ring-1 focus:ring-rose-500 focus:border-rose-500 outline-none">
                                    <option value="gateway">Gateway Architect (Default Routing)</option>
                                    {agents.map(a => <option key={a.id} value={a.id}>{a.name}</option>)}
                                </select>
                            </div>
                            <div>
                                <label className="block text-[10px] uppercase tracking-widest text-slate-500 font-bold mb-2">Interval (Hours)</label>
                                <input required type="number" min="1" max="8760" value={formData.intervalHours} onChange={e => setFormData({ ...formData, intervalHours: e.target.value })} className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-sm text-slate-200 focus:ring-1 focus:ring-rose-500 focus:border-rose-500 outline-none" />
                            </div>
                            <div>
                                <label className="block text-[10px] uppercase tracking-widest text-slate-500 font-bold mb-2">Task Prompt</label>
                                <textarea required rows={4} value={formData.prompt} onChange={e => setFormData({ ...formData, prompt: e.target.value })} placeholder="Agent instructions..." className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-sm text-slate-200 focus:ring-1 focus:ring-rose-500 focus:border-rose-500 outline-none resize-none" />
                            </div>
                            <div className="pt-4 flex justify-end gap-3">
                                <button type="button" onClick={() => setShowModal(false)} className="px-4 py-2 border border-slate-700 text-slate-300 rounded-lg text-sm hover:bg-slate-800 transition-colors">Cancel</button>
                                <button type="submit" className="px-5 py-2 bg-rose-600 hover:bg-rose-500 text-white rounded-lg text-sm font-semibold transition-colors">Deploy Job</button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
}

const funnyStatuses = [
    "Searching the web for answers...",
    "Talking to a friend...",
    "Consulting the ancient scrolls...",
    "Doing highly complex math...",
    "Asking a rubber duck...",
    "Reticulating splines...",
    "Herding cats...",
    "Downloading more RAM...",
    "Brewing digital coffee..."
];

export default function App() {
    type TabName = 'overview' | 'channels' | 'sessions' | 'usage' | 'chat' | 'agents' | 'skills' | 'logs' | 'flow' | 'cron' | 'processes';
    const [activeTab, setActiveTab] = useState<TabName>('chat');
    const [configuredChannel, setConfiguredChannel] = useState<string | null>(null);
    const [logs, setLogs] = useState<LogMessage[]>([]);
    const [flowEvents, setFlowEvents] = useState<AgentFlowEvent[]>([]);
    const [config, setConfig] = useState({ provider: 'Loading...', status: 'connecting' });
    const [skills, setSkills] = useState<string[]>([]);
    const [agents, setAgents] = useState<any[]>([]);
    const [alerts, setAlerts] = useState<{ id: number, message: string }[]>([]);
    const [chatInput, setChatInput] = useState('');
    const [isTyping, setIsTyping] = useState(false);
    const [isVerbose, setIsVerbose] = useState(false);
    const scrollRef = useRef<HTMLDivElement>(null);
    const chatEndRef = useRef<HTMLDivElement>(null);
    const wsRef = useRef<WebSocket | null>(null);

    const [loadingStatus, setLoadingStatus] = useState(funnyStatuses[0]);

    // Randomize checking status every 2 seconds if generating
    useEffect(() => {
        let interval: any;
        if (isTyping) {
            interval = setInterval(() => {
                setLoadingStatus(funnyStatuses[Math.floor(Math.random() * funnyStatuses.length)]);
            }, 2000);
        } else {
            setLoadingStatus(funnyStatuses[0]);
        }
        return () => clearInterval(interval);
    }, [isTyping]);

    useEffect(() => {
        if (activeTab === 'chat') {
            chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
        }
    }, [logs, activeTab, isVerbose]);

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

        fetch('/api/chat/history')
            .then(r => r.json())
            .then(data => {
                if (Array.isArray(data) && data.length > 0) {
                    // Prepend history safely to avoid wiping out websocket events that arrived during the fetch
                    setLogs(prev => {
                        const existingIds = new Set(prev.map(p => p.timestamp + p.data));
                        const uniqueHistory = data.filter(d => !existingIds.has(d.timestamp + d.data));
                        return [...uniqueHistory, ...prev].slice(-5000); // Allow preserving up to 5000 history items
                    });
                }
            })
            .catch(e => console.error("Could not fetch chat history", e));

        fetchAgents();

        // Connect WebSocket for live logs
        const host = window.location.port === '5173' ? 'localhost:4001' : window.location.host;
        const wsUrl = window.location.protocol === 'https:'
            ? `wss://${host}`
            : `ws://${host}`;
        const ws = new WebSocket(wsUrl);

        ws.onmessage = (event) => {
            try {
                const msg = JSON.parse(event.data);
                if (msg.type === 'log') {
                    if (msg.data.includes('Emulating human typing delay') || msg.data.includes('Sending structured request')) {
                        // We can also trigger typing state here for internal logs if we want
                        if (msg.data.includes('Sending structured request')) setIsTyping(true);
                        return;
                    }

                    if (msg.data.includes('[You]')) setIsTyping(true);
                    if (msg.data.includes('[Agent]')) setIsTyping(false);

                    setLogs(prev => [...prev.slice(-49999), msg]); // Keep last 50000 logs to prevent chat eviction
                } else if (msg.type === 'chat_response') {
                    setLogs(prev => [...prev.slice(-49999), { type: 'chat', data: `[Agent] ${msg.data}`, timestamp: msg.timestamp }]);
                    setIsTyping(false);
                } else if (msg.type === 'usage') {
                    const u = msg.data.usage;
                    setLogs(prev => [...prev.slice(-49999), { type: 'usage', data: `[API Token Usage] Model: ${msg.data.model} | In: ${u.promptTokens} | Out: ${u.completionTokens} | Total: ${u.totalTokens}`, timestamp: msg.timestamp }]);
                } else if (msg.type === 'agent_flow') {
                    if (msg.data.event === 'plan_generated') setFlowEvents([]); // Reset on new plan
                    setFlowEvents(prev => [...prev, msg.data]);
                } else if (msg.type === 'alert') {
                    const alertId = Date.now();
                    setAlerts(prev => [...prev, { id: alertId, message: msg.data }]);

                    // Auto-dismiss alert after 6 seconds
                    setTimeout(() => {
                        setAlerts(prev => prev.filter(a => a.id !== alertId));
                    }, 6000);
                }
            } catch (e) { }
        };

        ws.onopen = () => setConfig(prev => ({ ...prev, status: 'connected' }));
        ws.onclose = () => setConfig(prev => ({ ...prev, status: 'disconnected' }));

        wsRef.current = ws;

        return () => ws.close();
    }, []);

    const fetchAgents = async () => {
        try {
            const res = await fetch('/api/agents');
            const data = await res.json();
            setAgents(data);
        } catch (e) {
            console.error("Could not fetch agents", e);
        }
    };

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

    const [isGenerating, setIsGenerating] = useState(false);

    // Auto-scroll logs
    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [logs, isTyping]);

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
                        <button
                            onClick={() => setActiveTab('cron')}
                            className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 ${activeTab === 'cron' ? 'bg-rose-600/10 text-rose-400 ring-1 ring-rose-500/30 shadow-[0_4px_20px_-4px_rgba(225,29,72,0.2)]' : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'}`}
                        >
                            <Timer className="w-4 h-4" />
                            Cron Jobs
                        </button>
                        <button
                            onClick={() => setActiveTab('usage')}
                            className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 ${activeTab === 'usage' ? 'bg-indigo-600/10 text-indigo-400 ring-1 ring-indigo-500/30 shadow-[0_4px_20px_-4px_rgba(99,102,241,0.2)]' : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'}`}
                        >
                            <Activity className="w-4 h-4" />
                            Usage
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
                            onClick={() => setActiveTab('flow')}
                            className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 ${activeTab === 'flow' ? 'bg-indigo-600/10 text-indigo-400 ring-1 ring-indigo-500/30 shadow-[0_4px_20px_-4px_rgba(99,102,241,0.2)]' : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'}`}
                        >
                            <GitMerge className="w-4 h-4" />
                            Agent Flow
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
                            onClick={() => setActiveTab('processes')}
                            className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 ${activeTab === 'processes' ? 'bg-indigo-600/20 text-indigo-400 ring-1 ring-indigo-500/30 shadow-[0_4px_20px_-4px_rgba(99,102,241,0.2)]' : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'}`}
                        >
                            <Activity className="w-4 h-4" />
                            Process Monitor
                        </button>
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
                        <section className="flex-1 flex flex-col bg-slate-900/50 rounded-xl border border-slate-800/60 overflow-hidden shadow-lg backdrop-blur-sm">
                            <div className="p-4 border-b border-slate-800/60 flex items-center justify-between bg-slate-900">
                                <div className="flex items-center gap-2">
                                    <Terminal className="w-5 h-5 text-slate-400" />
                                    <h2 className="font-semibold text-slate-200">Live Agent Communications</h2>
                                </div>
                                <button
                                    onClick={() => setIsVerbose(!isVerbose)}
                                    className={`px-3 py-1.5 text-xs font-bold uppercase tracking-widest rounded-lg transition-colors border ${isVerbose
                                        ? 'bg-fuchsia-500/10 text-fuchsia-400 hover:bg-fuchsia-500/20 border-fuchsia-500/30 shadow-[0_0_15px_rgba(217,70,239,0.15)]'
                                        : 'bg-slate-800 hover:bg-slate-700 text-slate-400 border-slate-700'
                                        }`}
                                >
                                    Verbose: {isVerbose ? 'ON' : 'OFF'}
                                </button>
                            </div>
                            <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 font-mono text-sm space-y-2">
                                {logs.length === 0 ? (
                                    <div className="text-slate-500 flex flex-col items-center justify-center h-full opacity-60">
                                        <Activity className="w-12 h-12 mb-4 animate-pulse" />
                                        <span>Awaiting agent activity or chat messages...</span>
                                    </div>
                                ) : logs.filter(log => {
                                    if (isVerbose) return true;
                                    const text = log.data.trim(); // MUST Be trimmed so \n doesn't break startsWith!
                                    // In non-verbose mode, strictly only show User questions and final Agent answers
                                    if (text.includes('[You]')) return true;

                                    if (text.includes('[Agent]')) {
                                        // Filter out intermediate [Agent] system/status updates
                                        if (text.includes('OpenSpider is processing')) return false;
                                        if (text.includes('Sending structured request')) return false;
                                        return true; // Keep genuine [Agent] dialogue responses
                                    }

                                    // Hide absolutely everything else (raw JSON, [Server], [Web Chat], [Manager], [Worker])
                                    return false;
                                }).map((log, i) => {
                                    const text = log.data.trim();
                                    const isUser = text.includes('[You]');
                                    const isAgent = text.includes('[Agent]');
                                    const isSystem = !isUser && !isAgent;

                                    // Strip the prefixes
                                    let content = text;
                                    if (isUser) {
                                        content = content.substring(content.indexOf('[You]') + 5).trim();
                                    } else if (isAgent) {
                                        content = content.substring(content.indexOf('[Agent]') + 7).trim();
                                        content = content.replace(/Plan execution finished successfully\. Final Output:?[\s\n]*/g, '').trim();
                                    }

                                    return (
                                        <div key={i} className={`flex w-full mb-6 ${isUser ? 'justify-end' : 'justify-start'}`}>
                                            <div className={`max-w-[85%] sm:max-w-[75%] rounded-2xl px-5 py-3.5 shadow-md relative group ${isUser
                                                ? 'bg-gradient-to-br from-blue-500 to-blue-600 text-white rounded-br-sm shadow-blue-900/20'
                                                : isAgent
                                                    ? 'bg-slate-800/90 backdrop-blur-md border border-slate-700/50 text-slate-200 rounded-bl-sm shadow-slate-900/50'
                                                    : 'bg-slate-900/50 border border-slate-800 text-slate-400 rounded-xl font-mono text-[11px] p-2'
                                                }`}>
                                                <span className={`absolute -bottom-5 text-[10px] text-slate-500 opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap ${isUser ? 'right-2' : 'left-2'}`}>
                                                    {safeFormatTimestamp(log.timestamp)}
                                                </span>

                                                {isSystem ? (
                                                    <span className="whitespace-pre-wrap opacity-80">{content}</span>
                                                ) : isUser ? (
                                                    <span className="whitespace-pre-wrap font-medium text-[15px] leading-relaxed">{content}</span>
                                                ) : (
                                                    <div className="flex flex-col gap-1">
                                                        <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1 pt-1 ml-1 opacity-70">
                                                            {agents.length > 0 ? agents[0].name : 'OpenSpider'}
                                                        </span>
                                                        <div className="prose prose-invert prose-sm max-w-none prose-p:leading-relaxed prose-pre:bg-slate-950/80 prose-pre:border prose-pre:border-slate-800 prose-pre:shadow-inner text-[14.5px]">
                                                            <ReactMarkdown
                                                                remarkPlugins={[remarkGfm]}
                                                                components={{
                                                                    table: ({ node, ...props }) => (
                                                                        <div className="overflow-x-auto my-4 rounded-xl border border-slate-700/50 bg-slate-900/50 shadow-lg">
                                                                            <table className="min-w-full divide-y divide-slate-700/50 text-sm" {...props} />
                                                                        </div>
                                                                    ),
                                                                    thead: ({ node, ...props }) => <thead className="bg-slate-800/90" {...props} />,
                                                                    th: ({ node, ...props }) => <th className="px-4 py-3 text-left font-semibold text-slate-200 tracking-wide bg-slate-800/80 first:rounded-tl-lg last:rounded-tr-lg" {...props} />,
                                                                    td: ({ node, ...props }) => <td className="px-4 py-3 border-t border-slate-700/50 text-slate-300 group-hover/row:bg-slate-800/50 transition-colors" {...props} />,
                                                                    tr: ({ node, ...props }) => <tr className="group/row" {...props} />,
                                                                    p: ({ node, ...props }) => <p className="mb-2.5 last:mb-0" {...props} />,
                                                                    code: ({ node, inline, ...props }: any) => inline
                                                                        ? <code className="bg-slate-900/60 text-indigo-300 px-1.5 py-0.5 rounded text-[13px] border border-slate-700/40" {...props} />
                                                                        : <code {...props} />,
                                                                    a: ({ node, ...props }) => <a className="text-blue-400 hover:text-blue-300 underline underline-offset-2 decoration-blue-500/30 hover:decoration-blue-400 transition-all font-medium" {...props} />
                                                                }}
                                                            >
                                                                {content}
                                                            </ReactMarkdown>
                                                        </div>
                                                    </div>
                                                )}
                                            </div>
                                        </div>
                                    );
                                })}

                                {isTyping && !isVerbose && (
                                    <div className="flex w-full mb-6 justify-start">
                                        <div className="bg-slate-800/90 backdrop-blur-md border border-slate-700/50 rounded-2xl rounded-bl-sm px-5 py-3.5 shadow-md flex flex-col gap-1.5">
                                            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider pt-0.5 ml-1 opacity-70">
                                                {agents.length > 0 ? agents[0].name : 'OpenSpider'}
                                            </span>
                                            <div className="flex items-center gap-3 ml-1 mb-1">
                                                <div className="flex gap-1.5 items-center justify-center">
                                                    <div className="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                                                    <div className="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                                                    <div className="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                                                </div>
                                                <span className="text-sm text-indigo-300/80 font-medium italic animate-pulse">
                                                    {loadingStatus}
                                                </span>
                                            </div>
                                        </div>
                                    </div>
                                )}
                                <div ref={chatEndRef} />
                            </div>

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
                )
                }

                {
                    activeTab === 'channels' && (
                        <div className="flex-1 p-10 overflow-y-auto fade-in">
                            <div className="max-w-6xl mx-auto">
                                <header className="mb-10">
                                    <h2 className="text-3xl font-bold text-white tracking-tight">Channels Management</h2>
                                    <p className="text-slate-400 mt-2 text-sm max-w-2xl leading-relaxed">
                                        Configure and monitor external communication vectors for OpenSpider. Channels act as the sensory inputs and outputs for your autonomous agents.
                                    </p>
                                </header>

                                {configuredChannel ? (
                                    <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
                                        <button
                                            onClick={() => setConfiguredChannel(null)}
                                            className="mb-8 px-4 py-2 bg-slate-800/80 hover:bg-slate-700/80 text-slate-300 hover:text-white rounded-xl text-sm font-medium transition-colors flex items-center gap-2 w-fit border border-slate-700/50"
                                        >
                                            &larr; Back to Channels
                                        </button>

                                        {configuredChannel === 'wa' && (
                                            <WhatsAppSecurity isRunning={mockChannels.find(c => c.id === 'wa')?.status === 'running'} />
                                        )}
                                    </div>
                                ) : (
                                    <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6 pb-20">
                                        {mockChannels.map(channel => (
                                            <ChannelCard
                                                key={channel.id}
                                                channel={channel}
                                                onConfigure={() => setConfiguredChannel(channel.id)}
                                            />
                                        ))}
                                    </div>
                                )}
                            </div>
                        </div>
                    )
                }

                {activeTab === 'overview' && <OverviewView />}
                {activeTab === 'sessions' && <SessionsView provider={config.provider} />}
                {
                    activeTab === 'flow' && (
                        <div className="flex-1 p-8 fade-in h-full flex flex-col">
                            <AgentFlowGraph events={flowEvents} />
                        </div>
                    )
                }
                {activeTab === 'agents' && <AgentsView agents={agents} onRefresh={fetchAgents} provider={config.provider} skills={skills} />}
                {
                    activeTab === 'skills' && <SkillsView skills={skills} onRefresh={() => {
                        return fetch('/api/skills')
                            .then(r => r.json())
                            .then(data => setSkills(data.skills))
                            .catch(e => console.error("Could not refresh skills API", e));
                    }} isGenerating={isGenerating} setIsGenerating={setIsGenerating} />
                }
                {activeTab === 'usage' && <UsageView />}
                {activeTab === 'logs' && <LogsView logs={logs} />}
                {activeTab === 'cron' && <CronView agents={agents} />}
                {activeTab === 'processes' && <ProcessMonitor />}
            </main >

            {/* Toasts / Alerts Overlay */}
            < div className="fixed top-6 right-6 z-50 flex flex-col gap-3 pointer-events-none fade-in" >
                {
                    alerts.map(alert => (
                        <div key={alert.id} className="bg-slate-900 border border-red-500/50 rounded-xl shadow-[0_0_30px_rgba(239,68,68,0.2)] p-4 flex items-start gap-4 w-96 max-w-full relative overflow-hidden pointer-events-auto">
                            <div className="absolute top-0 inset-x-0 h-1 bg-gradient-to-r from-red-500 to-rose-500"></div>
                            <div className="p-2 bg-red-500/10 rounded-lg shrink-0 mt-0.5">
                                <AlertTriangle className="w-5 h-5 text-red-500 animate-pulse" />
                            </div>
                            <div className="flex-1 min-w-0">
                                <h4 className="text-sm font-bold text-red-400 mb-1 tracking-tight">System Alert</h4>
                                <p className="text-xs text-slate-300 leading-relaxed drop-shadow-sm">{alert.message}</p>
                            </div>
                            <button onClick={() => setAlerts(prev => prev.filter(a => a.id !== alert.id))} className="text-slate-500 hover:text-white transition-colors">
                                <X className="w-4 h-4" />
                            </button>
                        </div>
                    ))
                }
            </div >

        </div >
    );
}
