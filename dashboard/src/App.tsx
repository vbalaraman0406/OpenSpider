import { useState, useEffect, useRef } from 'react';
import { Activity, Terminal, CheckCircle2, Server, Key, Bot, Send, MessageSquare, Radio, Smartphone, MessagesSquare, Users, Globe, Play, Square, Settings, RefreshCw, LayoutDashboard, ListTree, FolderGit2, Wrench, FileText, FileCode, Search, Download, X, Trash, GitMerge, Timer, Plus, Clock, AlertTriangle, Paperclip, Image as ImageIcon, Sun, Moon, Monitor, Heart, Zap, Workflow } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import AgentFlowGraph, { AgentFlowEvent } from './components/AgentFlowGraph';
import { UsageView } from './components/UsageView';
import { WhatsAppSecurity } from './components/WhatsAppSecurity';
import { VoiceSettings } from './components/VoiceSettings';
import { EmailSettings } from './components/EmailSettings';
import { ProcessMonitor } from './components/ProcessMonitor';

// SECURITY: Authenticated fetch wrapper - attaches the dashboard API key to every request
const API_KEY = import.meta.env.VITE_API_KEY || '';
const apiFetch = (url: string, options: RequestInit = {}): Promise<Response> => {
    const headers = new Headers(options.headers || {});
    headers.set('X-API-Key', API_KEY);
    return fetch(url, { ...options, headers });
};

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
            <div className="w-full">
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
            <div className="w-full">
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
            const res = await apiFetch(`/api/agents/${selectedAgent.id}`, {
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
    const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
    const [isDeleting, setIsDeleting] = useState(false);

    const handleDeleteAgent = async () => {
        setIsDeleting(true);
        try {
            const res = await apiFetch(`/api/agents/${selectedAgent.id}`, { method: 'DELETE' });
            const data = await res.json();
            if (data.success) {
                setIsDeleteModalOpen(false);
                // Select first available agent after deletion
                const remaining = agents.filter(a => a.id !== selectedAgent.id);
                if (remaining.length > 0) setSelectedAgentId(remaining[0].id);
                onRefresh();
            } else {
                alert(`Error: ${data.error}`);
            }
        } catch (e: any) { alert(e.message); }
        finally { setIsDeleting(false); }
    };

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
                                        {(agent as any).emoji ? `${(agent as any).emoji} ${agent.name}` : agent.name}
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
                        <div className={`w-16 h-16 rounded-2xl bg-${selectedAgent.color}-500/20 border border-${selectedAgent.color}-500/30 flex items-center justify-center text-3xl`}>
                            {(selectedAgent as any).emoji || selectedAgent.initial}
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
                        <div className="flex items-center gap-3">
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
                            {selectedAgent.id !== 'manager' && (
                                <button
                                    onClick={() => setIsDeleteModalOpen(true)}
                                    className="px-4 py-2 rounded-lg text-xs font-bold uppercase tracking-widest transition-colors border bg-slate-800/50 text-red-400 hover:bg-red-500/10 border-slate-700 hover:border-red-500/30"
                                >
                                    🗑 Delete Agent
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
                                        const res = await apiFetch('/api/agents', {
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
                                        const res = await apiFetch(`/api/agents/${selectedAgent.id}/skills`, {
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

            {/* Delete Agent Confirmation Modal */}
            {
                isDeleteModalOpen && (
                    <div className="absolute inset-0 z-50 flex items-center justify-center p-10 fade-in">
                        <div className="absolute inset-0 bg-slate-950/80 backdrop-blur-md" onClick={() => setIsDeleteModalOpen(false)} />
                        <div className="bg-slate-900/95 border border-red-500/30 rounded-2xl shadow-[0_0_50px_rgba(239,68,68,0.1)] w-full max-w-lg relative z-10 overflow-hidden flex flex-col">
                            <div className="absolute top-0 inset-x-0 h-1 w-full bg-gradient-to-r from-red-500 to-orange-500" />
                            <header className="px-6 py-5 border-b border-slate-800/60 flex items-center gap-4">
                                <div className="p-2.5 rounded-xl bg-red-500/10 border border-red-500/20">
                                    <AlertTriangle className="w-6 h-6 text-red-400" />
                                </div>
                                <div>
                                    <h3 className="text-lg font-bold text-white tracking-tight">Delete Agent Permanently</h3>
                                    <p className="text-xs text-slate-400 mt-0.5">This action cannot be undone</p>
                                </div>
                            </header>

                            <div className="p-6 space-y-4">
                                <p className="text-sm text-slate-300 leading-relaxed">
                                    You are about to permanently delete <strong className="text-red-400">{selectedAgent.name}</strong> ({selectedAgent.id}). The following data will be <strong className="text-red-400">irreversibly lost</strong>:
                                </p>

                                <div className="space-y-2">
                                    <div className="flex items-start gap-3 bg-red-500/5 border border-red-500/10 rounded-lg p-3">
                                        <span className="text-red-400 mt-0.5">✕</span>
                                        <div>
                                            <div className="text-sm font-semibold text-slate-200">Identity & Soul</div>
                                            <div className="text-xs text-slate-400">IDENTITY.md, SOUL.md — the agent's personality and behavior core</div>
                                        </div>
                                    </div>
                                    <div className="flex items-start gap-3 bg-red-500/5 border border-red-500/10 rounded-lg p-3">
                                        <span className="text-red-400 mt-0.5">✕</span>
                                        <div>
                                            <div className="text-sm font-semibold text-slate-200">User Context & Memory</div>
                                            <div className="text-xs text-slate-400">USER.md — stored user preferences and learned context</div>
                                        </div>
                                    </div>
                                    <div className="flex items-start gap-3 bg-red-500/5 border border-red-500/10 rounded-lg p-3">
                                        <span className="text-red-400 mt-0.5">✕</span>
                                        <div>
                                            <div className="text-sm font-semibold text-slate-200">Capabilities & Skills</div>
                                            <div className="text-xs text-slate-400">CAPABILITIES.json — assigned tools, model config, and role definition</div>
                                        </div>
                                    </div>
                                </div>

                                <div className="bg-amber-500/5 border border-amber-500/20 rounded-lg p-3 flex items-start gap-3">
                                    <span className="text-amber-400 mt-0.5">⚠</span>
                                    <p className="text-xs text-amber-200/80 leading-relaxed">
                                        If other agents reference <strong>{selectedAgent.id}</strong> in their task delegation, those references will break. Make sure no active workflows depend on this agent.
                                    </p>
                                </div>
                            </div>

                            <footer className="px-6 py-4 bg-slate-950/50 border-t border-slate-800/60 flex justify-end gap-3">
                                <button onClick={() => setIsDeleteModalOpen(false)} className="px-5 py-2.5 text-sm font-medium text-slate-300 hover:text-white transition-colors rounded-lg hover:bg-slate-800">
                                    Cancel
                                </button>
                                <button
                                    onClick={handleDeleteAgent}
                                    disabled={isDeleting}
                                    className="px-5 py-2.5 bg-red-600 hover:bg-red-500 disabled:opacity-50 text-white rounded-lg text-sm font-semibold transition-colors shadow-lg shadow-red-900/30 flex items-center gap-2"
                                >
                                    {isDeleting ? 'Deleting...' : 'Yes, Delete Forever'}
                                </button>
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
    catalog: any;
    onRefresh: () => Promise<void> | void;
    isGenerating: boolean;
    setIsGenerating: (generating: boolean) => void;
}

function SkillsView({ skills, catalog, onRefresh, isGenerating, setIsGenerating }: SkillsViewProps) {
    const [isAddModalOpen, setIsAddModalOpen] = useState(false);
    const [skillName, setSkillName] = useState('');
    const [skillDesc, setSkillDesc] = useState('');
    const [skillInstruct, setSkillInstruct] = useState('');
    const [skillToDelete, setSkillToDelete] = useState<string | null>(null);
    const [detailsModalSkill, setDetailsModalSkill] = useState<{ name: string, content: string } | null>(null);
    const [isFetchingDetails, setIsFetchingDetails] = useState(false);
    const [isArchiving, setIsArchiving] = useState(false);
    const [archiveResult, setArchiveResult] = useState<any>(null);
    const [filterQuery, setFilterQuery] = useState('');
    const [viewMode, setViewMode] = useState<'curated' | 'temp'>('curated');

    const handleViewDetails = async (name: string) => {
        setIsFetchingDetails(true);
        try {
            if (name === 'web_search') {
                setDetailsModalSkill({ name, content: "# Built-in System Skill\n\nThis skill is natively provided by the OpenSpider runtime and proxy-forwards search queries to an external provider." });
                return;
            }
            const res = await apiFetch(`/api/skills/${name}`);
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
        setIsAddModalOpen(false);
        setSkillName('');
        setSkillDesc('');
        setSkillInstruct('');
        setIsGenerating(true);
        try {
            const res = await apiFetch('/api/skills/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name: skillName, description: skillDesc, instructions: skillInstruct })
            });
            const data = await res.json();
            if (!data.success) alert(`Error: ${data.error}`);
        } catch (e: any) {
            alert(`Error: ${e.message}`);
        } finally {
            await onRefresh();
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
            const res = await apiFetch(`/api/skills/${skillToDelete}`, { method: 'DELETE' });
            const data = await res.json();
            if (data.success) {
                setSkillToDelete(null);
                onRefresh();
            } else {
                alert(`Error deleting skill: ${data.error}`);
            }
        } catch (e: any) { alert(`Error: ${e.message}`); }
    };

    const handleArchive = async () => {
        setIsArchiving(true);
        setArchiveResult(null);
        try {
            const res = await apiFetch('/api/skills/archive', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ daysOld: 7 })
            });
            const data = await res.json();
            setArchiveResult(data);
            onRefresh();
        } catch (e: any) {
            alert(`Archive failed: ${e.message}`);
        } finally {
            setIsArchiving(false);
        }
    };

    const formatSkillName = (name: string) =>
        name.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase()).replace(/\bF1\b/gi, 'F1').replace(/\bS P\b/gi, 'S&P');

    const stats = catalog?.stats || { curatedCount: 0, tempCount: 0, tempTotalSizeKB: 0, archivedCount: 0 };
    const curatedSkills = catalog?.curated || [];
    const tempScripts = catalog?.temp || [];

    const filteredCurated = filterQuery
        ? curatedSkills.filter((s: any) => s.name.toLowerCase().includes(filterQuery.toLowerCase()) || s.description.toLowerCase().includes(filterQuery.toLowerCase()))
        : curatedSkills;
    const filteredTemp = filterQuery
        ? tempScripts.filter((s: any) => s.filename.toLowerCase().includes(filterQuery.toLowerCase()))
        : tempScripts;

    return (
        <div className="flex-1 p-10 overflow-y-auto fade-in relative">
            <div className="w-full h-full flex flex-col">
                <header className="mb-6 flex justify-between items-end shrink-0">
                    <div>
                        <h2 className="text-3xl font-bold text-white tracking-tight">Skills Catalog</h2>
                        <p className="text-slate-400 mt-2 text-sm max-w-2xl leading-relaxed">
                            Manage curated agent skills and temporary scripts generated during task execution.
                        </p>
                    </div>
                    <div className="flex items-center gap-4">
                        <div className="relative">
                            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
                            <input type="text" placeholder="Search skills..." value={filterQuery} onChange={e => setFilterQuery(e.target.value)} className="w-64 bg-slate-900/50 border border-slate-800 rounded-lg pl-9 pr-4 py-2 text-sm text-slate-300 focus:outline-none focus:ring-1 focus:ring-cyan-500/50" />
                        </div>
                        <button className="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg text-sm font-medium transition-colors shadow-lg shadow-cyan-900/20" onClick={() => setIsAddModalOpen(true)}>
                            + Add Skill
                        </button>
                    </div>
                </header>

                {/* Stats Dashboard */}
                <div className="grid grid-cols-4 gap-4 mb-6 shrink-0">
                    <div className="bg-slate-900/60 backdrop-blur-xl rounded-xl border border-cyan-500/20 p-4">
                        <div className="text-2xl font-bold text-cyan-400">{stats.curatedCount}</div>
                        <div className="text-xs text-slate-400 mt-1 uppercase tracking-wider font-semibold">Curated Skills</div>
                    </div>
                    <div className="bg-slate-900/60 backdrop-blur-xl rounded-xl border border-amber-500/20 p-4">
                        <div className="text-2xl font-bold text-amber-400">{stats.tempCount}</div>
                        <div className="text-xs text-slate-400 mt-1 uppercase tracking-wider font-semibold">Temp Scripts</div>
                    </div>
                    <div className="bg-slate-900/60 backdrop-blur-xl rounded-xl border border-slate-700 p-4">
                        <div className="text-2xl font-bold text-slate-300">{stats.tempTotalSizeKB} KB</div>
                        <div className="text-xs text-slate-400 mt-1 uppercase tracking-wider font-semibold">Temp Disk Usage</div>
                    </div>
                    <div className="bg-slate-900/60 backdrop-blur-xl rounded-xl border border-purple-500/20 p-4">
                        <div className="text-2xl font-bold text-purple-400">{stats.archivedCount}</div>
                        <div className="text-xs text-slate-400 mt-1 uppercase tracking-wider font-semibold">Archived</div>
                    </div>
                </div>

                {/* Archive Result Banner */}
                {archiveResult && (
                    <div className="mb-4 bg-emerald-900/30 border border-emerald-800/50 rounded-xl p-4 flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <span className="text-emerald-400 text-lg">✅</span>
                            <span className="text-sm text-emerald-200">Archived {archiveResult.archived} stale scripts ({archiveResult.freedKB} KB freed)</span>
                        </div>
                        <button className="text-xs text-slate-400 hover:text-white" onClick={() => setArchiveResult(null)}>Dismiss</button>
                    </div>
                )}

                {isGenerating && (
                    <div className="mb-4 bg-cyan-900/30 border border-cyan-800/50 rounded-xl p-4 flex items-center gap-4 animate-pulse">
                        <div className="w-8 h-8 rounded-full bg-cyan-500/20 flex items-center justify-center">
                            <Bot className="w-4 h-4 text-cyan-400 animate-bounce" />
                        </div>
                        <div>
                            <h4 className="text-sm font-medium text-cyan-200">Generating Skill Script...</h4>
                            <p className="text-xs text-cyan-400/70">The LLM is writing complex Python execution code. This can take up to 30 seconds.</p>
                        </div>
                    </div>
                )}

                {/* Tab Toggle */}
                <div className="flex gap-2 mb-4 shrink-0">
                    <button onClick={() => setViewMode('curated')} className={`px-4 py-2 rounded-lg text-xs font-bold uppercase tracking-widest transition-colors ${viewMode === 'curated' ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30' : 'text-slate-500 hover:text-slate-300 border border-transparent'}`}>
                        Curated ({stats.curatedCount})
                    </button>
                    <button onClick={() => setViewMode('temp')} className={`px-4 py-2 rounded-lg text-xs font-bold uppercase tracking-widest transition-colors ${viewMode === 'temp' ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30' : 'text-slate-500 hover:text-slate-300 border border-transparent'}`}>
                        Temp Scripts ({stats.tempCount})
                    </button>
                    {viewMode === 'temp' && stats.tempCount > 0 && (
                        <button onClick={handleArchive} disabled={isArchiving} className="ml-auto px-4 py-2 rounded-lg text-xs font-bold uppercase tracking-widest bg-red-500/10 text-red-400 border border-red-500/30 hover:bg-red-500/20 transition-colors disabled:opacity-50">
                            {isArchiving ? 'Archiving...' : '🗄️ Archive Stale (>7 days)'}
                        </button>
                    )}
                </div>

                <div className="flex-1 min-h-0 overflow-y-auto pb-10">
                    <div className="bg-slate-900/40 backdrop-blur-xl rounded-2xl border border-white/5 shadow-xl overflow-hidden">
                        {viewMode === 'curated' ? (
                            <>
                                <div className="grid grid-cols-[auto_1fr_auto_auto_auto] items-center px-5 py-3 border-b border-slate-800/60 text-[11px] uppercase tracking-widest text-slate-500 font-bold">
                                    <span className="w-8"></span>
                                    <span>Skill Name</span>
                                    <span className="text-center px-4">Agent</span>
                                    <span className="text-center px-4">Lang</span>
                                    <span className="text-right pr-1">Actions</span>
                                </div>
                                {filteredCurated.map((skill: any) => (
                                    <div key={skill.name} className="grid grid-cols-[auto_1fr_auto_auto_auto] items-center px-5 py-3.5 border-b border-slate-800/30 hover:bg-slate-800/30 transition-colors group">
                                        <div className="p-1.5 rounded-lg bg-cyan-500/10 text-cyan-400 mr-4">
                                            <Terminal className="w-4 h-4" />
                                        </div>
                                        <div className="truncate pr-4">
                                            <span className="text-sm font-medium text-white">{formatSkillName(skill.name)}</span>
                                            <p className="text-xs text-slate-500 truncate">{skill.description}</p>
                                        </div>
                                        <span className="text-[10px] uppercase tracking-widest text-slate-400 font-bold bg-slate-950/50 px-2.5 py-1 rounded border border-slate-800/60 mx-4 whitespace-nowrap">
                                            {skill.ownerAgent || 'Unassigned'}
                                        </span>
                                        <span className="text-[10px] uppercase tracking-widest text-emerald-400 font-bold bg-slate-950/50 px-2.5 py-1 rounded border border-emerald-800/40 mx-4 whitespace-nowrap">
                                            {skill.language}
                                        </span>
                                        <div className="flex items-center gap-4">
                                            <button className="text-xs font-semibold text-slate-500 hover:text-cyan-400 transition-colors" onClick={() => handleViewDetails(skill.name)}>
                                                {isFetchingDetails ? '...' : 'Details'}
                                            </button>
                                            <button className="text-xs font-semibold text-rose-500/60 hover:text-rose-400 transition-colors opacity-0 group-hover:opacity-100" onClick={(e) => handleDeleteSkill(e, skill.name)}>
                                                Delete
                                            </button>
                                        </div>
                                    </div>
                                ))}
                                {/* Built-in core skill */}
                                <div className="grid grid-cols-[auto_1fr_auto_auto_auto] items-center px-5 py-3.5 hover:bg-slate-800/30 transition-colors group">
                                    <div className="p-1.5 rounded-lg bg-emerald-500/10 text-emerald-400 mr-4">
                                        <Globe className="w-4 h-4" />
                                    </div>
                                    <div className="truncate pr-4">
                                        <span className="text-sm font-medium text-white">Web Search</span>
                                        <p className="text-xs text-slate-500">Built-in system search capability</p>
                                    </div>
                                    <span className="text-[10px] uppercase tracking-widest text-emerald-400 font-bold bg-slate-950/50 px-2.5 py-1 rounded border border-emerald-800/40 mx-4 whitespace-nowrap">System</span>
                                    <span className="text-[10px] uppercase tracking-widest text-emerald-400 font-bold bg-slate-950/50 px-2.5 py-1 rounded border border-emerald-800/40 mx-4 whitespace-nowrap">Built-in</span>
                                    <div className="flex items-center gap-4">
                                        <button className="text-xs font-semibold text-slate-500 hover:text-cyan-400 transition-colors" onClick={() => handleViewDetails('web_search')}>Details</button>
                                        <span className="text-xs text-transparent pointer-events-none">Delete</span>
                                    </div>
                                </div>
                            </>
                        ) : (
                            <>
                                <div className="grid grid-cols-[auto_1fr_auto_auto_auto] items-center px-5 py-3 border-b border-slate-800/60 text-[11px] uppercase tracking-widest text-slate-500 font-bold">
                                    <span className="w-8"></span>
                                    <span>Filename</span>
                                    <span className="text-center px-4">Size</span>
                                    <span className="text-center px-4">Age</span>
                                    <span className="text-right pr-1">Type</span>
                                </div>
                                {filteredTemp.length === 0 && (
                                    <div className="px-5 py-8 text-center text-slate-500 text-sm">
                                        No temp scripts found. The skills directory is clean! 🎉
                                    </div>
                                )}
                                {filteredTemp.map((script: any) => (
                                    <div key={script.filename} className="grid grid-cols-[auto_1fr_auto_auto_auto] items-center px-5 py-3 border-b border-slate-800/30 hover:bg-slate-800/30 transition-colors group">
                                        <div className="p-1.5 rounded-lg bg-amber-500/10 text-amber-400 mr-4">
                                            <FileCode className="w-4 h-4" />
                                        </div>
                                        <span className="text-sm font-mono text-slate-300 truncate pr-4">{script.filename}</span>
                                        <span className="text-xs text-slate-500 font-mono mx-4 whitespace-nowrap">{(script.sizeBytes / 1024).toFixed(1)} KB</span>
                                        <span className={`text-xs font-bold mx-4 whitespace-nowrap ${script.ageDays > 7 ? 'text-red-400' : script.ageDays > 3 ? 'text-amber-400' : 'text-emerald-400'}`}>
                                            {script.ageDays}d ago
                                        </span>
                                        <span className="text-[10px] uppercase tracking-widest text-amber-400 font-bold bg-slate-950/50 px-2.5 py-1 rounded border border-amber-800/40 whitespace-nowrap">
                                            {script.extension}
                                        </span>
                                    </div>
                                ))}
                            </>
                        )}
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
    const [autoFollow, setAutoFollow] = useState(true);
    const [searchQuery, setSearchQuery] = useState('');
    const [activeLevels, setActiveLevels] = useState<Set<string>>(new Set(['trace', 'debug', 'info', 'warn', 'error']));

    useEffect(() => {
        if (autoFollow) {
            endOfLogsRef.current?.scrollIntoView({ behavior: 'smooth' });
        }
    }, [logs, autoFollow]);

    // Classify log level based on content
    const getLogLevel = (data: string): string => {
        const lower = data.toLowerCase();
        if (lower.includes('error') || lower.includes('failed') || lower.includes('crash') || lower.includes('❌') || lower.includes('exception')) return 'error';
        if (lower.includes('warn') || lower.includes('⚠') || lower.includes('caution') || lower.includes('deprecated')) return 'warn';
        if (lower.includes('[worker') || lower.includes('[manager') || lower.includes('[scheduler') || lower.includes('usage') || lower.includes('completed') || lower.includes('delegating') || lower.includes('plan')) return 'info';
        if (lower.includes('[debug') || lower.includes('raw response') || lower.includes('token optimization') || lower.includes('context window')) return 'debug';
        return 'trace';
    };

    const levelConfig: Record<string, { color: string; bg: string; border: string }> = {
        error: { color: 'text-red-400', bg: 'bg-red-500/15', border: 'border-red-500/30' },
        warn: { color: 'text-amber-400', bg: 'bg-amber-500/15', border: 'border-amber-500/30' },
        info: { color: 'text-blue-400', bg: 'bg-blue-500/15', border: 'border-blue-500/30' },
        debug: { color: 'text-purple-400', bg: 'bg-purple-500/15', border: 'border-purple-500/30' },
        trace: { color: 'text-slate-400', bg: 'bg-slate-500/10', border: 'border-slate-700/30' },
    };

    const toggleLevel = (level: string) => {
        setActiveLevels(prev => {
            const next = new Set(prev);
            if (next.has(level)) next.delete(level);
            else next.add(level);
            return next;
        });
    };

    // Filter logs
    const filteredLogs = logs.filter(l => {
        const level = getLogLevel(l.data);
        if (!activeLevels.has(level)) return false;
        if (searchQuery && !l.data.toLowerCase().includes(searchQuery.toLowerCase())) return false;
        return true;
    });

    // Count logs per level
    const levelCounts: Record<string, number> = { error: 0, warn: 0, info: 0, debug: 0, trace: 0 };
    logs.forEach(l => { levelCounts[getLogLevel(l.data)]++; });

    // Export visible logs
    const handleExport = () => {
        const content = filteredLogs.map(l => `[${safeFormatTime(l.timestamp)}] [${getLogLevel(l.data).toUpperCase()}] ${l.data}`).join('\n');
        const blob = new Blob([content], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `openspider-logs-${new Date().toISOString().slice(0, 10)}.log`;
        a.click();
        URL.revokeObjectURL(url);
    };

    return (
        <div className="flex-1 p-10 overflow-y-auto fade-in flex flex-col max-h-screen">
            <div className="flex-1 flex flex-col min-h-0 bg-slate-900/40 backdrop-blur-xl rounded-2xl border border-white/5 shadow-xl relative overflow-hidden group">
                <div className="absolute top-0 inset-x-0 h-px w-full bg-gradient-to-r from-transparent via-slate-500/30 to-transparent z-10"></div>

                <header className="px-6 py-5 border-b border-slate-800/60 shrink-0 flex items-center justify-between bg-slate-900/80">
                    <div className="flex items-center gap-4">
                        <h2 className="text-xl font-bold text-white tracking-tight">System Telemetry</h2>
                        <div className="h-6 w-px bg-slate-800"></div>
                        <div className="flex items-center gap-2">
                            <input
                                type="checkbox"
                                className="rounded bg-slate-950 border-slate-800 text-blue-500 focus:ring-blue-500/30"
                                checked={autoFollow}
                                onChange={(e) => setAutoFollow(e.target.checked)}
                            />
                            <label className="text-xs font-semibold text-slate-400">Auto-follow</label>
                        </div>
                        <span className="text-xs font-mono text-slate-500 bg-slate-950/80 px-2 py-1 rounded border border-slate-800">
                            {filteredLogs.length} / {logs.length}
                        </span>
                    </div>

                    <div className="flex items-center gap-4">
                        {/* Level filter buttons */}
                        <div className="flex p-1 bg-slate-950 rounded-lg border border-slate-800">
                            {(['trace', 'debug', 'info', 'warn', 'error'] as const).map(level => {
                                const isActive = activeLevels.has(level);
                                const cfg = levelConfig[level];
                                return (
                                    <button
                                        key={level}
                                        onClick={() => toggleLevel(level)}
                                        className={`px-3 py-1 text-[10px] uppercase tracking-widest font-bold rounded transition-all ${isActive
                                            ? `${cfg.bg} ${cfg.color} shadow-sm`
                                            : 'text-slate-600 hover:text-slate-400'
                                            }`}
                                    >
                                        {level}
                                        {levelCounts[level] > 0 && (
                                            <span className="ml-1.5 text-[9px] opacity-70">
                                                {levelCounts[level]}
                                            </span>
                                        )}
                                    </button>
                                );
                            })}
                        </div>

                        {/* Search */}
                        <div className="relative w-48">
                            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
                            <input
                                type="text"
                                placeholder="Filter logs..."
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-9 pr-4 py-1.5 text-sm font-mono text-slate-300 focus:outline-none focus:border-blue-500/50"
                            />
                        </div>

                        {/* Export */}
                        <button
                            onClick={handleExport}
                            className="p-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg transition-colors border border-slate-700"
                            title="Download visible logs"
                        >
                            <Download className="w-4 h-4" />
                        </button>
                    </div>
                </header>

                <div className="flex-1 bg-slate-950/80 p-6 overflow-y-auto font-mono text-[13px] leading-relaxed text-slate-300">
                    {filteredLogs.length === 0 ? (
                        <div className="text-slate-500 opacity-60 text-center mt-20">
                            {logs.length === 0 ? 'Awaiting stream...' : 'No logs match the current filter.'}
                        </div>
                    ) : filteredLogs.map((l, i) => {
                        const level = getLogLevel(l.data);
                        const cfg = levelConfig[level];
                        return (
                            <div key={i} className={`mb-1 break-all hover:bg-slate-800/50 px-3 py-1 rounded transition-colors flex items-start gap-3 border-l-2 ${cfg.border}`}>
                                <span className="text-slate-500 shrink-0 select-none text-[11px] mt-0.5">{safeFormatTime(l.timestamp)}</span>
                                <span className={`shrink-0 text-[9px] uppercase font-bold tracking-wider px-1.5 py-0.5 rounded ${cfg.bg} ${cfg.color} mt-0.5`}>
                                    {level}
                                </span>
                                <span className={
                                    level === 'error' ? 'text-red-300' :
                                        level === 'warn' ? 'text-amber-200' :
                                            level === 'info' ? 'text-slate-200' :
                                                level === 'debug' ? 'text-purple-300' : 'text-slate-400'
                                }>
                                    {l.data}
                                </span>
                            </div>
                        );
                    })}
                    <div ref={endOfLogsRef} />
                </div>
            </div>
        </div>
    );
}

function CronView({ agents, logs }: { agents: any[]; logs: LogMessage[] }) {
    const [jobs, setJobs] = useState<any[]>([]);
    const [showModal, setShowModal] = useState(false);
    const [formData, setFormData] = useState({ description: '', prompt: '', intervalHours: '24', agentId: 'gateway', status: 'enabled', preferredTime: '', modelOverride: '' });
    const [editJob, setEditJob] = useState<any>(null);
    const [editFormData, setEditFormData] = useState({ description: '', prompt: '', intervalHours: '24', preferredTime: '', modelOverride: '', agentId: 'manager' });
    const [expandedPrompts, setExpandedPrompts] = useState<Set<string>>(new Set());
    const [waContacts, setWaContacts] = useState<{ groups: any[]; dms: any[] }>({ groups: [], dms: [] });
    const [contactSearch, setContactSearch] = useState('');
    const [showContactDropdown, setShowContactDropdown] = useState(false);
    const [maxJobs, setMaxJobs] = useState(50);
    const [showSettings, setShowSettings] = useState(false);
    const [editMaxJobs, setEditMaxJobs] = useState('50');

    useEffect(() => {
        fetchJobs();
        // Fetch cron config
        apiFetch('/api/cron/config').then(r => r.json()).then(data => {
            setMaxJobs(data.maxJobs || 50);
            setEditMaxJobs(String(data.maxJobs || 50));
        }).catch(() => {});
    }, []);

    const fetchJobs = async () => {
        try {
            const res = await apiFetch('/api/cron');
            const data = await res.json();
            setJobs(data);
        } catch (e) {
            console.error("Failed to fetch cron jobs", e);
        }
    };

    const handleDelete = async (id: string) => {
        try {
            await apiFetch(`/api/cron/${id}`, { method: 'DELETE' });
            fetchJobs();
        } catch (e) { }
    };

    const toggleStatus = async (job: any) => {
        try {
            const newStatus = job.status === 'enabled' ? 'disabled' : 'enabled';
            await apiFetch(`/api/cron/${job.id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ status: newStatus })
            });
            fetchJobs();
        } catch (e) { }
    };

    const handleRunForcefully = async (id: string) => {
        try {
            await apiFetch(`/api/cron/${id}/run`, { method: 'POST' });
            // We just optimistically refetch to update the last run time
            setTimeout(fetchJobs, 1000);
        } catch (e) { }
    };

    const handleCreate = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            const payload = { ...formData, preferredTime: formData.preferredTime || undefined, modelOverride: formData.modelOverride || undefined };
            await apiFetch('/api/cron', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            setShowModal(false);
            setFormData({ description: '', prompt: '', intervalHours: '24', agentId: 'gateway', status: 'enabled', preferredTime: '', modelOverride: '' });
            fetchJobs();
        } catch (e) { }
    };

    const openEdit = (job: any) => {
        setEditJob(job);
        setEditFormData({
            description: job.description || '',
            prompt: job.prompt || '',
            intervalHours: String(job.intervalHours || 24),
            preferredTime: job.preferredTime || '',
            modelOverride: job.modelOverride || '',
            agentId: job.agentId || 'manager',
        });
        setContactSearch('');
        setShowContactDropdown(false);
        // Fetch WhatsApp contacts for the picker
        apiFetch('/api/whatsapp/contacts')
            .then(r => r.json())
            .then(data => setWaContacts({ groups: data.groups || [], dms: data.dms || [] }))
            .catch(() => setWaContacts({ groups: [], dms: [] }));
    };

    const handleEdit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!editJob) return;
        try {
            const payload: any = {
                description: editFormData.description,
                prompt: editFormData.prompt,
                intervalHours: Number(editFormData.intervalHours) || 24,
            };
            // Send empty string (not undefined) so JSON.stringify includes them
            // and the server's spread operator correctly clears old values
            payload.preferredTime = editFormData.preferredTime || '';
            payload.modelOverride = editFormData.modelOverride || '';
            payload.agentId = editFormData.agentId || 'manager';
            await apiFetch(`/api/cron/${editJob.id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            setEditJob(null);
            fetchJobs();
        } catch (e) { }
    };

    const togglePrompt = (id: string) => {
        setExpandedPrompts(prev => {
            const next = new Set(prev);
            if (next.has(id)) next.delete(id); else next.add(id);
            return next;
        });
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
            <div className="w-full">
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
                    <div className="flex items-center gap-3">
                        {/* Job count + settings */}
                        <div className="flex items-center gap-2">
                            <span className="text-xs text-slate-500 font-mono">{jobs.length} / {maxJobs} jobs</span>
                            <button
                                onClick={() => { setShowSettings(!showSettings); setEditMaxJobs(String(maxJobs)); }}
                                className="p-1.5 text-slate-500 hover:text-slate-300 hover:bg-slate-800 rounded-lg transition-colors"
                                title="Cron settings"
                            >
                                <Settings className="w-4 h-4" />
                            </button>
                        </div>
                        <button
                            onClick={() => setShowModal(true)}
                            className="flex items-center gap-2 px-5 py-2.5 bg-rose-600 hover:bg-rose-500 text-white rounded-xl text-sm font-semibold transition-all shadow-[0_0_20px_rgba(225,29,72,0.3)] hover:shadow-[0_0_30px_rgba(225,29,72,0.5)] border border-rose-500/50"
                        >
                            <Plus className="w-4 h-4" />
                            Deploy Job
                        </button>
                    </div>
                </header>

                {/* Settings panel */}
                {showSettings && (
                    <div className="mb-6 bg-slate-900/60 backdrop-blur-xl rounded-2xl border border-white/5 p-5 shadow-xl">
                        <div className="flex items-center justify-between">
                            <div>
                                <h4 className="text-sm font-bold text-white flex items-center gap-2"><Settings className="w-4 h-4 text-slate-400" /> Cron Settings</h4>
                                <p className="text-xs text-slate-500 mt-1">Configure the maximum number of concurrent cron jobs.</p>
                            </div>
                            <div className="flex items-center gap-3">
                                <label className="text-[10px] uppercase tracking-widest text-slate-500 font-bold">Max Jobs</label>
                                <input
                                    type="number" min="5" max="200"
                                    value={editMaxJobs}
                                    onChange={e => setEditMaxJobs(e.target.value)}
                                    className="w-20 bg-slate-950 border border-slate-700 rounded-lg px-3 py-1.5 text-sm text-slate-200 focus:ring-1 focus:ring-rose-500 outline-none text-center"
                                />
                                <button
                                    onClick={async () => {
                                        const val = Math.max(5, Math.min(200, Number(editMaxJobs) || 50));
                                        await apiFetch('/api/cron/config', {
                                            method: 'PUT',
                                            headers: { 'Content-Type': 'application/json' },
                                            body: JSON.stringify({ maxJobs: val })
                                        });
                                        setMaxJobs(val);
                                        setEditMaxJobs(String(val));
                                        setShowSettings(false);
                                    }}
                                    className="px-4 py-1.5 bg-rose-600 hover:bg-rose-500 text-white rounded-lg text-xs font-semibold transition-colors"
                                >Save</button>
                            </div>
                        </div>
                    </div>
                )}

                <div className="space-y-4">
                    {jobs.length === 0 ? (
                        <div className="bg-slate-900/40 backdrop-blur-xl rounded-2xl border border-white/5 p-10 text-center text-slate-500 shadow-xl">
                            No autonomous jobs currently running.
                        </div>
                    ) : jobs.map((job: any) => {
                        const isEnabled = job.status !== 'disabled';
                        const neverRun = job.lastRunTimestamp === 0;

                        const hasPreferredTime = !!job.preferredTime;
                        const intervalMs = job.intervalHours * 60 * 60 * 1000;
                        const timeSinceLast = Date.now() - job.lastRunTimestamp;
                        const timeUntilNext = hasPreferredTime ? 0 : intervalMs - timeSinceLast;

                        // Extract delivery info from prompt
                        const emails: string[] = [...new Set((job.prompt.match(/[a-zA-Z0-9._%+-]+@(?:gmail|yahoo|hotmail|outlook|icloud|protonmail|aol)\.[a-z]{2,}/gi) || []) as string[])];
                        const whatsappNumbers: string[] = [...new Set((job.prompt.match(/\+?\d{10,15}(?=@s\.whatsapp\.net)/g) || []) as string[])];
                        // Extract WhatsApp group JIDs (e.g. 120363423852747118@g.us)
                        const groupJids: string[] = [...new Set((job.prompt.match(/\d+@g\.us/g) || []) as string[])];
                        // Try to extract group names from prompt like: group "Name" (group JID: xxx@g.us)
                        const groupNames: Record<string, string> = {};
                        for (const gid of groupJids) {
                            const nameMatch = job.prompt.match(new RegExp(`group\\s+["']([^"']+)["']\\s*\\(.*?${gid.replace('.', '\\.')}`, 'i'));
                            if (nameMatch) groupNames[gid] = nameMatch[1];
                        }
                        const hasWhatsApp = /whatsapp/i.test(job.prompt);
                        const hasEmail = /email/i.test(job.prompt) || emails.length > 0;

                        return (
                            <div key={job.id} className="bg-slate-900/60 backdrop-blur-xl rounded-2xl border border-white/5 p-6 flex flex-col gap-4 shadow-xl hover:bg-slate-900/80 transition-all">

                                {/* Header Details */}
                                <div className="flex justify-between items-start">
                                    <div>
                                        <h3 className="text-xl font-bold text-white tracking-tight mb-1">{job.description}</h3>
                                        <div className="text-xs text-slate-500 font-mono flex gap-2">
                                            <span>{job.preferredTime ? `Daily at ${job.preferredTime}` : job.intervalHours < 1 ? `Every ${Math.round(job.intervalHours * 60)}m` : `Every ${job.intervalHours}h`}</span>
                                            {job.modelOverride && <span className="ml-2 px-1.5 py-0.5 bg-purple-500/10 text-purple-400 text-[10px] font-bold rounded border border-purple-500/20 uppercase">{job.modelOverride}</span>}
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
                                            <span className="text-slate-300 font-mono">{!isEnabled ? 'n/a' : hasPreferredTime ? job.preferredTime : `in ${formatTimeDelta(timeUntilNext)}`}</span>
                                        </div>
                                        <div className="flex justify-between gap-6 items-center">
                                            <span className="text-slate-500 font-bold tracking-widest uppercase">Last</span>
                                            <span className="text-slate-400 font-mono">{neverRun ? 'never' : `${formatTimeDelta(timeSinceLast)} ago`}</span>
                                        </div>
                                    </div>
                                </div>

                                {/* Delivery Info */}
                                {(hasEmail || hasWhatsApp) && (
                                    <div className="mt-1">
                                        <span className="text-[10px] uppercase font-bold text-slate-500 tracking-widest block mb-2">Delivery</span>
                                        <div className="flex flex-wrap gap-2">
                                            {emails.map((email, i) => (
                                                <span key={`email-${i}`} className="inline-flex items-center gap-1.5 px-2.5 py-1 bg-blue-500/10 text-blue-400 text-xs font-mono rounded-lg border border-blue-500/20">
                                                    📧 {email}
                                                </span>
                                            ))}
                                            {whatsappNumbers.map((num, i) => (
                                                <span key={`wa-${i}`} className="inline-flex items-center gap-1.5 px-2.5 py-1 bg-emerald-500/10 text-emerald-400 text-xs font-mono rounded-lg border border-emerald-500/20">
                                                    💬 +{num}
                                                </span>
                                            ))}
                                            {groupJids.map((gid, i) => (
                                                <span key={`wag-${i}`} className="inline-flex items-center gap-1.5 px-2.5 py-1 bg-teal-500/10 text-teal-400 text-xs font-mono rounded-lg border border-teal-500/20">
                                                    👥 {groupNames[gid] || gid}
                                                </span>
                                            ))}
                                            {hasWhatsApp && whatsappNumbers.length === 0 && groupJids.length === 0 && (
                                                <span className="inline-flex items-center gap-1.5 px-2.5 py-1 bg-emerald-500/10 text-emerald-400 text-xs font-mono rounded-lg border border-emerald-500/20">
                                                    💬 WhatsApp (default user)
                                                </span>
                                            )}
                                        </div>
                                    </div>
                                )}

                                {/* Prompt Block */}
                                <div className="mt-2 text-sm text-slate-400 leading-relaxed max-w-3xl">
                                    <span className="text-[10px] uppercase font-bold text-slate-500 tracking-widest block mb-1">Prompt</span>
                                    <span>
                                        {job.prompt.length > 150 && !expandedPrompts.has(job.id)
                                            ? <>{job.prompt.substring(0, 150)}… <button onClick={() => togglePrompt(job.id)} className="text-rose-400 hover:text-rose-300 text-xs font-semibold ml-1">show more</button></>
                                            : <>{job.prompt}{job.prompt.length > 150 && <button onClick={() => togglePrompt(job.id)} className="text-rose-400 hover:text-rose-300 text-xs font-semibold ml-1">show less</button>}</>
                                        }
                                    </span>
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
                                        <button onClick={() => openEdit(job)} className="px-4 py-1.5 text-xs font-semibold text-sky-400 hover:text-white hover:bg-sky-600/80 bg-sky-500/10 rounded-lg border border-sky-500/20 transition-colors">Edit</button>
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
                                <label className="block text-[10px] uppercase tracking-widest text-slate-500 font-bold mb-2">Preferred Time (e.g. 07:00) — leave blank for interval-based</label>
                                <input type="time" value={formData.preferredTime} onChange={e => setFormData({ ...formData, preferredTime: e.target.value })} className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-sm text-slate-200 focus:ring-1 focus:ring-rose-500 focus:border-rose-500 outline-none" />
                            </div>
                            <div>
                                <label className="block text-[10px] uppercase tracking-widest text-slate-500 font-bold mb-2">Interval — used when no preferred time is set</label>
                                <select value={formData.intervalHours} onChange={e => setFormData({ ...formData, intervalHours: e.target.value })} className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-sm text-slate-200 focus:ring-1 focus:ring-rose-500 focus:border-rose-500 outline-none">
                                    <option value="0.25">Every 15 minutes</option>
                                    <option value="0.5">Every 30 minutes</option>
                                    <option value="1">Every 1 hour</option>
                                    <option value="2">Every 2 hours</option>
                                    <option value="4">Every 4 hours</option>
                                    <option value="6">Every 6 hours</option>
                                    <option value="8">Every 8 hours</option>
                                    <option value="12">Every 12 hours</option>
                                    <option value="24">Every 24 hours (daily)</option>
                                    <option value="48">Every 2 days</option>
                                    <option value="168">Every 7 days (weekly)</option>
                                </select>
                            </div>
                            <div>
                                <label className="block text-[10px] uppercase tracking-widest text-slate-500 font-bold mb-2">Task Prompt</label>
                                <textarea required rows={4} value={formData.prompt} onChange={e => setFormData({ ...formData, prompt: e.target.value })} placeholder="Agent instructions..." className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-sm text-slate-200 focus:ring-1 focus:ring-rose-500 focus:border-rose-500 outline-none resize-none" />
                            </div>
                            <div>
                                <label className="block text-[10px] uppercase tracking-widest text-slate-500 font-bold mb-2">Model Override — leave as Default to use primary model</label>
                                <select value={formData.modelOverride} onChange={e => setFormData({ ...formData, modelOverride: e.target.value })} className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-sm text-slate-200 focus:ring-1 focus:ring-rose-500 focus:border-rose-500 outline-none">
                                    <option value="">Default (Primary Model)</option>
                                    <option value="nvidia-1">NVIDIA Backup 1</option>
                                    <option value="nvidia-2">NVIDIA Backup 2</option>
                                    <option value="deepseek">DeepSeek V3</option>
                                    <option value="antigravity">Antigravity (Gemini)</option>
                                    <option value="openai">OpenAI</option>
                                    <option value="anthropic">Anthropic</option>
                                    <option value="ollama">Ollama</option>
                                </select>
                            </div>
                            <div className="pt-4 flex justify-end gap-3">
                                <button type="button" onClick={() => setShowModal(false)} className="px-4 py-2 border border-slate-700 text-slate-300 rounded-lg text-sm hover:bg-slate-800 transition-colors">Cancel</button>
                                <button type="submit" className="px-5 py-2 bg-rose-600 hover:bg-rose-500 text-white rounded-lg text-sm font-semibold transition-colors">Deploy Job</button>
                            </div>
                        </form>
                    </div>
                </div>
            )}

            {/* Edit Job Modal */}
            {editJob && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm fade-in">
                    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 w-full max-w-xl shadow-2xl relative overflow-hidden">
                        <div className="absolute top-0 inset-x-0 h-px w-full bg-gradient-to-r from-transparent via-sky-500/50 to-transparent"></div>
                        <div className="flex justify-between items-center mb-6">
                            <h3 className="text-xl font-bold text-white flex items-center gap-2">
                                <Clock className="w-5 h-5 text-sky-500" />
                                Edit Job
                            </h3>
                            <button onClick={() => setEditJob(null)} className="text-slate-500 hover:text-white transition-colors">
                                <X className="w-5 h-5" />
                            </button>
                        </div>
                        <form onSubmit={handleEdit} className="space-y-4">
                            <div>
                                <label className="block text-[10px] uppercase tracking-widest text-slate-500 font-bold mb-2">Description</label>
                                <input required type="text" value={editFormData.description} onChange={e => setEditFormData({ ...editFormData, description: e.target.value })} className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-sm text-slate-200 focus:ring-1 focus:ring-sky-500 focus:border-sky-500 outline-none" />
                            </div>
                            <div>
                                <label className="block text-[10px] uppercase tracking-widest text-slate-500 font-bold mb-2">Assigned Agent</label>
                                <select value={editFormData.agentId} onChange={e => setEditFormData({ ...editFormData, agentId: e.target.value })} className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-sm text-slate-200 focus:ring-1 focus:ring-sky-500 focus:border-sky-500 outline-none">
                                    <option value="gateway">Gateway Architect (Default Routing)</option>
                                    <option value="manager">Manager</option>
                                    {agents.map(a => <option key={a.id} value={a.id}>{a.name}</option>)}
                                </select>
                            </div>
                            <div>
                                <label className="block text-[10px] uppercase tracking-widest text-slate-500 font-bold mb-2">Preferred Time (e.g. 07:00) — leave blank for interval-based</label>
                                <input type="time" value={editFormData.preferredTime} onChange={e => setEditFormData({ ...editFormData, preferredTime: e.target.value })} className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-sm text-slate-200 focus:ring-1 focus:ring-sky-500 focus:border-sky-500 outline-none" />
                            </div>
                            <div>
                                <label className="block text-[10px] uppercase tracking-widest text-slate-500 font-bold mb-2">Interval — used when no preferred time is set</label>
                                <select value={editFormData.intervalHours} onChange={e => setEditFormData({ ...editFormData, intervalHours: e.target.value })} className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-sm text-slate-200 focus:ring-1 focus:ring-sky-500 focus:border-sky-500 outline-none">
                                    <option value="0.25">Every 15 minutes</option>
                                    <option value="0.5">Every 30 minutes</option>
                                    <option value="1">Every 1 hour</option>
                                    <option value="2">Every 2 hours</option>
                                    <option value="4">Every 4 hours</option>
                                    <option value="6">Every 6 hours</option>
                                    <option value="8">Every 8 hours</option>
                                    <option value="12">Every 12 hours</option>
                                    <option value="24">Every 24 hours (daily)</option>
                                    <option value="48">Every 2 days</option>
                                    <option value="168">Every 7 days (weekly)</option>
                                </select>
                            </div>
                            <div>
                                <label className="block text-[10px] uppercase tracking-widest text-slate-500 font-bold mb-2">Task Prompt</label>
                                <textarea required rows={6} value={editFormData.prompt} onChange={e => setEditFormData({ ...editFormData, prompt: e.target.value })} className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-sm text-slate-200 focus:ring-1 focus:ring-sky-500 focus:border-sky-500 outline-none resize-none" />
                            </div>
                            <div>
                                <label className="block text-[10px] uppercase tracking-widest text-slate-500 font-bold mb-2">Model Override</label>
                                <select value={editFormData.modelOverride} onChange={e => setEditFormData({ ...editFormData, modelOverride: e.target.value })} className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-sm text-slate-200 focus:ring-1 focus:ring-sky-500 focus:border-sky-500 outline-none">
                                    <option value="">Default (Primary Model)</option>
                                    <option value="nvidia-1">NVIDIA Backup 1</option>
                                    <option value="nvidia-2">NVIDIA Backup 2</option>
                                    <option value="deepseek">DeepSeek V3</option>
                                    <option value="antigravity">Antigravity (Gemini)</option>
                                    <option value="openai">OpenAI</option>
                                    <option value="anthropic">Anthropic</option>
                                    <option value="ollama">Ollama</option>
                                </select>
                            </div>
                            {/* Delivery Channels — add/remove recipients */}
                            <div className="bg-slate-950/50 border border-slate-800 rounded-lg p-3">
                                <label className="block text-[10px] uppercase tracking-widest text-slate-500 font-bold mb-3">Delivery Channels</label>
                                {/* Detected recipients */}
                                <div className="flex flex-wrap gap-2 mb-3">
                                    {(() => {
                                        const promptText = editFormData.prompt || '';
                                        const detectedEmails: string[] = [...new Set((promptText.match(/[a-zA-Z0-9._%+-]+@(?:gmail|yahoo|hotmail|outlook|icloud|protonmail|aol)\.[a-z]{2,}/gi) || []) as string[])];
                                        const detectedWA: string[] = [...new Set((promptText.match(/\+?\d{10,15}(?=@s\.whatsapp\.net)/g) || []) as string[])];
                                        // Detect WhatsApp group JIDs (format: 120363423852747118@g.us or 14156249639-1373117853@g.us)
                                        const groupMatches = [...promptText.matchAll(/group\s+(?:JID:\s*)?([\d-]+@g\.us)/gi)];
                                        const detectedGroups: { jid: string; name: string }[] = [];
                                        for (const m of groupMatches) {
                                            const jid = m[1];
                                            if (!detectedGroups.find(g => g.jid === jid)) {
                                                // Try to extract the group name from the prompt (pattern: "GroupName" (group JID: xxx@g.us))
                                                const nameMatch = promptText.match(new RegExp(`"([^"]+)"\\s*\\(group\\s+JID:\\s*${jid.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\)`, 'i'));
                                                detectedGroups.push({ jid, name: nameMatch ? nameMatch[1] : jid });
                                            }
                                        }
                                        const mentionsWA = /whatsapp/i.test(promptText) && detectedWA.length === 0 && detectedGroups.length === 0;
                                        return (
                                            <>
                                                {detectedEmails.map((email, i) => (
                                                    <span key={`edit-email-${i}`} className="inline-flex items-center gap-1.5 px-2.5 py-1 bg-blue-500/10 text-blue-400 text-xs font-mono rounded-lg border border-blue-500/20">
                                                        📧 {email}
                                                        <button type="button" onClick={() => {
                                                            const updated = editFormData.prompt.replace(new RegExp(`\\s*(AND\\s+)?${email.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}(\\s+AND)?`, 'gi'), ' ').replace(/\s{2,}/g, ' ');
                                                            setEditFormData({ ...editFormData, prompt: updated });
                                                        }} className="text-blue-400/60 hover:text-red-400 ml-1 text-[10px] font-bold">×</button>
                                                    </span>
                                                ))}
                                                {detectedGroups.map((g, i) => (
                                                    <span key={`edit-grp-${i}`} className="inline-flex items-center gap-1.5 px-2.5 py-1 bg-emerald-500/10 text-emerald-400 text-xs rounded-lg border border-emerald-500/20">
                                                        👥 {g.name}
                                                        <button type="button" onClick={() => {
                                                            // Remove the entire group delivery sentence from prompt
                                                            const escaped = g.jid.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
                                                            const updated = editFormData.prompt
                                                                .replace(new RegExp(`\\s*Also send[^.]*${escaped}[^.]*\\.?`, 'gi'), '')
                                                                .replace(/\s{2,}/g, ' ').trim();
                                                            setEditFormData({ ...editFormData, prompt: updated });
                                                        }} className="text-emerald-400/60 hover:text-red-400 ml-1 text-[10px] font-bold">×</button>
                                                    </span>
                                                ))}
                                                {detectedWA.map((num, i) => (
                                                    <span key={`edit-wa-${i}`} className="inline-flex items-center gap-1.5 px-2.5 py-1 bg-emerald-500/10 text-emerald-400 text-xs font-mono rounded-lg border border-emerald-500/20">
                                                        💬 +{num}
                                                        <button type="button" onClick={() => {
                                                            // Remove the entire DM delivery sentence from prompt
                                                            const updated = editFormData.prompt
                                                                .replace(new RegExp(`\\s*Also send[^.]*${num}@s\\.whatsapp\\.net[^.]*\\.?`, 'gi'), '')
                                                                .replace(/\s{2,}/g, ' ').trim();
                                                            setEditFormData({ ...editFormData, prompt: updated });
                                                        }} className="text-emerald-400/60 hover:text-red-400 ml-1 text-[10px] font-bold">×</button>
                                                    </span>
                                                ))}
                                                {mentionsWA && (
                                                    <span className="inline-flex items-center gap-1.5 px-2.5 py-1 bg-emerald-500/10 text-emerald-400 text-xs font-mono rounded-lg border border-emerald-500/20">
                                                        💬 WhatsApp (default user)
                                                    </span>
                                                )}
                                                {detectedEmails.length === 0 && detectedWA.length === 0 && detectedGroups.length === 0 && !mentionsWA && (
                                                    <span className="text-xs text-slate-600 italic">No delivery channels detected</span>
                                                )}
                                            </>
                                        );
                                    })()}
                                </div>
                                {/* Add new recipient — searchable WhatsApp contact picker */}
                                <div className="relative">
                                    <div className="flex gap-2">
                                        <input
                                            type="text"
                                            id="add-recipient-input"
                                            placeholder="Search groups/contacts or type email/phone..."
                                            value={contactSearch}
                                            onChange={e => {
                                                setContactSearch(e.target.value);
                                                setShowContactDropdown(true);
                                            }}
                                            onFocus={() => setShowContactDropdown(true)}
                                            className="flex-1 bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-200 focus:ring-1 focus:ring-sky-500 focus:border-sky-500 outline-none placeholder-slate-600"
                                            onKeyDown={(e) => {
                                                if (e.key === 'Escape') setShowContactDropdown(false);
                                                if (e.key === 'Enter') {
                                                    e.preventDefault();
                                                    // Manual entry fallback
                                                    const val = contactSearch.trim();
                                                    if (!val) return;
                                                    let updatedPrompt = editFormData.prompt;
                                                    if (val.includes('@') && /\.[a-z]{2,}$/i.test(val)) {
                                                        updatedPrompt += ` Also send via email to ${val}.`;
                                                    } else if (/^\+?\d{10,15}$/.test(val.replace(/[\s-]/g, ''))) {
                                                        const cleaned = val.replace(/[\s-]/g, '').replace(/^\+/, '');
                                                        updatedPrompt += ` Also send via WhatsApp to ${cleaned}@s.whatsapp.net.`;
                                                    }
                                                    setEditFormData({ ...editFormData, prompt: updatedPrompt });
                                                    setContactSearch('');
                                                    setShowContactDropdown(false);
                                                }
                                            }}
                                        />
                                        <button
                                            type="button"
                                            onClick={() => setShowContactDropdown(!showContactDropdown)}
                                            className="px-3 py-2 bg-sky-600 hover:bg-sky-500 text-white rounded-lg text-xs font-bold transition-colors"
                                            title="Browse contacts"
                                        >
                                            <Users className="w-3.5 h-3.5" />
                                        </button>
                                    </div>

                                    {/* Contact dropdown — groups first on text search, DMs first on number/empty search */}
                                    {showContactDropdown && (waContacts.groups.length > 0 || waContacts.dms.length > 0) && (() => {
                                        const search = contactSearch.toLowerCase().trim();
                                        const isNumericSearch = contactSearch && /^\+?\d+$/.test(contactSearch.replace(/[\s-]/g, ''));
                                        const isTextSearch = contactSearch && !isNumericSearch;

                                        // Filter DMs: only by number when numeric, show all otherwise
                                        const filteredDMs = isNumericSearch
                                            ? waContacts.dms.filter((d: any) => d.number.includes(contactSearch.replace(/[\s+-]/g, '')))
                                            : waContacts.dms;

                                        // Filter + sort groups: exact → starts with → contains
                                        const filteredGroups = waContacts.groups
                                            .filter((g: any) => !search || g.name.toLowerCase().includes(search))
                                            .sort((a: any, b: any) => {
                                                if (!search) return 0;
                                                const aExact = a.name.toLowerCase() === search;
                                                const bExact = b.name.toLowerCase() === search;
                                                if (aExact && !bExact) return -1;
                                                if (!aExact && bExact) return 1;
                                                const aStarts = a.name.toLowerCase().startsWith(search);
                                                const bStarts = b.name.toLowerCase().startsWith(search);
                                                if (aStarts && !bStarts) return -1;
                                                if (!aStarts && bStarts) return 1;
                                                return 0;
                                            });

                                        const dmSection = filteredDMs.length > 0 && (
                                            <>
                                                <div className="px-3 py-1.5 bg-slate-800/60 text-[9px] font-bold uppercase tracking-widest text-slate-500 sticky top-0 z-10 flex justify-between">
                                                    <span>Direct Messages</span>
                                                    <span className="text-slate-600">{filteredDMs.length}</span>
                                                </div>
                                                {filteredDMs.map((d: any, i: number) => (
                                                    <button key={`dm-${i}`} type="button"
                                                        onClick={() => {
                                                            setEditFormData({ ...editFormData, prompt: editFormData.prompt + ` Also send via WhatsApp to ${d.number}@s.whatsapp.net.` });
                                                            setContactSearch(''); setShowContactDropdown(false);
                                                        }}
                                                        className="w-full text-left px-3 py-2 text-xs text-slate-300 hover:bg-sky-500/10 hover:text-sky-300 transition-colors flex items-center gap-2 border-b border-slate-800/40 last:border-b-0"
                                                    >
                                                        <span className="text-blue-400">💬</span>
                                                        <span className="truncate">{d.name !== d.number ? d.name : `+${d.number}`}</span>
                                                        <span className="text-slate-600 text-[10px] ml-auto font-mono">+{d.number}</span>
                                                    </button>
                                                ))}
                                            </>
                                        );

                                        const groupSection = filteredGroups.length > 0 && (
                                            <>
                                                <div className="px-3 py-1.5 bg-slate-800/60 text-[9px] font-bold uppercase tracking-widest text-slate-500 sticky top-0 z-10 flex justify-between">
                                                    <span>WhatsApp Groups</span>
                                                    <span className="text-slate-600">{filteredGroups.length}</span>
                                                </div>
                                                {filteredGroups.map((g: any, i: number) => (
                                                    <button key={`grp-${i}`} type="button"
                                                        onClick={() => {
                                                            setEditFormData({ ...editFormData, prompt: editFormData.prompt + ` Also send the results to the WhatsApp group "${g.name}" (group JID: ${g.id}).` });
                                                            setContactSearch(''); setShowContactDropdown(false);
                                                        }}
                                                        className="w-full text-left px-3 py-2 text-xs text-slate-300 hover:bg-sky-500/10 hover:text-sky-300 transition-colors flex items-center gap-2 border-b border-slate-800/40 last:border-b-0"
                                                    >
                                                        <span className="text-emerald-400">👥</span>
                                                        <span className="truncate">{g.name}</span>
                                                    </button>
                                                ))}
                                            </>
                                        );

                                        return (
                                            <div className="absolute z-50 mt-1 w-full bg-slate-900 border border-slate-700 rounded-lg shadow-2xl max-h-[280px] overflow-y-auto">
                                                {/* When text searched: groups first. Otherwise: DMs first */}
                                                {isTextSearch ? <>{groupSection}{dmSection}</> : <>{dmSection}{groupSection}</>}
                                                {!filteredDMs.length && !filteredGroups.length && (
                                                    <div className="px-3 py-3 text-[10px] text-slate-600 italic text-center">No matching contacts</div>
                                                )}
                                            </div>
                                        );
                                    })()}
                                </div>
                            </div>
                            <div className="pt-4 flex justify-end gap-3">
                                <button type="button" onClick={() => setEditJob(null)} className="px-4 py-2 border border-slate-700 text-slate-300 rounded-lg text-sm hover:bg-slate-800 transition-colors">Cancel</button>
                                <button type="submit" className="px-5 py-2 bg-sky-600 hover:bg-sky-500 text-white rounded-lg text-sm font-semibold transition-colors">Save Changes</button>
                            </div>
                        </form>
                    </div>
                </div>
            )}

            {/* Cron Execution Logs */}
            <div className="mt-12">
                <h3 className="text-xl font-bold text-white tracking-tight flex items-center gap-3 mb-6">
                    <FileText className="w-6 h-6 text-indigo-400" />
                    Execution Logs
                </h3>
                {(() => {
                    const cronLogs = logs.filter(l => (l as any).type === 'cron_result');
                    if (cronLogs.length === 0) {
                        return (
                            <div className="text-slate-500 text-sm italic bg-slate-900/50 rounded-xl border border-slate-800/60 p-8 text-center">
                                No cron execution results yet. Results will appear here as scheduled jobs complete.
                            </div>
                        );
                    }
                    return (
                        <div className="space-y-4 max-h-[600px] overflow-y-auto pr-2">
                            {cronLogs
                                .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
                                .slice(0, 50)
                                .map((log, i) => {
                                    const text = log.data.trim();
                                    const cronMatch = text.match(/^\[Cron: (.+?)\] /);
                                    const jobName = cronMatch ? cronMatch[1] : 'Unknown Job';
                                    let content = cronMatch ? text.substring(cronMatch[0].length).trim() : text;
                                    content = content.replace(/Plan execution finished successfully\. Final Output:?[\s\n]*/g, '').trim();
                                    const time = new Date(log.timestamp);
                                    const timeStr = time.toLocaleString(undefined, { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit', hour12: true });

                                    return (
                                        <details key={i} className="group bg-slate-900/50 rounded-xl border border-slate-800/60 overflow-hidden hover:border-indigo-500/30 transition-colors">
                                            <summary className="px-5 py-4 cursor-pointer flex items-center justify-between hover:bg-slate-800/30 transition-colors">
                                                <div className="flex items-center gap-3">
                                                    <span className="text-indigo-400 text-lg">⏰</span>
                                                    <span className="text-sm font-semibold text-white">{jobName}</span>
                                                </div>
                                                <span className="text-[11px] text-slate-500 font-mono">{timeStr}</span>
                                            </summary>
                                            <div className="px-5 pb-5 border-t border-slate-800/40">
                                                <div className="prose prose-invert prose-sm max-w-none mt-4 prose-p:leading-relaxed prose-pre:bg-slate-950/80 prose-pre:border prose-pre:border-slate-800 text-[14px]">
                                                    <ReactMarkdown
                                                        remarkPlugins={[remarkGfm]}
                                                        components={{
                                                            table: ({ node, ...props }) => (
                                                                <div className="overflow-x-auto my-4 rounded-xl border border-indigo-700/50 bg-indigo-950/50 shadow-lg">
                                                                    <table className="min-w-full divide-y divide-indigo-700/50 text-sm" {...props} />
                                                                </div>
                                                            ),
                                                            thead: ({ node, ...props }) => <thead className="bg-indigo-900/50" {...props} />,
                                                            th: ({ node, ...props }) => <th className="px-4 py-3 text-left font-semibold text-indigo-200 tracking-wide bg-indigo-900/40 first:rounded-tl-lg last:rounded-tr-lg" {...props} />,
                                                            td: ({ node, ...props }) => <td className="px-4 py-3 border-t border-indigo-700/40 text-slate-300" {...props} />,
                                                            p: ({ node, ...props }) => <p className="mb-2.5 last:mb-0" {...props} />,
                                                            a: ({ node, ...props }) => <a className="text-indigo-400 hover:text-indigo-300 underline underline-offset-2 decoration-indigo-500/30 hover:decoration-indigo-400 transition-all font-medium" {...props} />
                                                        }}
                                                    >{content}</ReactMarkdown>
                                                </div>
                                            </div>
                                        </details>
                                    );
                                })}
                        </div>
                    );
                })()}
            </div>
        </div>
    );
}

// ─── Workflows View ─────────────────────────────────────────────────────────

function WorkflowsView() {
    const [workflows, setWorkflows] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [expanded, setExpanded] = useState<string | null>(null);
    const [runResult, setRunResult] = useState<any | null>(null);
    const [showCreate, setShowCreate] = useState(false);
    const [editingId, setEditingId] = useState<string | null>(null);
    const [newWf, setNewWf] = useState({ name: '', steps: [{ id: 's1', action: 'agent_task', prompt: '' }] as any[] });

    const fetchWorkflows = () => {
        apiFetch('/api/workflows').then(r => r.json()).then(d => {
            setWorkflows(d.workflows || []);
            setLoading(false);
        }).catch(() => setLoading(false));
    };

    useEffect(() => { fetchWorkflows(); }, []);

    const deleteWorkflow = (id: string) => {
        apiFetch(`/api/workflows/${id}`, { method: 'DELETE' }).then(() => fetchWorkflows());
    };

    const runWorkflow = async (id: string) => {
        setRunResult({ running: true, workflowId: id });
        try {
            const res = await apiFetch(`/api/workflows/${id}/run`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({}) });
            const data = await res.json();
            setRunResult(data.result || data);
        } catch (e: any) {
            setRunResult({ error: e.message });
        }
    };

    const toggleStatus = async (wf: any) => {
        const updated = { ...wf, status: wf.status === 'enabled' ? 'disabled' : 'enabled' };
        await apiFetch(`/api/workflows/${wf.id}`, {
            method: 'PUT', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(updated)
        });
        fetchWorkflows();
    };

    const createWorkflow = async () => {
        if (!newWf.name) return;
        if (editingId) {
            // Update existing
            const existing = workflows.find(w => w.id === editingId);
            await apiFetch(`/api/workflows/${editingId}`, {
                method: 'PUT', headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ ...existing, name: newWf.name, steps: newWf.steps })
            });
        } else {
            // Create new
            const id = newWf.name.toLowerCase().replace(/[^a-z0-9]+/g, '-');
            await apiFetch('/api/workflows', {
                method: 'POST', headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ id, name: newWf.name, status: 'enabled', trigger: { type: 'manual' }, steps: newWf.steps })
            });
        }
        setShowCreate(false);
        setEditingId(null);
        setNewWf({ name: '', steps: [{ id: 's1', action: 'agent_task', prompt: '' }] });
        fetchWorkflows();
    };

    const editWorkflow = (wf: any) => {
        setNewWf({ name: wf.name, steps: wf.steps || [] });
        setEditingId(wf.id);
        setShowCreate(true);
        setExpanded(null);
    };

    const addStep = () => {
        const num = newWf.steps.length + 1;
        setNewWf({ ...newWf, steps: [...newWf.steps, { id: `s${num}`, action: 'agent_task', prompt: '' }] });
    };

    const updateStep = (idx: number, field: string, value: string) => {
        const steps = [...newWf.steps];
        steps[idx] = { ...steps[idx], [field]: value };
        setNewWf({ ...newWf, steps });
    };

    const removeStep = (idx: number) => {
        setNewWf({ ...newWf, steps: newWf.steps.filter((_: any, i: number) => i !== idx) });
    };

    return (
        <div className="flex-1 p-8 fade-in overflow-y-auto">
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h2 className="text-2xl font-bold text-white">Workflow Chains</h2>
                    <p className="text-slate-400 text-sm mt-1">Multi-step task pipelines that chain agent actions together.</p>
                </div>
                <div className="flex gap-2">
                    <button onClick={() => { setShowCreate(!showCreate); setEditingId(null); setNewWf({ name: '', steps: [{ id: 's1', action: 'agent_task', prompt: '' }] }); }} className="flex items-center gap-2 px-4 py-2 bg-indigo-600/20 text-indigo-400 rounded-lg hover:bg-indigo-600/30 transition ring-1 ring-indigo-500/30">
                        <Plus className="w-4 h-4" /> Create Workflow
                    </button>
                    <button onClick={fetchWorkflows} className="flex items-center gap-2 px-4 py-2 bg-slate-700/50 text-slate-300 rounded-lg hover:bg-slate-700 transition">
                        <RefreshCw className="w-4 h-4" /> Refresh
                    </button>
                </div>
            </div>

            {/* Create Form */}
            {showCreate && (
                <div className={`bg-slate-800/70 border ${editingId ? 'border-cyan-500/30' : 'border-indigo-500/30'} rounded-xl p-5 mb-6`}>
                    <h3 className={`text-sm font-semibold ${editingId ? 'text-cyan-400' : 'text-indigo-400'} mb-4`}>{editingId ? `Editing: ${newWf.name}` : 'New Workflow'}</h3>
                    <input
                        type="text" placeholder="Workflow name (e.g. Market Research Pipeline)"
                        value={newWf.name} onChange={e => setNewWf({ ...newWf, name: e.target.value })}
                        className="w-full bg-slate-900/50 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white mb-4 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                    />
                    <div className="text-xs text-slate-500 uppercase tracking-wider mb-2">Steps</div>
                    {newWf.steps.map((step: any, i: number) => (
                        <div key={i} className="flex gap-2 mb-2">
                            <span className="text-slate-600 text-xs font-mono py-2 w-6">{i + 1}.</span>
                            <select value={step.action} onChange={e => updateStep(i, 'action', e.target.value)}
                                className="bg-slate-900/50 border border-slate-700 rounded-lg px-2 py-2 text-xs text-white focus:outline-none">
                                <option value="agent_task">Agent Task</option>
                                <option value="deliver">Deliver</option>
                                <option value="condition">Condition</option>
                                <option value="skill">Skill</option>
                            </select>
                            {step.action === 'agent_task' && (
                                <input type="text" placeholder="Prompt for the agent..." value={step.prompt || ''}
                                    onChange={e => updateStep(i, 'prompt', e.target.value)}
                                    className="flex-1 bg-slate-900/50 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:ring-1 focus:ring-indigo-500" />
                            )}
                            {step.action === 'deliver' && (
                                <>
                                    <select value={step.channel || 'whatsapp'} onChange={e => updateStep(i, 'channel', e.target.value)}
                                        className="bg-slate-900/50 border border-slate-700 rounded-lg px-2 py-2 text-xs text-white focus:outline-none">
                                        <option value="whatsapp">WhatsApp</option>
                                        <option value="email">Email</option>
                                    </select>
                                    <input type="text" placeholder="Target (default, group name, or email)" value={step.target || ''}
                                        onChange={e => updateStep(i, 'target', e.target.value)}
                                        className="flex-1 bg-slate-900/50 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white focus:outline-none" />
                                </>
                            )}
                            {step.action === 'condition' && (
                                <input type="text" placeholder="e.g. output.includes('urgent')" value={step.if || ''}
                                    onChange={e => updateStep(i, 'if', e.target.value)}
                                    className="flex-1 bg-slate-900/50 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white focus:outline-none" />
                            )}
                            {newWf.steps.length > 1 && (
                                <button onClick={() => removeStep(i)} className="text-red-400/50 hover:text-red-400"><X className="w-4 h-4" /></button>
                            )}
                        </div>
                    ))}
                    <div className="flex gap-2 mt-3">
                        <button onClick={addStep} className="px-3 py-1.5 bg-slate-700/50 text-slate-400 rounded-lg text-xs hover:bg-slate-700 transition">+ Add Step</button>
                        <button onClick={createWorkflow} className={`px-4 py-1.5 ${editingId ? 'bg-cyan-600 hover:bg-cyan-700' : 'bg-indigo-600 hover:bg-indigo-700'} text-white rounded-lg text-xs font-medium transition`}>{editingId ? 'Save Changes' : 'Create Workflow'}</button>
                        <button onClick={() => { setShowCreate(false); setEditingId(null); }} className="px-3 py-1.5 text-slate-500 text-xs hover:text-slate-300 transition">Cancel</button>
                    </div>
                </div>
            )}

            {/* Stats */}
            <div className="grid grid-cols-3 gap-4 mb-6">
                <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-4">
                    <div className="text-2xl font-bold text-emerald-400">{workflows.length}</div>
                    <div className="text-xs text-slate-500 uppercase tracking-wider">Total Workflows</div>
                </div>
                <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-4">
                    <div className="text-2xl font-bold text-blue-400">{workflows.filter(w => w.status === 'enabled').length}</div>
                    <div className="text-xs text-slate-500 uppercase tracking-wider">Active</div>
                </div>
                <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-4">
                    <div className="text-2xl font-bold text-orange-400">{workflows.filter(w => w.lastRunStatus === 'failed').length}</div>
                    <div className="text-xs text-slate-500 uppercase tracking-wider">Last Failed</div>
                </div>
            </div>

            {loading ? (
                <div className="text-slate-400 text-center py-8">Loading workflows...</div>
            ) : workflows.length === 0 ? (
                <div className="bg-slate-800/30 border border-slate-700/30 rounded-xl p-12 text-center">
                    <Workflow className="w-12 h-12 text-slate-600 mx-auto mb-4" />
                    <h3 className="text-lg font-semibold text-slate-300 mb-2">No Workflows Yet</h3>
                    <p className="text-slate-500 text-sm">Create workflows via the API or agent chat to automate multi-step task chains.</p>
                </div>
            ) : (
                <div className="space-y-3">
                    {workflows.map((wf: any) => (
                        <div key={wf.id} className="bg-slate-800/50 border border-slate-700/50 rounded-xl overflow-hidden">
                            <div className="p-4 flex items-center justify-between cursor-pointer hover:bg-slate-800/70 transition" onClick={() => setExpanded(expanded === wf.id ? null : wf.id)}>
                                <div className="flex items-center gap-3">
                                    <Workflow className="w-5 h-5 text-indigo-400" />
                                    <div>
                                        <div className="font-semibold text-white">{wf.name}</div>
                                        <div className="text-xs text-slate-500">{wf.description || `${wf.steps?.length || 0} steps · Trigger: ${wf.trigger?.type || 'manual'}`}</div>
                                    </div>
                                </div>
                                <div className="flex items-center gap-2">
                                    <span className={`px-2 py-0.5 rounded text-xs font-medium ${wf.status === 'enabled' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-slate-600/30 text-slate-500'}`}>
                                        {wf.status?.toUpperCase()}
                                    </span>
                                    {wf.lastRunStatus && (
                                        <span className={`px-2 py-0.5 rounded text-xs ${wf.lastRunStatus === 'success' ? 'bg-green-500/20 text-green-400' : wf.lastRunStatus === 'failed' ? 'bg-red-500/20 text-red-400' : 'bg-yellow-500/20 text-yellow-400'}`}>
                                            {wf.lastRunStatus}
                                        </span>
                                    )}
                                </div>
                            </div>
                            {expanded === wf.id && (
                                <div className="border-t border-slate-700/50 p-4 bg-slate-900/30">
                                    <div className="text-xs text-slate-500 mb-3 uppercase tracking-wider">Pipeline Steps</div>
                                    <div className="space-y-2 mb-4">
                                        {(wf.steps || []).map((step: any, i: number) => (
                                            <div key={step.id} className="flex items-center gap-3 text-sm">
                                                <span className="text-slate-600 font-mono text-xs w-6">{i + 1}.</span>
                                                <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                                                    step.action === 'agent_task' ? 'bg-blue-500/20 text-blue-400' :
                                                    step.action === 'condition' ? 'bg-yellow-500/20 text-yellow-400' :
                                                    step.action === 'deliver' ? 'bg-green-500/20 text-green-400' :
                                                    'bg-purple-500/20 text-purple-400'
                                                }`}>{step.action}</span>
                                                <span className="text-slate-300 truncate">{step.prompt || step.if || step.template || step.skillName || '—'}</span>
                                            </div>
                                        ))}
                                    </div>
                                    {wf.lastRunAt && (
                                        <div className="text-xs text-slate-500 mb-3">Last run: {new Date(wf.lastRunAt).toLocaleString()}</div>
                                    )}
                                    <div className="flex gap-2">
                                        <button onClick={() => runWorkflow(wf.id)} className="px-3 py-1.5 bg-indigo-600/20 text-indigo-400 rounded-lg text-xs font-medium hover:bg-indigo-600/30 transition flex items-center gap-1">
                                            <Play className="w-3 h-3" /> Run Now
                                        </button>
                                        <button onClick={() => editWorkflow(wf)} className="px-3 py-1.5 bg-cyan-600/20 text-cyan-400 rounded-lg text-xs font-medium hover:bg-cyan-600/30 transition flex items-center gap-1">
                                            <Settings className="w-3 h-3" /> Edit
                                        </button>
                                        <button onClick={() => toggleStatus(wf)} className="px-3 py-1.5 bg-slate-700/50 text-slate-400 rounded-lg text-xs font-medium hover:bg-slate-700 transition">
                                            {wf.status === 'enabled' ? 'Disable' : 'Enable'}
                                        </button>
                                        <button onClick={() => deleteWorkflow(wf.id)} className="px-3 py-1.5 bg-red-500/10 text-red-400 rounded-lg text-xs font-medium hover:bg-red-500/20 transition flex items-center gap-1">
                                            <Trash className="w-3 h-3" /> Delete
                                        </button>
                                    </div>
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            )}

            {/* Run Result Display */}
            {runResult && (
                <div className="mt-6 bg-slate-800/50 border border-slate-700/50 rounded-xl p-4">
                    <div className="flex items-center justify-between mb-2">
                        <h3 className="text-sm font-semibold text-white">Run Result</h3>
                        <button onClick={() => setRunResult(null)} className="text-slate-500 hover:text-slate-300"><X className="w-4 h-4" /></button>
                    </div>
                    {runResult.running ? (
                        <div className="text-yellow-400 text-sm">⏳ Workflow executing...</div>
                    ) : runResult.error ? (
                        <div className="text-red-400 text-sm">{runResult.error}</div>
                    ) : (
                        <div className="text-sm">
                            <div className={`font-medium ${runResult.status === 'success' ? 'text-green-400' : 'text-red-400'}`}>
                                {runResult.status?.toUpperCase()} — {runResult.totalDurationMs}ms
                            </div>
                            <div className="mt-2 space-y-1">
                                {(runResult.stepResults || []).map((sr: any) => (
                                    <div key={sr.stepId} className="flex items-center gap-2 text-xs">
                                        <span className={sr.status === 'success' ? 'text-green-400' : 'text-red-400'}>{sr.status === 'success' ? '✓' : '✗'}</span>
                                        <span className="text-slate-400">{sr.stepId}</span>
                                        <span className="text-slate-500 truncate">{sr.output?.substring(0, 100)}</span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}

// ─── Event Triggers View ────────────────────────────────────────────────────

function EventTriggersView() {
    const [triggers, setTriggers] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [showCreate, setShowCreate] = useState(false);
    const [editingId, setEditingId] = useState<string | null>(null);
    const [newTrig, setNewTrig] = useState({ name: '', source: 'gmail', filterKey: 'from', filterValue: '', actionType: 'agent_task', actionPrompt: '', actionWorkflowId: '' });

    const fetchTriggers = () => {
        apiFetch('/api/events/triggers').then(r => r.json()).then(d => {
            setTriggers(d.triggers || []);
            setLoading(false);
        }).catch(() => setLoading(false));
    };

    useEffect(() => { fetchTriggers(); }, []);

    const deleteTrigger = (id: string) => {
        apiFetch(`/api/events/triggers/${id}`, { method: 'DELETE' }).then(() => fetchTriggers());
    };

    const toggleStatus = async (t: any) => {
        const updated = { ...t, status: t.status === 'enabled' ? 'disabled' : 'enabled' };
        await apiFetch('/api/events/triggers', {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(updated)
        });
        fetchTriggers();
    };

    const sourceColors: Record<string, string> = {
        gmail: 'bg-red-500/20 text-red-400',
        whatsapp: 'bg-green-500/20 text-green-400',
        webhook: 'bg-purple-500/20 text-purple-400',
        cron_result: 'bg-blue-500/20 text-blue-400',
    };

    const createTrigger = async () => {
        if (!newTrig.name) return;
        const filter: any = {};
        if (newTrig.filterKey && newTrig.filterValue) filter[newTrig.filterKey] = newTrig.filterValue;
        const action: any = newTrig.actionType === 'workflow'
            ? { type: 'workflow', workflowId: newTrig.actionWorkflowId }
            : { type: 'agent_task', prompt: newTrig.actionPrompt };
        if (editingId) {
            // Update existing
            const existing = triggers.find(t => t.id === editingId);
            await apiFetch('/api/events/triggers', {
                method: 'POST', headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ ...existing, name: newTrig.name, source: newTrig.source, filter, action })
            });
        } else {
            // Create new
            const id = newTrig.name.toLowerCase().replace(/[^a-z0-9]+/g, '-');
            await apiFetch('/api/events/triggers', {
                method: 'POST', headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ id, name: newTrig.name, source: newTrig.source, status: 'enabled', filter, action })
            });
        }
        setShowCreate(false);
        setEditingId(null);
        setNewTrig({ name: '', source: 'gmail', filterKey: 'from', filterValue: '', actionType: 'agent_task', actionPrompt: '', actionWorkflowId: '' });
        fetchTriggers();
    };

    const editTrigger = (t: any) => {
        const filterEntries = Object.entries(t.filter || {});
        const fKey = filterEntries.length > 0 ? filterEntries[0][0] as string : 'from';
        const fVal = filterEntries.length > 0 ? filterEntries[0][1] as string : '';
        setNewTrig({
            name: t.name,
            source: t.source || 'gmail',
            filterKey: fKey,
            filterValue: fVal,
            actionType: t.action?.type || 'agent_task',
            actionPrompt: t.action?.prompt || '',
            actionWorkflowId: t.action?.workflowId || ''
        });
        setEditingId(t.id);
        setShowCreate(true);
    };

    return (
        <div className="flex-1 p-8 fade-in overflow-y-auto">
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h2 className="text-2xl font-bold text-white">Event Triggers</h2>
                    <p className="text-slate-400 text-sm mt-1">React to real-time events — emails, messages, webhooks, and cron results.</p>
                </div>
                <div className="flex gap-2">
                    <button onClick={() => { setShowCreate(!showCreate); setEditingId(null); setNewTrig({ name: '', source: 'gmail', filterKey: 'from', filterValue: '', actionType: 'agent_task', actionPrompt: '', actionWorkflowId: '' }); }} className="flex items-center gap-2 px-4 py-2 bg-amber-600/20 text-amber-400 rounded-lg hover:bg-amber-600/30 transition ring-1 ring-amber-500/30">
                        <Plus className="w-4 h-4" /> Create Trigger
                    </button>
                    <button onClick={fetchTriggers} className="flex items-center gap-2 px-4 py-2 bg-slate-700/50 text-slate-300 rounded-lg hover:bg-slate-700 transition">
                        <RefreshCw className="w-4 h-4" /> Refresh
                    </button>
                </div>
            </div>

            {/* Create Form */}
            {showCreate && (
                <div className={`bg-slate-800/70 border ${editingId ? 'border-cyan-500/30' : 'border-amber-500/30'} rounded-xl p-5 mb-6`}>
                    <h3 className={`text-sm font-semibold ${editingId ? 'text-cyan-400' : 'text-amber-400'} mb-4`}>{editingId ? `Editing: ${newTrig.name}` : 'New Event Trigger'}</h3>
                    <input
                        type="text" placeholder="Trigger name (e.g. Urgent Email Handler)"
                        value={newTrig.name} onChange={e => setNewTrig({ ...newTrig, name: e.target.value })}
                        className="w-full bg-slate-900/50 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white mb-4 focus:outline-none focus:ring-1 focus:ring-amber-500"
                    />
                    <div className="grid grid-cols-2 gap-4 mb-4">
                        <div>
                            <div className="text-xs text-slate-500 uppercase tracking-wider mb-1">Event Source</div>
                            <select value={newTrig.source} onChange={e => setNewTrig({ ...newTrig, source: e.target.value })}
                                className="w-full bg-slate-900/50 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none">
                                <option value="gmail">Gmail</option>
                                <option value="whatsapp">WhatsApp</option>
                                <option value="webhook">Webhook</option>
                                <option value="cron_result">Cron Result</option>
                            </select>
                        </div>
                        <div>
                            <div className="text-xs text-slate-500 uppercase tracking-wider mb-1">Filter</div>
                            <div className="flex gap-2">
                                <select value={newTrig.filterKey} onChange={e => setNewTrig({ ...newTrig, filterKey: e.target.value })}
                                    className="bg-slate-900/50 border border-slate-700 rounded-lg px-2 py-2 text-xs text-white focus:outline-none">
                                    <option value="from">from</option>
                                    <option value="subject_contains">subject_contains</option>
                                    <option value="body_contains">body_contains</option>
                                    <option value="topic">topic</option>
                                </select>
                                <input type="text" placeholder="e.g. *@google.com" value={newTrig.filterValue}
                                    onChange={e => setNewTrig({ ...newTrig, filterValue: e.target.value })}
                                    className="flex-1 bg-slate-900/50 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white focus:outline-none" />
                            </div>
                        </div>
                    </div>
                    <div className="mb-4">
                        <div className="text-xs text-slate-500 uppercase tracking-wider mb-1">Action</div>
                        <div className="flex gap-2 mb-2">
                            <select value={newTrig.actionType} onChange={e => setNewTrig({ ...newTrig, actionType: e.target.value })}
                                className="bg-slate-900/50 border border-slate-700 rounded-lg px-2 py-2 text-xs text-white focus:outline-none">
                                <option value="agent_task">Agent Task</option>
                                <option value="workflow">Run Workflow</option>
                            </select>
                            {newTrig.actionType === 'agent_task' ? (
                                <input type="text" placeholder="Prompt for the agent..." value={newTrig.actionPrompt}
                                    onChange={e => setNewTrig({ ...newTrig, actionPrompt: e.target.value })}
                                    className="flex-1 bg-slate-900/50 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white focus:outline-none" />
                            ) : (
                                <input type="text" placeholder="Workflow ID (e.g. breaking-news-alert)" value={newTrig.actionWorkflowId}
                                    onChange={e => setNewTrig({ ...newTrig, actionWorkflowId: e.target.value })}
                                    className="flex-1 bg-slate-900/50 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white focus:outline-none" />
                            )}
                        </div>
                    </div>
                    <div className="flex gap-2">
                        <button onClick={createTrigger} className={`px-4 py-1.5 ${editingId ? 'bg-cyan-600 hover:bg-cyan-700' : 'bg-amber-600 hover:bg-amber-700'} text-white rounded-lg text-xs font-medium transition`}>{editingId ? 'Save Changes' : 'Create Trigger'}</button>
                        <button onClick={() => { setShowCreate(false); setEditingId(null); }} className="px-3 py-1.5 text-slate-500 text-xs hover:text-slate-300 transition">Cancel</button>
                    </div>
                </div>
            )}

            {/* Stats */}
            <div className="grid grid-cols-4 gap-4 mb-6">
                <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-4">
                    <div className="text-2xl font-bold text-emerald-400">{triggers.length}</div>
                    <div className="text-xs text-slate-500 uppercase tracking-wider">Total Triggers</div>
                </div>
                <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-4">
                    <div className="text-2xl font-bold text-blue-400">{triggers.filter(t => t.status === 'enabled').length}</div>
                    <div className="text-xs text-slate-500 uppercase tracking-wider">Active</div>
                </div>
                <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-4">
                    <div className="text-2xl font-bold text-orange-400">{triggers.reduce((sum: number, t: any) => sum + (t.fireCount || 0), 0)}</div>
                    <div className="text-xs text-slate-500 uppercase tracking-wider">Total Fires</div>
                </div>
                <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-4">
                    <div className="text-2xl font-bold text-purple-400">{new Set(triggers.map((t: any) => t.source)).size}</div>
                    <div className="text-xs text-slate-500 uppercase tracking-wider">Sources</div>
                </div>
            </div>

            {loading ? (
                <div className="text-slate-400 text-center py-8">Loading triggers...</div>
            ) : triggers.length === 0 ? (
                <div className="bg-slate-800/30 border border-slate-700/30 rounded-xl p-12 text-center">
                    <Zap className="w-12 h-12 text-slate-600 mx-auto mb-4" />
                    <h3 className="text-lg font-semibold text-slate-300 mb-2">No Event Triggers Yet</h3>
                    <p className="text-slate-500 text-sm">Create triggers via the API or agent chat to react to Gmail, WhatsApp, webhooks, and cron results.</p>
                </div>
            ) : (
                <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl overflow-hidden">
                    <table className="w-full">
                        <thead>
                            <tr className="border-b border-slate-700/50">
                                <th className="text-left text-xs text-slate-500 uppercase tracking-wider p-3">Name</th>
                                <th className="text-left text-xs text-slate-500 uppercase tracking-wider p-3">Source</th>
                                <th className="text-left text-xs text-slate-500 uppercase tracking-wider p-3">Filter</th>
                                <th className="text-left text-xs text-slate-500 uppercase tracking-wider p-3">Action</th>
                                <th className="text-left text-xs text-slate-500 uppercase tracking-wider p-3">Fires</th>
                                <th className="text-left text-xs text-slate-500 uppercase tracking-wider p-3">Status</th>
                                <th className="text-right text-xs text-slate-500 uppercase tracking-wider p-3">Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {triggers.map((t: any) => (
                                <tr key={t.id} className="border-b border-slate-700/30 hover:bg-slate-800/70 transition">
                                    <td className="p-3">
                                        <div className="font-medium text-white text-sm">{t.name}</div>
                                        {t.description && <div className="text-xs text-slate-500">{t.description}</div>}
                                    </td>
                                    <td className="p-3">
                                        <span className={`px-2 py-0.5 rounded text-xs font-medium ${sourceColors[t.source] || 'bg-slate-600/30 text-slate-400'}`}>
                                            {t.source?.toUpperCase()}
                                        </span>
                                    </td>
                                    <td className="p-3 text-xs text-slate-400 font-mono">
                                        {Object.entries(t.filter || {}).map(([k, v]) => `${k}: ${v}`).join(', ') || '—'}
                                    </td>
                                    <td className="p-3 text-xs text-slate-400">
                                        {t.action?.type === 'workflow' ? `→ Workflow: ${t.action.workflowId}` : `→ Agent Task`}
                                    </td>
                                    <td className="p-3 text-sm text-slate-300">{t.fireCount || 0}</td>
                                    <td className="p-3">
                                        <button onClick={() => toggleStatus(t)} className={`px-2 py-0.5 rounded text-xs font-medium cursor-pointer transition ${t.status === 'enabled' ? 'bg-emerald-500/20 text-emerald-400 hover:bg-emerald-500/30' : 'bg-slate-600/30 text-slate-500 hover:bg-slate-600/50'}`}>
                                            {t.status?.toUpperCase()}
                                        </button>
                                    </td>
                                    <td className="p-3 text-right">
                                        <div className="flex items-center gap-2 justify-end">
                                            <button onClick={() => editTrigger(t)} className="text-cyan-400/60 hover:text-cyan-400 transition">
                                                <Settings className="w-4 h-4" />
                                            </button>
                                            <button onClick={() => deleteTrigger(t.id)} className="text-red-400/60 hover:text-red-400 transition">
                                                <Trash className="w-4 h-4" />
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}

            {/* Info Card */}
            <div className="mt-6 bg-slate-800/30 border border-slate-700/30 rounded-xl p-4">
                <h4 className="text-sm font-semibold text-slate-300 mb-2">Supported Event Sources</h4>
                <div className="grid grid-cols-2 gap-3 text-xs">
                    <div className="flex items-center gap-2"><span className="px-2 py-0.5 rounded bg-red-500/20 text-red-400 font-medium">GMAIL</span> <span className="text-slate-500">Incoming emails via webhook</span></div>
                    <div className="flex items-center gap-2"><span className="px-2 py-0.5 rounded bg-green-500/20 text-green-400 font-medium">WHATSAPP</span> <span className="text-slate-500">Message pattern matching</span></div>
                    <div className="flex items-center gap-2"><span className="px-2 py-0.5 rounded bg-purple-500/20 text-purple-400 font-medium">WEBHOOK</span> <span className="text-slate-500">POST /api/webhooks/trigger</span></div>
                    <div className="flex items-center gap-2"><span className="px-2 py-0.5 rounded bg-blue-500/20 text-blue-400 font-medium">CRON_RESULT</span> <span className="text-slate-500">After cron job completion</span></div>
                </div>
            </div>
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
    type TabName = 'overview' | 'channels' | 'sessions' | 'usage' | 'chat' | 'agents' | 'skills' | 'workflows' | 'events' | 'logs' | 'flow' | 'cron' | 'processes';
    const [activeTab, setActiveTab] = useState<TabName>('chat');
    const [configuredChannel, setConfiguredChannel] = useState<string | null>(null);
    const [logs, setLogs] = useState<LogMessage[]>([]);
    const [flowEvents, setFlowEvents] = useState<AgentFlowEvent[]>([]);
    const [config, setConfig] = useState({ provider: 'Loading...', status: 'connecting' });
    const [skills, setSkills] = useState<string[]>([]);
    const [catalog, setCatalog] = useState<any>(null);
    const [agents, setAgents] = useState<any[]>([]);
    const [alerts, setAlerts] = useState<{ id: number, message: string }[]>([]);
    const [chatInput, setChatInput] = useState('');
    const [chatHistory, setChatHistory] = useState<string[]>([]);
    const [historyIndex, setHistoryIndex] = useState(-1);
    const [isTyping, setIsTyping] = useState(false);
    // Ref to prevent late-arriving log messages from re-locking chat after task completes
    const chatDoneRef = useRef(true);
    const [isVerbose, setIsVerbose] = useState(false);
    const scrollRef = useRef<HTMLDivElement>(null);
    const chatEndRef = useRef<HTMLDivElement>(null);
    const wsRef = useRef<WebSocket | null>(null);

    // Theme state
    type ThemeMode = 'dark' | 'light' | 'system';
    const [theme, setTheme] = useState<ThemeMode>(() => {
        const saved = localStorage.getItem('openspider-theme');
        return (saved === 'dark' || saved === 'light' || saved === 'system') ? saved : 'dark';
    });

    useEffect(() => {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('openspider-theme', theme);
    }, [theme]);

    // Health state
    const [health, setHealth] = useState<{
        version: string;
        status: 'green' | 'amber' | 'red';
        uptime: number;
        memory: number;
        components: { whatsapp: string; llm: string; server: string; scheduler: string };
    } | null>(null);
    const [isHealthHovered, setIsHealthHovered] = useState(false);

    // Version update banner state
    const [updateInfo, setUpdateInfo] = useState<{
        current: string;
        latest: string;
        updateAvailable: boolean;
        releaseUrl?: string;
        releaseName?: string;
    } | null>(null);
    const [updateDismissed, setUpdateDismissed] = useState(false);

    useEffect(() => {
        const fetchHealth = () => {
            apiFetch('/api/health')
                .then(r => r.json())
                .then(data => setHealth(data))
                .catch(() => setHealth(prev => prev ? { ...prev, status: 'red' } : null));
        };
        fetchHealth();
        const interval = setInterval(fetchHealth, 30000);
        return () => clearInterval(interval);
    }, []);

    // Check for updates on mount
    useEffect(() => {
        apiFetch('/api/version-check')
            .then(r => r.json())
            .then(data => setUpdateInfo(data))
            .catch(() => {}); // Silently fail — not critical
    }, []);

    const formatUptime = (seconds: number) => {
        const d = Math.floor(seconds / 86400);
        const h = Math.floor((seconds % 86400) / 3600);
        const m = Math.floor((seconds % 3600) / 60);
        if (d > 0) return `${d}d ${h}h`;
        if (h > 0) return `${h}h ${m}m`;
        return `${m}m`;
    };

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
        apiFetch('/api/config')
            .then(r => r.json())
            .then(data => setConfig(prev => ({ ...prev, provider: data.provider })))
            .catch(e => console.error("Could not fetch config API", e));

        apiFetch('/api/skills')
            .then(r => r.json())
            .then(data => {
                setCatalog(data);
                setSkills((data.curated || []).map((s: any) => s.name));
            })
            .catch(e => console.error("Could not fetch skills API", e));

        // Fetch persisted cron execution logs so they survive dashboard refresh
        apiFetch('/api/cron/logs')
            .then(r => r.json())
            .then(data => {
                if (data.logs && Array.isArray(data.logs) && data.logs.length > 0) {
                    const cronEntries = data.logs.map((log: any) => ({
                        type: 'cron_result' as any,
                        data: `[Cron: ${log.jobName}] ${log.result}`,
                        timestamp: log.timestamp || new Date().toISOString()
                    }));
                    setLogs(prev => {
                        // Deduplicate by timestamp to avoid double-counting live + persisted
                        const existingTimestamps = new Set(prev.filter((l: any) => l.type === 'cron_result').map(l => l.timestamp));
                        const uniqueCronEntries = cronEntries.filter((e: any) => !existingTimestamps.has(e.timestamp));
                        return [...uniqueCronEntries, ...prev];
                    });
                }
            })
            .catch(e => console.error("Could not fetch cron logs", e));

        // Chat history is now served via WebSocket chatBuffer replay on connect
        // (the /api/chat/history endpoint re-creates timestamps from memory file strings
        //  which caused sort-order bugs due to timezone parsing inconsistencies)
        // apiFetch('/api/chat/history')
        //     .then(r => r.json())
        //     .then(data => {
        //         if (Array.isArray(data) && data.length > 0) {
        //             setLogs(prev => {
        //                 const existingIds = new Set(prev.map(p => p.timestamp + p.data));
        //                 const uniqueHistory = data.filter(d => !existingIds.has(d.timestamp + d.data));
        //                 return [...uniqueHistory, ...prev].slice(-5000);
        //             });
        //         }
        //     })
        //     .catch(e => console.error("Could not fetch chat history", e));

        fetchAgents();

        // Connect WebSocket for live logs (API key sent as query param for auth)
        const host = window.location.port === '5173' ? 'localhost:4001' : window.location.host;
        const wsUrl = window.location.protocol === 'https:'
            ? `wss://${host}/?apiKey=${API_KEY}`
            : `ws://${host}/?apiKey=${API_KEY}`;
        const ws = new WebSocket(wsUrl);

        ws.onmessage = (event) => {
            try {
                const msg = JSON.parse(event.data);
                if (msg.type === 'log') {
                    // Ignore cron-originated logs for typing state management
                    const isCronLog = typeof msg.data === 'string' && msg.data.startsWith('[CRON]');

                    if (msg.data.includes('Emulating human typing delay') || msg.data.includes('Sending structured request') || msg.data.includes('Sending structured generation')) {
                        // Only trigger typing if we haven't already received the chat_response
                        if (!isCronLog && (msg.data.includes('Sending structured request') || msg.data.includes('Sending structured generation')) && !chatDoneRef.current) {
                            setIsTyping(true);
                        }
                        return;
                    }

                    if (!isCronLog) {
                        // Only set typing=true if chat hasn't completed yet
                        if (msg.data.includes('[You]') && !chatDoneRef.current) setIsTyping(true);
                        if (msg.data.includes('[Agent]')) {
                            setIsTyping(false);
                            chatDoneRef.current = true; // Mark as done to block re-locking
                        }
                    }

                    setLogs(prev => [...prev.slice(-49999), msg]); // Keep last 50000 logs to prevent chat eviction
                } else if (msg.type === 'chat_response') {
                    setLogs(prev => [...prev.slice(-49999), { type: 'chat', data: `[Agent] ${msg.data}`, timestamp: msg.timestamp }]);
                    setIsTyping(false);
                    chatDoneRef.current = true; // Authoritative: task is done, prevent re-lock
                } else if (msg.type === 'chat') {
                    // Replayed chat buffer messages (user + agent conversation history)
                    // Deduplicate against existing logs to avoid double-display
                    setLogs(prev => {
                        const key = msg.timestamp + msg.data;
                        const alreadyExists = prev.some(p => (p.timestamp + p.data) === key);
                        if (alreadyExists) return prev;
                        return [...prev.slice(-49999), msg];
                    });
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
                } else if (msg.type === 'cron_result') {
                    // Show cron job results in the chat window
                    const cronLog = {
                        type: 'cron_result' as any,
                        data: `[Cron: ${msg.data.jobName}] ${msg.data.result}`,
                        timestamp: msg.data.timestamp || new Date().toISOString()
                    };
                    setLogs(prev => [...prev.slice(-49999), cronLog]);
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
            const res = await apiFetch('/api/agents');
            const data = await res.json();
            setAgents(data);
        } catch (e) {
            console.error("Could not fetch agents", e);
        }
    };

    const [attachments, setAttachments] = useState<Array<{ name: string; type: string; dataUrl: string; preview?: string }>>([]);
    const fileInputRef = useRef<HTMLInputElement>(null);

    const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        const files = e.target.files;
        if (!files) return;

        Array.from(files).forEach(file => {
            const reader = new FileReader();
            reader.onload = () => {
                const dataUrl = reader.result as string;
                setAttachments(prev => [...prev, {
                    name: file.name,
                    type: file.type,
                    dataUrl,
                    preview: file.type.startsWith('image/') ? dataUrl : undefined
                }]);
            };
            reader.readAsDataURL(file);
        });

        // Reset input so same file can be re-selected
        e.target.value = '';
    };

    const removeAttachment = (index: number) => {
        setAttachments(prev => prev.filter((_, i) => i !== index));
    };

    const sendChatMessage = () => {
        if ((!chatInput.trim() && attachments.length === 0) || !wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) return;

        const imageAttachments = attachments.filter(a => a.type.startsWith('image/'));
        const fileAttachments = attachments.filter(a => !a.type.startsWith('image/'));

        // Build message text
        let messageText = chatInput;

        const payload: any = { type: 'chat', text: messageText || 'Analyze the attached file(s).' };
        if (imageAttachments.length > 0) {
            payload.images = imageAttachments.map(a => a.dataUrl);
        }
        // Send non-image files so server can save them to disk for Worker access
        if (fileAttachments.length > 0) {
            payload.files = fileAttachments.map(a => ({ name: a.name, dataUrl: a.dataUrl }));
        }
        wsRef.current.send(JSON.stringify(payload));

        // Save to history
        setChatHistory(prev => {
            const updated = [chatInput, ...prev.filter(h => h !== chatInput)];
            return updated.slice(0, 50); // Keep max 50 entries
        });
        setHistoryIndex(-1);

        const attachmentLabel = attachments.length > 0 ? ` [📎 ${attachments.map(a => a.name).join(', ')}]` : '';
        setLogs(prev => [...prev, { type: 'chat', data: `[You] ${chatInput || 'Analyze attached image(s)'}${attachmentLabel}`, timestamp: new Date().toISOString() }]);
        setChatInput('');
        setAttachments([]);
        setIsTyping(true);
        chatDoneRef.current = false; // New message: allow typing state changes

        // Safety timeout: unlock input if agent never responds (e.g. crash, network issue)
        // Uses chatDoneRef to avoid unlocking if a response already arrived and re-locked for a new request
        const sentTimestamp = Date.now();
        setTimeout(() => {
            if (!chatDoneRef.current) {
                console.warn('[Chat] Safety timeout: unlocking input after 180s');
                setIsTyping(false);
                chatDoneRef.current = true;
            }
        }, 180_000);
    };

    const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendChatMessage();
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            if (chatHistory.length > 0) {
                const nextIndex = Math.min(historyIndex + 1, chatHistory.length - 1);
                setHistoryIndex(nextIndex);
                setChatInput(chatHistory[nextIndex]);
            }
        } else if (e.key === 'ArrowDown') {
            e.preventDefault();
            if (historyIndex > 0) {
                const nextIndex = historyIndex - 1;
                setHistoryIndex(nextIndex);
                setChatInput(chatHistory[nextIndex]);
            } else if (historyIndex === 0) {
                setHistoryIndex(-1);
                setChatInput('');
            }
        }
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
                        <div className="flex items-center gap-2">
                            <h1 className="text-xl font-bold text-white tracking-tight leading-tight">OpenSpider</h1>
                            {health && (
                                <span className="px-1.5 py-0.5 text-[9px] font-bold uppercase tracking-wider bg-gradient-to-r from-indigo-500/20 to-purple-500/20 text-indigo-300 border border-indigo-500/30 rounded-md">
                                    v{health.version}
                                </span>
                            )}
                        </div>
                        <p className="text-[11px] text-slate-400 font-semibold uppercase tracking-widest mt-0.5">Dashboard</p>
                        {/* Inline update hint in sidebar */}
                        {updateInfo?.updateAvailable && !updateDismissed && (
                            <a
                                href={updateInfo.releaseUrl || '#'}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-[10px] text-emerald-400 hover:text-emerald-300 mt-1 flex items-center gap-1 transition-colors"
                            >
                                <span className="inline-block w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                                v{updateInfo.latest} available
                            </a>
                        )}
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
                        <button
                            onClick={() => setActiveTab('workflows')}
                            className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 ${activeTab === 'workflows' ? 'bg-indigo-600/10 text-indigo-400 ring-1 ring-indigo-500/30 shadow-[0_4px_20px_-4px_rgba(99,102,241,0.2)]' : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'}`}
                        >
                            <Workflow className="w-4 h-4" />
                            Workflows
                        </button>
                        <button
                            onClick={() => setActiveTab('events')}
                            className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 ${activeTab === 'events' ? 'bg-amber-600/10 text-amber-400 ring-1 ring-amber-500/30 shadow-[0_4px_20px_-4px_rgba(245,158,11,0.2)]' : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'}`}
                        >
                            <Zap className="w-4 h-4" />
                            Event Triggers
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

                <div className="p-5 border-t border-slate-800/60 bg-slate-900/30 space-y-4">
                    {/* Theme Toggle */}
                    <div className="flex flex-col gap-2">
                        <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Appearance</span>
                        <div className="theme-toggle">
                            <button
                                onClick={() => setTheme('light')}
                                className={theme === 'light' ? 'active' : ''}
                                title="Light mode"
                            >
                                <Sun className="w-3.5 h-3.5 inline-block mr-1 relative -top-px" />Light
                            </button>
                            <button
                                onClick={() => setTheme('dark')}
                                className={theme === 'dark' ? 'active' : ''}
                                title="Dark mode"
                            >
                                <Moon className="w-3.5 h-3.5 inline-block mr-1 relative -top-px" />Dark
                            </button>
                            <button
                                onClick={() => setTheme('system')}
                                className={theme === 'system' ? 'active' : ''}
                                title="System preference"
                            >
                                <Monitor className="w-3.5 h-3.5 inline-block mr-1 relative -top-px" />Auto
                            </button>
                        </div>
                    </div>

                    <div className="h-px w-full bg-slate-800/60"></div>

                    {/* Health Status */}
                    {(() => {
                        const isConnected = config.status === 'connected';
                        const isGreen = isConnected && health?.status === 'green';
                        const isAmber = isConnected && health?.status === 'amber';

                        const statusLabel = !isConnected ? 'Disconnected' : isGreen ? 'All Systems Healthy' : isAmber ? 'Degraded' : 'Unreachable';

                        return (
                            <div
                                className="relative"
                                onMouseEnter={() => setIsHealthHovered(true)}
                                onMouseLeave={() => setIsHealthHovered(false)}
                            >
                                <div className="flex items-center justify-between cursor-pointer">
                                    <div className="flex items-center gap-2.5">
                                        <div className={`relative flex items-center justify-center w-8 h-8 rounded-lg ${isGreen ? 'bg-emerald-500/10 border border-emerald-500/30' :
                                                isAmber ? 'bg-amber-500/10 border border-amber-500/30' :
                                                    'bg-red-500/10 border border-red-500/30'
                                            }`}>
                                            <Heart className={`w-4 h-4 ${isGreen ? 'text-emerald-400' :
                                                    isAmber ? 'text-amber-400' :
                                                        'text-red-400'
                                                }`} />
                                            <span className={`absolute -top-0.5 -right-0.5 w-2.5 h-2.5 rounded-full border-2 border-slate-900 ${isGreen ? 'bg-emerald-400 health-pulse shadow-[0_0_8px_rgba(52,211,153,0.6)]' :
                                                    isAmber ? 'bg-amber-400 health-pulse shadow-[0_0_8px_rgba(251,191,36,0.6)]' :
                                                        'bg-red-500 animate-pulse shadow-[0_0_8px_rgba(239,68,68,0.6)]'
                                                }`}></span>
                                        </div>
                                        <div className="flex flex-col">
                                            <span className={`text-xs font-semibold ${isGreen ? 'text-emerald-400' :
                                                    isAmber ? 'text-amber-400' :
                                                        'text-red-400'
                                                }`}>
                                                {statusLabel}
                                            </span>
                                            <span className="text-[10px] text-slate-500 font-medium">
                                                {!isConnected ? 'Offline' : health ? `Uptime: ${formatUptime(health.uptime)}` : 'Connecting...'}
                                            </span>
                                        </div>
                                    </div>
                                </div>

                                {/* Health Detail Tooltip */}
                                {isHealthHovered && (
                                    <div className="absolute bottom-full left-0 right-0 mb-3 bg-slate-900/95 backdrop-blur-xl border border-slate-700/60 rounded-xl shadow-2xl p-4 z-50">
                                        <div className="absolute bottom-[-6px] left-6 w-3 h-3 bg-slate-900/95 border-r border-b border-slate-700/60 rotate-45"></div>
                                        <div className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-3">System Health</div>

                                        {!isConnected ? (
                                            <div className="text-xs text-red-400 mb-2 font-medium leading-relaxed">
                                                WebSocket Disconnected. Attempting to reconnect or the gateway engine is offline...
                                            </div>
                                        ) : health ? (
                                            <div className="space-y-2.5">
                                                <div className="flex items-center justify-between">
                                                    <span className="text-xs text-slate-400 flex items-center gap-2">
                                                        <Smartphone className="w-3 h-3" /> WhatsApp
                                                    </span>
                                                    <span className={`text-xs font-semibold flex items-center gap-1.5 ${health.components.whatsapp === 'connected' ? 'text-emerald-400' : 'text-amber-400'}`}>
                                                        <span className={`w-1.5 h-1.5 rounded-full ${health.components.whatsapp === 'connected' ? 'bg-emerald-400' : 'bg-amber-400'}`}></span>
                                                        {health.components.whatsapp}
                                                    </span>
                                                </div>
                                                <div className="flex items-center justify-between">
                                                    <span className="text-xs text-slate-400 flex items-center gap-2">
                                                        <Bot className="w-3 h-3" /> LLM
                                                    </span>
                                                    <span className="text-xs font-semibold text-emerald-400 flex items-center gap-1.5">
                                                        <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
                                                        {health.components.llm}
                                                    </span>
                                                </div>
                                                <div className="flex items-center justify-between">
                                                    <span className="text-xs text-slate-400 flex items-center gap-2">
                                                        <Server className="w-3 h-3" /> Server
                                                    </span>
                                                    <span className="text-xs font-semibold text-emerald-400 flex items-center gap-1.5">
                                                        <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
                                                        running
                                                    </span>
                                                </div>
                                                <div className="h-px w-full bg-slate-800/60 my-1"></div>
                                                <div className="flex items-center justify-between">
                                                    <span className="text-[10px] text-slate-500">Memory</span>
                                                    <span className="text-[10px] font-mono text-slate-300">{health.memory} MB</span>
                                                </div>
                                                <div className="flex items-center justify-between">
                                                    <span className="text-[10px] text-slate-500">Uptime</span>
                                                    <span className="text-[10px] font-mono text-slate-300">{formatUptime(health.uptime)}</span>
                                                </div>
                                            </div>
                                        ) : (
                                            <div className="text-xs text-slate-400">Loading components...</div>
                                        )}
                                    </div>
                                )}
                            </div>
                        );
                    })()}
                </div>
            </aside>

            {/* Main Content Area */}
            <main className="flex-1 flex flex-col h-screen overflow-hidden relative bg-slate-950/50">
                {/* Update Available Banner */}
                {updateInfo?.updateAvailable && !updateDismissed && (
                    <div className="relative px-6 py-3 bg-gradient-to-r from-emerald-500/10 via-teal-500/10 to-cyan-500/10 border-b border-emerald-500/20 flex items-center justify-between shrink-0 animate-in slide-in-from-top">
                        <div className="flex items-center gap-3">
                            <span className="flex items-center gap-1.5 px-2.5 py-1 bg-emerald-500/15 border border-emerald-500/30 rounded-full">
                                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                                <span className="text-[11px] font-bold text-emerald-400 uppercase tracking-wide">New Update</span>
                            </span>
                            <span className="text-sm text-slate-300">
                                <strong className="text-white">OpenSpider {updateInfo.releaseName || `v${updateInfo.latest}`}</strong> is available
                                <span className="text-slate-500 ml-1">(you're on v{updateInfo.current})</span>
                            </span>
                        </div>
                        <div className="flex items-center gap-3">
                            <a
                                href={updateInfo.releaseUrl || '#'}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-xs font-semibold text-emerald-400 hover:text-emerald-300 transition-colors underline underline-offset-2"
                            >
                                View Changes
                            </a>
                            <span className="text-[11px] text-slate-500 font-mono bg-slate-800/60 px-2 py-0.5 rounded border border-slate-700/50">
                                openspider update
                            </span>
                            <button
                                onClick={() => setUpdateDismissed(true)}
                                className="p-1 text-slate-500 hover:text-slate-300 transition-colors rounded-md hover:bg-slate-800/50"
                                title="Dismiss"
                            >
                                <X size={14} />
                            </button>
                        </div>
                    </div>
                )}
                {activeTab === 'chat' && (
                    <div className="flex-1 p-8 flex gap-8 overflow-hidden w-full h-full fade-in">

                        {/* Left Column: Logs */}
                        <section className="flex-1 flex flex-col bg-slate-900/50 rounded-xl border border-slate-800/60 overflow-hidden shadow-lg backdrop-blur-sm">
                            <div className="relative px-6 py-5 border-b border-slate-800/60 flex items-center justify-between bg-gradient-to-r from-slate-900 via-slate-900/95 to-slate-900">
                                {/* Gradient accent top bar */}
                                <div className="absolute top-0 inset-x-0 h-[2px] bg-gradient-to-r from-blue-500 via-fuchsia-500 to-purple-500" />
                                <div className="flex items-center gap-4">
                                    <div className="relative">
                                        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500/20 to-purple-500/20 border border-blue-500/20 flex items-center justify-center">
                                            <Radio className="w-5 h-5 text-blue-400" />
                                        </div>
                                        {/* Live pulse dot */}
                                        <span className="absolute -top-0.5 -right-0.5 w-3 h-3 bg-emerald-500 rounded-full border-2 border-slate-900 animate-pulse shadow-[0_0_8px_rgba(16,185,129,0.6)]" />
                                    </div>
                                    <div>
                                        <h2 className="text-lg font-bold text-white tracking-tight">Live Agent Communications</h2>
                                        <p className="text-[11px] text-slate-500 font-medium mt-0.5 tracking-wide">Real-time messaging · OpenSpider Agent Network</p>
                                    </div>
                                </div>
                                <button
                                    onClick={() => setIsVerbose(!isVerbose)}
                                    className={`px-4 py-2 text-xs font-bold uppercase tracking-widest rounded-lg transition-all duration-300 border ${isVerbose
                                        ? 'bg-fuchsia-500/10 text-fuchsia-400 hover:bg-fuchsia-500/20 border-fuchsia-500/30 shadow-[0_0_20px_rgba(217,70,239,0.15)]'
                                        : 'bg-slate-800/80 hover:bg-slate-700 text-slate-400 border-slate-700 hover:border-slate-600'
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
                                    let text = log.data.trim(); // MUST Be trimmed so \n doesn't break startsWith!
                                    // Fix: Strip [CRON] prefix if present so dashboard messages still render correctly
                                    if (text.startsWith('[CRON]')) text = text.substring(7).trim();
                                    // In non-verbose mode, strictly only show User questions and final Agent answers
                                    if (text.includes('[You]')) return true;

                                    if (text.includes('[Agent]')) {
                                        // Filter out intermediate [Agent] system/status updates
                                        if (text.includes('OpenSpider is processing')) return false;
                                        if (text.includes('Sending structured request')) return false;
                                        return true; // Keep genuine [Agent] dialogue responses
                                    }

                                    // Show cron job results only in verbose mode (they have their own Cron Jobs tab)
                                    // if ((log as any).type === 'cron_result') return true;

                                    // Hide absolutely everything else (raw JSON, [Server], [Web Chat], [Manager], [Worker], cron_result)
                                    return false;
                                })
                                // Sort by timestamp to fix out-of-order display from multiple async sources
                                .sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime())
                                // Deduplicate by content+timestamp key to prevent double rendering
                                .filter((log, idx, arr) => {
                                    if (idx === 0) return true;
                                    const key = log.timestamp + log.data;
                                    return !arr.slice(0, idx).some(prev => (prev.timestamp + prev.data) === key);
                                })
                                .map((log, i) => {
                                    let text = log.data.trim();
                                    // Fix: Strip [CRON] prefix for rendering too
                                    if (text.startsWith('[CRON]')) text = text.substring(7).trim();
                                    const isUser = text.includes('[You]');
                                    const isAgent = text.includes('[Agent]');
                                    const isCronResult = (log as any).type === 'cron_result';
                                    const isSystem = !isUser && !isAgent && !isCronResult;

                                    // Strip the prefixes
                                    let content = text;
                                    let cronJobName = '';
                                    if (isUser) {
                                        content = content.substring(content.indexOf('[You]') + 5).trim();
                                    } else if (isCronResult) {
                                        const cronMatch = content.match(/^\[Cron: (.+?)\] /);
                                        if (cronMatch) {
                                            cronJobName = cronMatch[1];
                                            content = content.substring(cronMatch[0].length).trim();
                                        }
                                        content = content.replace(/Plan execution finished successfully\. Final Output:?[\s\n]*/g, '').trim();
                                    } else if (isAgent) {
                                        content = content.substring(content.indexOf('[Agent]') + 7).trim();
                                        content = content.replace(/Plan execution finished successfully\. Final Output:?[\s\n]*/g, '').trim();
                                    }

                                    return (
                                        <div key={i} className={`flex w-full mb-6 ${isUser ? 'justify-end' : 'justify-start'}`}>
                                            <div className={`max-w-[95%] xl:max-w-[85%] 2xl:max-w-[75%] rounded-2xl px-5 py-3.5 shadow-md relative group ${isUser
                                                ? 'bg-gradient-to-br from-blue-500 to-blue-600 text-white rounded-br-sm shadow-blue-900/20'
                                                : isCronResult
                                                    ? 'bg-gradient-to-br from-indigo-950/90 to-purple-950/80 backdrop-blur-md border border-indigo-700/50 text-slate-200 rounded-bl-sm shadow-indigo-900/30'
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
                                                ) : isCronResult ? (
                                                    <div className="flex flex-col gap-1">
                                                        <span className="text-[10px] font-bold text-indigo-300 uppercase tracking-wider mb-1 pt-1 ml-1 flex items-center gap-1.5">
                                                            <span>⏰</span> Cron: {cronJobName}
                                                        </span>
                                                        <div className="prose prose-invert prose-sm max-w-none prose-p:leading-relaxed prose-pre:bg-slate-950/80 prose-pre:border prose-pre:border-slate-800 prose-pre:shadow-inner text-[14.5px]">
                                                            <ReactMarkdown
                                                                remarkPlugins={[remarkGfm]}
                                                                components={{
                                                                    table: ({ node, ...props }) => (
                                                                        <div className="overflow-x-auto my-4 rounded-xl border border-indigo-700/50 bg-indigo-950/50 shadow-lg">
                                                                            <table className="min-w-full divide-y divide-indigo-700/50 text-sm" {...props} />
                                                                        </div>
                                                                    ),
                                                                    thead: ({ node, ...props }) => <thead className="bg-indigo-900/50" {...props} />,
                                                                    th: ({ node, ...props }) => <th className="px-4 py-3 text-left font-semibold text-indigo-200 tracking-wide bg-indigo-900/40 first:rounded-tl-lg last:rounded-tr-lg" {...props} />,
                                                                    td: ({ node, ...props }) => <td className="px-4 py-3 border-t border-indigo-700/40 text-slate-300" {...props} />,
                                                                    tr: ({ node, ...props }) => <tr {...props} />,
                                                                    p: ({ node, ...props }) => <p className="mb-2.5 last:mb-0" {...props} />,
                                                                    code: ({ node, inline, ...props }: any) => inline
                                                                        ? <code className="bg-indigo-950/60 text-indigo-300 px-1.5 py-0.5 rounded text-[13px] border border-indigo-700/40" {...props} />
                                                                        : <code {...props} />,
                                                                    a: ({ node, ...props }) => <a className="text-indigo-400 hover:text-indigo-300 underline underline-offset-2 decoration-indigo-500/30 hover:decoration-indigo-400 transition-all font-medium" {...props} />
                                                                }}
                                                            >{content}</ReactMarkdown>
                                                        </div>
                                                    </div>
                                                ) : (
                                                    <div className="flex flex-col gap-1">
                                                        <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1 pt-1 ml-1 opacity-70">
                                                            {agents.length > 0 ? `${(agents[0] as any).emoji ? (agents[0] as any).emoji + ' ' : ''}${agents[0].name}` : 'OpenSpider'}
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
                            <div className="border-t border-slate-800/60 bg-slate-900">
                                {/* Attachment Preview Strip */}
                                {attachments.length > 0 && (
                                    <div className="px-4 pt-3 pb-1 flex flex-wrap gap-2">
                                        {attachments.map((att, idx) => (
                                            <div key={idx} className="relative group/att flex items-center gap-2 bg-slate-800/80 border border-slate-700/60 rounded-lg px-3 py-2 text-xs text-slate-300">
                                                {att.preview ? (
                                                    <img src={att.preview} alt={att.name} className="w-8 h-8 rounded object-cover border border-slate-600/50" />
                                                ) : (
                                                    <FileText className="w-4 h-4 text-slate-400 shrink-0" />
                                                )}
                                                <span className="max-w-[120px] truncate font-medium">{att.name}</span>
                                                <button
                                                    onClick={() => removeAttachment(idx)}
                                                    className="ml-1 p-0.5 rounded-full hover:bg-red-900/60 text-slate-500 hover:text-red-400 transition-colors"
                                                    title="Remove"
                                                >
                                                    <X className="w-3 h-3" />
                                                </button>
                                            </div>
                                        ))}
                                    </div>
                                )}

                                {/* Chat input bar — Gemini-style layout */}
                                <div className="px-4 pt-2 pb-3">
                                    <input
                                        ref={fileInputRef}
                                        type="file"
                                        multiple
                                        accept="*/*"
                                        className="hidden"
                                        onChange={handleFileSelect}
                                    />

                                    {/*
                                        Gemini layout: pill container with two rows
                                        Row 1 – textarea (full width, no icons)
                                        Row 2 – bottom toolbar: [📎 attach]  ·····  [Send ▶]
                                    */}
                                    <div className="flex flex-col bg-slate-900 border border-slate-700/60 rounded-2xl focus-within:ring-1 focus-within:ring-blue-500/60 focus-within:border-blue-500/40 transition-all overflow-hidden">

                                        {/* Row 1: textarea */}
                                        <textarea
                                            title="Chat Input"
                                            rows={3}
                                            value={chatInput}
                                            onChange={(e) => {
                                                setChatInput(e.target.value);
                                                e.target.style.height = 'auto';
                                                e.target.style.height = Math.min(e.target.scrollHeight, 200) + 'px';
                                            }}
                                            onKeyDown={handleKeyDown}
                                            placeholder="Assign a task to OpenSpider..."
                                            className="w-full bg-transparent px-4 pt-4 pb-2 text-sm text-slate-200 placeholder-slate-500 focus:outline-none resize-none leading-relaxed min-h-[80px] max-h-[200px] overflow-y-auto font-medium"
                                            disabled={config.status !== 'connected' || isTyping}
                                            style={{ height: '80px' }}
                                        />

                                        {/* Row 2: bottom toolbar — mirrors Gemini exactly */}
                                        <div className="flex items-center justify-between px-3 pb-3 pt-1">
                                            {/* Left: attach + future action icons */}
                                            <div className="flex items-center gap-1">
                                                <button
                                                    title="Attach file"
                                                    type="button"
                                                    onClick={() => fileInputRef.current?.click()}
                                                    disabled={config.status !== 'connected' || isTyping}
                                                    className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-full text-slate-400 hover:text-slate-200 hover:bg-slate-800 disabled:opacity-30 disabled:cursor-not-allowed transition-colors text-xs font-medium"
                                                >
                                                    <Paperclip className="w-4 h-4" />
                                                    <span>Attach</span>
                                                </button>
                                                {attachments.length > 0 && (
                                                    <span className="text-[10px] text-blue-400 font-semibold px-2 py-0.5 bg-blue-500/10 rounded-full border border-blue-500/20">
                                                        {attachments.length} file{attachments.length > 1 ? 's' : ''}
                                                    </span>
                                                )}
                                            </div>

                                            {/* Right: hint + send button */}
                                            <div className="flex items-center gap-2">
                                                <span className="text-[10px] text-slate-600 hidden sm:block">⏎ send · ⇧⏎ newline</span>
                                                <button
                                                    title="Send Message"
                                                    type="button"
                                                    onClick={sendChatMessage}
                                                    disabled={(!chatInput.trim() && attachments.length === 0) || config.status !== 'connected' || isTyping}
                                                    className="bg-blue-600 hover:bg-blue-500 disabled:bg-slate-700 disabled:text-slate-500 disabled:cursor-not-allowed text-white px-3 py-1.5 rounded-full text-xs font-semibold transition-all flex items-center gap-1.5"
                                                >
                                                    <Send className="w-3.5 h-3.5" />
                                                    Send
                                                </button>
                                                {isTyping && (
                                                    <button
                                                        onClick={() => {
                                                            if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
                                                                wsRef.current.send(JSON.stringify({ type: 'cancel' }));
                                                                setIsTyping(false);
                                                            }
                                                        }}
                                                        className="bg-red-600/80 hover:bg-red-500 text-white px-3 py-1.5 rounded-full text-xs font-semibold transition-all flex items-center gap-1.5 border border-red-500/50 animate-pulse hover:animate-none"
                                                        title="Cancel current agent task"
                                                    >
                                                        ✕ Cancel
                                                    </button>
                                                )}
                                            </div>
                                        </div>

                                    </div>
                                </div>
                            </div>
                        </section >
                    </div>
                )
                }

                {
                    activeTab === 'channels' && (
                        <div className="flex-1 p-10 overflow-y-auto fade-in">
                            <div className="w-full">
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
                                            <>
                                                <WhatsAppSecurity isRunning={mockChannels.find(c => c.id === 'wa')?.status === 'running'} />
                                                <VoiceSettings />
                                                <EmailSettings />
                                            </>
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
                    activeTab === 'skills' && <SkillsView skills={skills} catalog={catalog} onRefresh={() => {
                        return apiFetch('/api/skills')
                            .then(r => r.json())
                            .then(data => {
                                setCatalog(data);
                                setSkills((data.curated || []).map((s: any) => s.name));
                            })
                            .catch(e => console.error("Could not refresh skills API", e));
                    }} isGenerating={isGenerating} setIsGenerating={setIsGenerating} />
                }
                {activeTab === 'usage' && <UsageView />}
                {activeTab === 'logs' && <LogsView logs={logs} />}
                {activeTab === 'cron' && <CronView agents={agents} logs={logs} />}
                {activeTab === 'workflows' && <WorkflowsView />}
                {activeTab === 'events' && <EventTriggersView />}
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
