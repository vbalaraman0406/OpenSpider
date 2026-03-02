import { useState, useEffect, useMemo } from 'react';
import { RefreshCw, AlertTriangle, TrendingUp, TrendingDown, Coins, Search, Cpu, Zap, Hash, ArrowUpRight, ArrowDownRight } from 'lucide-react';
import {
    AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell, Label,
    XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend
} from 'recharts';

export interface UsageSummary {
    totalTokens: number;
    totalCostEst: number;
    totalRequests: number;
    avgTokensPerRequest: number;
    previousPeriodCost: number;
    models: Record<string, number>;
    agents: Record<string, number>;
    dailyTokens: { date: string, totalTokens: number, promptTokens: number, completionTokens: number }[];
    recentSessions: any[];
}

// Colors for the donut chart and agent bars
const CHART_COLORS = ['#3b82f6', '#d946ef', '#f59e0b', '#10b981', '#a855f7', '#06b6d4', '#f43f5e', '#84cc16'];

const AGENT_COLORS: Record<string, string> = {
    gateway: '#3b82f6',
    manager: '#a855f7',
    researcher: '#10b981',
    coder: '#f59e0b',
    tester: '#06b6d4',
};

const safeFormatDateTime = (ts: any) => {
    if (!ts) return 'Unknown';
    try {
        const d = new Date(ts);
        if (isNaN(d.getTime())) return 'Invalid Date';
        return d.toLocaleString();
    } catch {
        return 'Invalid Date';
    }
};

const relativeTime = (ts: any): string => {
    if (!ts) return '';
    try {
        const now = Date.now();
        const then = new Date(ts).getTime();
        const diffMs = now - then;
        if (diffMs < 0) return 'just now';
        const sec = Math.floor(diffMs / 1000);
        if (sec < 60) return `${sec}s ago`;
        const min = Math.floor(sec / 60);
        if (min < 60) return `${min}m ago`;
        const hr = Math.floor(min / 60);
        if (hr < 24) return `${hr}h ago`;
        const day = Math.floor(hr / 24);
        return `${day}d ago`;
    } catch {
        return '';
    }
};

// Custom tooltip for the area chart
const AreaTooltip = ({ active, payload, label }: any) => {
    if (!active || !payload?.length) return null;
    return (
        <div className="bg-slate-900/95 border border-slate-700/60 rounded-xl px-4 py-3 shadow-2xl backdrop-blur-md">
            <div className="text-slate-400 text-xs font-semibold mb-2">{label}</div>
            {payload.map((p: any, i: number) => (
                <div key={i} className="flex items-center gap-2 text-sm">
                    <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: p.color }} />
                    <span className="text-slate-300">{p.name}:</span>
                    <span className="font-mono font-bold text-white">{(p.value || 0).toLocaleString()}</span>
                </div>
            ))}
        </div>
    );
};

// Custom label for the donut center
const DonutCenterLabel = ({ viewBox, total }: any) => {
    const { cx, cy } = viewBox;
    return (
        <g>
            <text x={cx} y={cy - 8} textAnchor="middle" className="fill-slate-400 text-[10px] font-bold uppercase tracking-widest">
                Total Cost
            </text>
            <text x={cx} y={cy + 18} textAnchor="middle" className="fill-white text-xl font-bold">
                ${total}
            </text>
        </g>
    );
};

export function UsageView() {
    const [summary, setSummary] = useState<UsageSummary | null>(null);
    const [loading, setLoading] = useState(true);
    const [daysScope, setDaysScope] = useState<number>(30);
    const [sessionSearch, setSessionSearch] = useState('');

    const fetchUsage = async () => {
        setLoading(true);
        try {
            const res = await fetch(`/api/usage?days=${daysScope}`);
            const data = await res.json();
            // Safe fallbacks for new fields (backward compat if backend not yet rebuilt)
            data.totalRequests = data.totalRequests ?? data.recentSessions?.length ?? 0;
            data.avgTokensPerRequest = data.avgTokensPerRequest ?? (data.totalRequests > 0 ? Math.round((data.totalTokens || 0) / data.totalRequests) : 0);
            data.previousPeriodCost = data.previousPeriodCost ?? 0;
            setSummary(data);
        } catch (e) {
            console.error('Failed to fetch usage:', e);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchUsage();
    }, [daysScope]);

    // Filter recent sessions
    const filteredSessions = useMemo(() => {
        if (!summary || !summary.recentSessions) return [];
        if (!sessionSearch.trim()) return summary.recentSessions;
        const lowerSearch = sessionSearch.toLowerCase();
        return summary.recentSessions.filter((s: any) =>
            (s.agentId || '').toLowerCase().includes(lowerSearch) ||
            (s.model || '').toLowerCase().includes(lowerSearch)
        );
    }, [sessionSearch, summary]);

    if (loading && !summary) {
        return (
            <div className="flex-1 p-10 flex items-center justify-center">
                <RefreshCw className="w-8 h-8 text-indigo-500 animate-spin" />
            </div>
        );
    }

    if (!summary) {
        return (
            <div className="flex-1 p-10 flex items-center justify-center text-red-400">
                <AlertTriangle className="w-6 h-6 mr-2" />
                Error loading usage data.
            </div>
        );
    }

    // Chart data
    const chartData = summary.dailyTokens.map((d: any) => ({
        name: d.date.slice(5), // "MM-DD" for compact labels
        Input: d.promptTokens,
        Output: d.completionTokens,
    }));

    // Donut data — cost by model
    const modelCostData = Object.entries(summary.models).map(([model, tokens]) => {
        // Rough proportional cost allocation
        const proportion = summary.totalTokens > 0 ? tokens / summary.totalTokens : 0;
        return {
            name: model.length > 20 ? model.slice(0, 18) + '…' : model,
            fullName: model,
            value: Number((proportion * summary.totalCostEst).toFixed(4)),
            tokens,
        };
    }).filter(d => d.value > 0 || d.tokens > 0);

    // If all costs are 0 (local models), show by token proportion instead
    const allCostZero = modelCostData.every(d => d.value === 0);
    if (allCostZero) {
        modelCostData.forEach(d => { d.value = d.tokens; });
    }

    // Agent bar chart data
    const agentData = Object.entries(summary.agents || {})
        .sort(([, a]: any, [, b]: any) => b - a)
        .map(([agent, tokens]) => ({
            agent,
            tokens,
            fill: AGENT_COLORS[agent] || CHART_COLORS[Object.keys(summary.agents).indexOf(agent) % CHART_COLORS.length],
        }));

    // Cost delta
    const costDelta = summary.previousPeriodCost > 0
        ? ((summary.totalCostEst - summary.previousPeriodCost) / summary.previousPeriodCost * 100)
        : 0;
    const costDeltaUp = costDelta >= 0;

    // Date range options
    const ranges = [
        { label: 'Today', value: 1 },
        { label: '7d', value: 7 },
        { label: '30d', value: 30 },
        { label: 'All', value: 0 },
    ];

    return (
        <div className="flex-1 p-10 overflow-y-auto fade-in">
            <div className="max-w-7xl mx-auto">
                {/* Header */}
                <header className="mb-10 flex justify-between items-end">
                    <div>
                        <h2 className="text-3xl font-bold text-white tracking-tight">Usage Monitoring</h2>
                        <p className="text-slate-400 mt-2 text-sm max-w-2xl leading-relaxed">
                            Track token consumption, API costs, and agent activity across your system.
                        </p>
                    </div>
                    <div className="flex items-center gap-4">
                        <div className="flex items-center bg-slate-900/50 rounded-lg p-1 border border-slate-800">
                            {ranges.map(r => (
                                <button
                                    key={r.value}
                                    onClick={() => setDaysScope(r.value)}
                                    className={`px-3 py-1.5 rounded-md text-xs font-semibold transition-all ${daysScope === r.value ? 'bg-indigo-500/20 text-indigo-400 border border-indigo-500/30 shadow-sm' : 'text-slate-500 hover:text-slate-300'}`}
                                >
                                    {r.label}
                                </button>
                            ))}
                        </div>
                        <button onClick={fetchUsage} className="p-2.5 rounded-lg bg-slate-800/50 hover:bg-slate-700 text-slate-400 hover:text-white transition-colors border border-transparent hover:border-slate-600 shadow-md">
                            <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
                        </button>
                    </div>
                </header>

                {/* ──────────── Stat Cards ──────────── */}
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
                    {/* Total Tokens */}
                    <div className="bg-slate-900/40 backdrop-blur-xl rounded-2xl border border-white/5 p-6 shadow-xl relative overflow-hidden group hover:bg-slate-900/60 transition-all">
                        <div className="absolute top-0 inset-x-0 h-px w-full bg-gradient-to-r from-transparent via-cyan-500/40 to-transparent" />
                        <div className="flex items-center gap-3 mb-3 opacity-80">
                            <TrendingUp className="w-4 h-4 text-cyan-400" />
                            <span className="text-[10px] uppercase tracking-widest text-slate-500 font-bold">Total Tokens</span>
                        </div>
                        <div className="text-4xl font-bold tracking-tight text-white">{summary.totalTokens.toLocaleString()}</div>
                        <div className="text-xs text-slate-500 mt-2">
                            {daysScope === 0 ? 'All time' : daysScope === 1 ? 'Today' : `Last ${daysScope} days`}
                        </div>
                    </div>

                    {/* Estimated Cost */}
                    <div className="bg-slate-900/40 backdrop-blur-xl rounded-2xl border border-white/5 p-6 shadow-xl relative overflow-hidden group hover:bg-slate-900/60 transition-all">
                        <div className="absolute top-0 inset-x-0 h-px w-full bg-gradient-to-r from-transparent via-emerald-500/40 to-transparent" />
                        <div className="flex items-center gap-3 mb-3 opacity-80">
                            <Coins className="w-4 h-4 text-emerald-400" />
                            <span className="text-[10px] uppercase tracking-widest text-slate-500 font-bold">Est. Cost</span>
                        </div>
                        <div className="flex items-end gap-3">
                            <div className="text-4xl font-bold tracking-tight text-emerald-400">${summary.totalCostEst.toFixed(3)}</div>
                            {costDelta !== 0 && (
                                <div className={`flex items-center gap-1 text-xs font-bold px-2 py-0.5 rounded-full mb-1.5 ${costDeltaUp ? 'bg-red-500/10 text-red-400' : 'bg-emerald-500/10 text-emerald-400'}`}>
                                    {costDeltaUp ? <ArrowUpRight className="w-3 h-3" /> : <ArrowDownRight className="w-3 h-3" />}
                                    {Math.abs(costDelta).toFixed(1)}%
                                </div>
                            )}
                        </div>
                        <div className="text-xs text-slate-500 mt-2">vs prior period</div>
                    </div>

                    {/* Avg Tokens/Request */}
                    <div className="bg-slate-900/40 backdrop-blur-xl rounded-2xl border border-white/5 p-6 shadow-xl relative overflow-hidden group hover:bg-slate-900/60 transition-all">
                        <div className="absolute top-0 inset-x-0 h-px w-full bg-gradient-to-r from-transparent via-purple-500/40 to-transparent" />
                        <div className="flex items-center gap-3 mb-3 opacity-80">
                            <Zap className="w-4 h-4 text-purple-400" />
                            <span className="text-[10px] uppercase tracking-widest text-slate-500 font-bold">Avg / Request</span>
                        </div>
                        <div className="text-4xl font-bold tracking-tight text-purple-300">{summary.avgTokensPerRequest.toLocaleString()}</div>
                        <div className="text-xs text-slate-500 mt-2">tokens per API call</div>
                    </div>

                    {/* Total Requests */}
                    <div className="bg-slate-900/40 backdrop-blur-xl rounded-2xl border border-white/5 p-6 shadow-xl relative overflow-hidden group hover:bg-slate-900/60 transition-all">
                        <div className="absolute top-0 inset-x-0 h-px w-full bg-gradient-to-r from-transparent via-amber-500/40 to-transparent" />
                        <div className="flex items-center gap-3 mb-3 opacity-80">
                            <Hash className="w-4 h-4 text-amber-400" />
                            <span className="text-[10px] uppercase tracking-widest text-slate-500 font-bold">Total Requests</span>
                        </div>
                        <div className="text-4xl font-bold tracking-tight text-amber-300">{summary.totalRequests.toLocaleString()}</div>
                        <div className="text-xs text-slate-500 mt-2">API call count</div>
                    </div>
                </div>

                {/* ──────────── Charts Row ──────────── */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
                    {/* Area Chart — Token Usage Over Time */}
                    <div className="lg:col-span-2 bg-slate-900/40 backdrop-blur-xl rounded-2xl border border-white/5 p-6 shadow-xl relative overflow-hidden">
                        <div className="absolute top-0 inset-x-0 h-px w-full bg-gradient-to-r from-transparent via-blue-500/30 to-transparent" />
                        <h3 className="text-lg font-semibold text-white mb-6 tracking-tight">Token Usage Over Time</h3>
                        <div className="h-72 -ml-2">
                            {chartData.length > 0 ? (
                                <ResponsiveContainer width="100%" height="100%">
                                    <AreaChart data={chartData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                                        <defs>
                                            <linearGradient id="gradInput" x1="0" y1="0" x2="0" y2="1">
                                                <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.35} />
                                                <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.0} />
                                            </linearGradient>
                                            <linearGradient id="gradOutput" x1="0" y1="0" x2="0" y2="1">
                                                <stop offset="5%" stopColor="#d946ef" stopOpacity={0.35} />
                                                <stop offset="95%" stopColor="#d946ef" stopOpacity={0.0} />
                                            </linearGradient>
                                        </defs>
                                        <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                                        <XAxis dataKey="name" stroke="#475569" fontSize={11} tickMargin={10} axisLine={false} tickLine={false} />
                                        <YAxis stroke="#475569" fontSize={11} tickMargin={10} axisLine={false} tickLine={false} tickFormatter={(val) => val >= 1000 ? `${(val / 1000).toFixed(0)}k` : val} />
                                        <Tooltip content={<AreaTooltip />} />
                                        <Area type="monotone" dataKey="Input" stackId="1" stroke="#3b82f6" strokeWidth={2} fill="url(#gradInput)" />
                                        <Area type="monotone" dataKey="Output" stackId="1" stroke="#d946ef" strokeWidth={2} fill="url(#gradOutput)" />
                                    </AreaChart>
                                </ResponsiveContainer>
                            ) : (
                                <div className="w-full h-full flex items-center justify-center text-slate-500 text-sm font-medium">
                                    No timeline data yet. Run some tasks!
                                </div>
                            )}
                        </div>
                        {/* Legend */}
                        <div className="flex items-center gap-6 mt-4 ml-2">
                            <div className="flex items-center gap-2 text-xs text-slate-400">
                                <span className="w-3 h-1.5 rounded-full bg-blue-500" /> Input (Prompt)
                            </div>
                            <div className="flex items-center gap-2 text-xs text-slate-400">
                                <span className="w-3 h-1.5 rounded-full bg-fuchsia-500" /> Output (Completion)
                            </div>
                        </div>
                    </div>

                    {/* Donut Chart — Cost by Model */}
                    <div className="bg-slate-900/40 backdrop-blur-xl rounded-2xl border border-white/5 p-6 shadow-xl relative overflow-hidden flex flex-col">
                        <div className="absolute top-0 inset-x-0 h-px w-full bg-gradient-to-r from-transparent via-fuchsia-500/30 to-transparent" />
                        <h3 className="text-lg font-semibold text-white mb-4 tracking-tight">
                            {allCostZero ? 'Tokens by Model' : 'Cost by Model'}
                        </h3>
                        {modelCostData.length > 0 ? (
                            <>
                                <div className="flex-1 flex items-center justify-center min-h-[180px]">
                                    <ResponsiveContainer width="100%" height={200}>
                                        <PieChart>
                                            <Pie
                                                data={modelCostData}
                                                cx="50%"
                                                cy="50%"
                                                innerRadius={55}
                                                outerRadius={82}
                                                paddingAngle={3}
                                                dataKey="value"
                                                stroke="none"
                                            >
                                                {modelCostData.map((_, i) => (
                                                    <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />
                                                ))}
                                                <Label
                                                    content={<DonutCenterLabel total={summary.totalCostEst.toFixed(2)} />}
                                                    position="center"
                                                />
                                            </Pie>
                                            <Tooltip
                                                contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '0.5rem', fontSize: '12px', color: '#f8fafc' }}
                                                formatter={(value: any, name: any) => [
                                                    allCostZero ? `${Number(value).toLocaleString()} tokens` : `$${Number(value).toFixed(4)}`,
                                                    name
                                                ]}
                                            />
                                        </PieChart>
                                    </ResponsiveContainer>
                                </div>
                                {/* Legend */}
                                <div className="space-y-2 mt-2">
                                    {modelCostData.map((entry, i) => (
                                        <div key={entry.name} className="flex items-center justify-between text-xs">
                                            <div className="flex items-center gap-2 truncate pr-2">
                                                <span className="w-2.5 h-2.5 rounded-full shrink-0" style={{ backgroundColor: CHART_COLORS[i % CHART_COLORS.length] }} />
                                                <span className="text-slate-300 truncate">{entry.name}</span>
                                            </div>
                                            <span className="font-mono text-slate-400 shrink-0">
                                                {allCostZero ? `${Math.round((entry.tokens / summary.totalTokens) * 100)}%` : `$${entry.value.toFixed(3)}`}
                                            </span>
                                        </div>
                                    ))}
                                </div>
                            </>
                        ) : (
                            <div className="flex-1 flex items-center justify-center text-slate-500 text-sm font-medium">
                                No model data yet
                            </div>
                        )}
                    </div>
                </div>

                {/* ──────────── Bottom Row ──────────── */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* Agent Activity */}
                    <div className="bg-slate-900/40 backdrop-blur-xl rounded-2xl border border-white/5 p-6 shadow-xl relative overflow-hidden">
                        <div className="absolute top-0 inset-x-0 h-px w-full bg-gradient-to-r from-transparent via-indigo-500/30 to-transparent" />
                        <h3 className="text-lg font-semibold text-white mb-6 tracking-tight">Agent Activity</h3>
                        {agentData.length > 0 ? (
                            <div className="h-56">
                                <ResponsiveContainer width="100%" height="100%">
                                    <BarChart data={agentData} layout="vertical" margin={{ left: 0, right: 20, top: 5, bottom: 5 }}>
                                        <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" horizontal={false} />
                                        <XAxis type="number" stroke="#475569" fontSize={11} axisLine={false} tickLine={false} tickFormatter={(val) => val >= 1000 ? `${(val / 1000).toFixed(0)}k` : val} />
                                        <YAxis type="category" dataKey="agent" stroke="#475569" fontSize={12} width={90} axisLine={false} tickLine={false} />
                                        <Tooltip
                                            contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '0.5rem', fontSize: '12px', color: '#f8fafc' }}
                                            formatter={(value: any) => [`${Number(value).toLocaleString()} tokens`, 'Usage']}
                                        />
                                        <Bar dataKey="tokens" radius={[0, 6, 6, 0]} barSize={20}>
                                            {agentData.map((entry, i) => (
                                                <Cell key={i} fill={entry.fill} />
                                            ))}
                                        </Bar>
                                    </BarChart>
                                </ResponsiveContainer>
                            </div>
                        ) : (
                            <div className="h-56 flex items-center justify-center text-slate-500 text-sm font-medium">
                                No agent activity recorded
                            </div>
                        )}
                    </div>

                    {/* Recent Activity Feed */}
                    <div className="bg-slate-900/40 backdrop-blur-xl rounded-2xl border border-white/5 shadow-xl overflow-hidden flex flex-col">
                        <div className="absolute top-0 inset-x-0 h-px w-full bg-gradient-to-r from-transparent via-rose-500/30 to-transparent" />
                        <div className="p-5 border-b border-slate-800/60 bg-slate-900/80 flex items-center justify-between shrink-0">
                            <div>
                                <h3 className="text-lg font-semibold text-white tracking-tight">Recent Activity</h3>
                                <span className="text-xs text-slate-400 font-medium">
                                    {daysScope === 0 ? 'All Time' : daysScope === 1 ? 'Today' : `Last ${daysScope} days`}
                                </span>
                            </div>
                            <div className="relative">
                                <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
                                <input
                                    type="text"
                                    placeholder="Filter by agent or model..."
                                    value={sessionSearch}
                                    onChange={(e) => setSessionSearch(e.target.value)}
                                    className="w-56 bg-slate-950/80 border border-slate-800 rounded-lg pl-9 pr-4 py-2 text-sm text-slate-300 focus:outline-none focus:ring-1 focus:ring-indigo-500/50"
                                />
                            </div>
                        </div>

                        <div className="flex-1 overflow-y-auto max-h-[320px] divide-y divide-slate-800/40">
                            {filteredSessions.length > 0 ? filteredSessions.slice(0, 50).map((session: any, i: number) => {
                                const isSpike = session.usage?.totalTokens > 5000;
                                const agentId = session.agentId || 'gateway';
                                const agentColor = AGENT_COLORS[agentId] || '#64748b';
                                return (
                                    <div key={session.timestamp + i} className={`px-5 py-3.5 flex items-center gap-4 transition-colors hover:bg-slate-800/20 ${isSpike ? 'bg-red-500/5' : ''}`}>
                                        {/* Agent badge */}
                                        <div
                                            className="w-8 h-8 rounded-lg flex items-center justify-center text-xs font-bold uppercase shrink-0"
                                            style={{ backgroundColor: agentColor + '20', color: agentColor, border: `1px solid ${agentColor}30` }}
                                        >
                                            {agentId.charAt(0).toUpperCase()}
                                        </div>
                                        {/* Details */}
                                        <div className="flex-1 min-w-0">
                                            <div className="flex items-center gap-2">
                                                <span className="text-sm font-semibold text-slate-200">{agentId}</span>
                                                <span className="bg-slate-800 text-slate-400 px-2 py-0.5 rounded text-[10px] font-mono truncate max-w-[140px]">{session.model}</span>
                                            </div>
                                            <div className="text-[11px] text-slate-500 mt-0.5">
                                                {session.usage?.promptTokens || 0} in · {session.usage?.completionTokens || 0} out
                                            </div>
                                        </div>
                                        {/* Token count + time */}
                                        <div className="text-right shrink-0">
                                            <div className={`text-sm font-mono font-bold flex items-center justify-end gap-1.5 ${isSpike ? 'text-red-400' : 'text-emerald-400'}`}>
                                                {session.usage?.totalTokens?.toLocaleString() || 0}
                                                {isSpike && <AlertTriangle className="w-3 h-3 text-red-500 animate-pulse" />}
                                            </div>
                                            <div className="text-[10px] text-slate-500 mt-0.5">{relativeTime(session.timestamp)}</div>
                                        </div>
                                    </div>
                                );
                            }) : (
                                <div className="px-5 py-12 text-center text-slate-500 font-medium text-sm">
                                    No sessions recorded.
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
