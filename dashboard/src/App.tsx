import { useState, useEffect, useRef } from 'react';
import { Activity, Terminal, CheckCircle2, Server, Key, Bot, Send, MessageSquare, Radio, Smartphone, MessagesSquare, Users, Globe, Play, Square, Settings, RefreshCw } from 'lucide-react';

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
    { id: 'wa', name: 'WhatsApp', icon: Smartphone, status: 'running', lastProbe: '2m ago', authAge: '14d 2h', description: 'Primary agent interface for direct user SMS.' },
    { id: 'tg', name: 'Telegram', icon: MessagesSquare, status: 'offline', lastProbe: '1h ago', description: 'Telegram bot API polling. Currently disabled.' },
    { id: 'dc', name: 'Discord', icon: Users, status: 'configured', description: 'Discord webhook interop. Pending token.' },
    { id: 'gc', name: 'Google Chat', icon: MessageSquare, status: 'configured', description: 'Google Workspace Chat integration.' },
    { id: 'sl', name: 'Slack', icon: Activity, status: 'offline', description: 'Slack Enterprise Grid connector.' },
    { id: 'si', name: 'Signal', icon: Globe, status: 'configured', description: 'Encrypted Signal proxy bridge.' }
];

interface LogMessage {
    type: string;
    data: string;
    timestamp: string;
}

export default function App() {
    const [activeTab, setActiveTab] = useState<'chat' | 'channels'>('chat');
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

                <nav className="flex-1 px-4 py-8 space-y-2">
                    <div className="text-xs font-semibold text-slate-500 uppercase tracking-widest mb-4 px-2">Views</div>
                    <button
                        onClick={() => setActiveTab('chat')}
                        className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200 ${activeTab === 'chat' ? 'bg-blue-600/10 text-blue-400 ring-1 ring-blue-500/30 shadow-[0_4px_20px_-4px_rgba(37,99,235,0.2)]' : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'}`}
                    >
                        <MessageSquare className="w-5 h-5" />
                        Agent Chat
                    </button>
                    <button
                        onClick={() => setActiveTab('channels')}
                        className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200 ${activeTab === 'channels' ? 'bg-emerald-600/10 text-emerald-400 ring-1 ring-emerald-500/30 shadow-[0_4px_20px_-4px_rgba(16,185,129,0.2)]' : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'}`}
                    >
                        <Radio className="w-5 h-5" />
                        Channels Manager
                    </button>
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
                {activeTab === 'chat' ? (
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
                ) : (
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
            </main >
        </div >
    );
}
