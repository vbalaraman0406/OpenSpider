import { useState, useEffect, useMemo } from 'react';
import { Activity, RefreshCw, AlertTriangle, Cpu, TrendingUp, Coins, Search, Sparkles, Filter } from 'lucide-react';
import { BarChart, Bar, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export interface UsageSummary {
    totalTokens: number;
    totalCostEst: number;
    models: Record<string, number>;
    agents: Record<string, number>;
    dailyTokens: { date: string, totalTokens: number, promptTokens: number, completionTokens: number }[];
    recentSessions: any[];
}

const safeFormatDateTime = (ts: any) => {
    if (!ts) return 'Unknown Date';
    try {
        const d = new Date(ts);
        if (isNaN(d.getTime())) return 'Invalid Date';
        return d.toLocaleString();
    } catch {
        return 'Invalid Date';
    }
};

export function UsageView() {
    const [summary, setSummary] = useState<UsageSummary | null>(null);
    const [loading, setLoading] = useState(true);

    // V2 state
    const [daysScope, setDaysScope] = useState<number>(30);
    const [sessionSearch, setSessionSearch] = useState('');

    const fetchUsage = async () => {
        setLoading(true);
        try {
            const res = await fetch(`/api/usage?days=${daysScope}`);
            const data = await res.json();
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
    // Filter recent sessions dynamically (hook rules dictate this must be before conditionals)
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

    // Prepare chart data format
    const chartData = summary.dailyTokens.map((d: any) => ({
        name: d.date,
        Tokens: d.totalTokens,
        Input: d.promptTokens,
        Output: d.completionTokens
    }));

    // Calculate dynamic insights
    const sortedModels = Object.entries(summary.models).sort(([, a]: any, [, b]: any) => b - a);
    const topModelEntry = sortedModels.length > 0 ? sortedModels[0] : null;

    const sortedAgents = Object.entries(summary.agents || {}).sort(([, a]: any, [, b]: any) => b - a);
    const topAgentEntry = sortedAgents.length > 0 ? sortedAgents[0] : null;

    // Date Options
    const ranges = [
        { label: 'Today', value: 1 },
        { label: '7d', value: 7 },
        { label: '30d', value: 30 },
        { label: 'All', value: 0 }
    ];

    return (
        <div className="flex-1 p-10 overflow-y-auto fade-in">
            <div className="max-w-6xl mx-auto">
                <header className="mb-10 flex justify-between items-end">
                    <div>
                        <h2 className="text-3xl font-bold text-white tracking-tight">Usage Monitoring</h2>
                        <p className="text-slate-400 mt-2 text-sm max-w-2xl leading-relaxed">
                            See where tokens go, identify usage spikes, and exact tracking of API expenses.
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

                <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
                    <div className="bg-slate-900/40 backdrop-blur-xl rounded-2xl border border-white/5 p-6 shadow-xl relative overflow-hidden group hover:bg-slate-900/60 transition-all">
                        <div className="absolute top-0 inset-x-0 h-px w-full bg-gradient-to-r from-transparent via-cyan-500/30 to-transparent"></div>
                        <div className="flex items-center gap-3 mb-2 opacity-80">
                            <TrendingUp className="w-4 h-4 text-cyan-400" />
                            <span className="text-[10px] uppercase tracking-widest text-slate-500 font-bold">Total Tokens</span>
                        </div>
                        <div className="text-4xl font-bold tracking-tight text-white">{summary.totalTokens.toLocaleString()}</div>
                    </div>

                    <div className="bg-slate-900/40 backdrop-blur-xl rounded-2xl border border-white/5 p-6 shadow-xl relative overflow-hidden group hover:bg-slate-900/60 transition-all">
                        <div className="absolute top-0 inset-x-0 h-px w-full bg-gradient-to-r from-transparent via-emerald-500/30 to-transparent"></div>
                        <div className="flex items-center gap-3 mb-2 opacity-80">
                            <Coins className="w-4 h-4 text-emerald-400" />
                            <span className="text-[10px] uppercase tracking-widest text-slate-500 font-bold">Est. Expense</span>
                        </div>
                        <div className="text-4xl font-bold tracking-tight text-emerald-400">${summary.totalCostEst.toFixed(3)}</div>
                        <div className="text-xs text-slate-500 mt-2">Rough estimate across mixed models</div>
                    </div>

                    <div className="bg-slate-900/40 backdrop-blur-xl rounded-2xl border border-white/5 p-6 shadow-xl relative overflow-hidden group hover:bg-slate-900/60 transition-all">
                        <div className="absolute top-0 inset-x-0 h-px w-full bg-gradient-to-r from-transparent via-purple-500/30 to-transparent"></div>
                        <div className="flex items-center gap-3 mb-2 opacity-80">
                            <Cpu className="w-4 h-4 text-purple-400" />
                            <span className="text-[10px] uppercase tracking-widest text-slate-500 font-bold">Top Provider</span>
                        </div>
                        <div className="text-3xl font-bold tracking-tight text-purple-300 truncate">
                            {topModelEntry ? topModelEntry[0] : 'N/A'}
                        </div>
                        {topModelEntry && <div className="text-xs text-slate-500 mt-2">{topModelEntry[1].toLocaleString()} total tokens</div>}
                    </div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-10">
                    <div className="lg:col-span-2 bg-slate-900/40 backdrop-blur-xl rounded-2xl border border-white/5 p-6 shadow-xl relative overflow-hidden">
                        <div className="absolute top-0 inset-x-0 h-px w-full bg-gradient-to-r from-transparent via-blue-500/30 to-transparent"></div>
                        <h3 className="text-lg font-semibold text-white mb-6 tracking-tight">Daily Input / Output Volume</h3>

                        <div className="h-64 mt-4 -ml-4">
                            {chartData.length > 0 ? (
                                <ResponsiveContainer width="100%" height="100%">
                                    <BarChart data={chartData} margin={{ top: 10, right: 10, left: 10, bottom: 0 }}>
                                        <XAxis dataKey="name" stroke="#475569" fontSize={11} tickMargin={10} axisLine={false} tickLine={false} />
                                        <YAxis stroke="#475569" fontSize={11} tickMargin={10} axisLine={false} tickLine={false} tickFormatter={(val) => `${val / 1000}k`} />
                                        <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                                        <Tooltip
                                            cursor={{ fill: '#1e293b', opacity: 0.4 }}
                                            contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '0.5rem', fontSize: '13px', color: '#f8fafc' }}
                                        />
                                        <Bar dataKey="Input" stackId="a" fill="#3b82f6" radius={[0, 0, 0, 0]} />
                                        <Bar dataKey="Output" stackId="a" fill="#d946ef" radius={[4, 4, 0, 0]} />
                                    </BarChart>
                                </ResponsiveContainer>
                            ) : (
                                <div className="w-full h-full flex items-center justify-center text-slate-500 text-sm font-medium">
                                    No timeline data yet. Run some tasks!
                                </div>
                            )}
                        </div>
                    </div>

                    <div className="bg-slate-900/40 backdrop-blur-xl rounded-2xl border border-white/5 p-6 shadow-xl relative overflow-hidden flex flex-col">
                        <div className="absolute top-0 inset-x-0 h-px w-full bg-gradient-to-r from-transparent via-fuchsia-500/30 to-transparent"></div>
                        <h3 className="text-lg font-semibold text-white mb-6 tracking-tight">Model Breakdown</h3>

                        <div className="flex-1 overflow-y-auto space-y-4 pr-2">
                            {Object.entries(summary.models).map(([model, tok]) => (
                                <div key={model} className="bg-slate-950/50 rounded-xl border border-slate-800/60 p-4">
                                    <div className="flex justify-between items-center mb-2">
                                        <div className="text-sm font-semibold text-slate-200 truncate pr-4">{model}</div>
                                        <div className="text-xs font-mono text-fuchsia-400 bg-fuchsia-500/10 px-2 py-0.5 rounded flex-shrink-0">
                                            {Math.round((tok / summary.totalTokens) * 100)}%
                                        </div>
                                    </div>
                                    <div className="w-full bg-slate-800 rounded-full h-1.5 mt-2 overflow-hidden">
                                        <div className="bg-fuchsia-500 h-1.5 rounded-full" style={{ width: `${Math.max(2, (tok / summary.totalTokens) * 100)}%` }}></div>
                                    </div>
                                    <div className="text-[10px] text-slate-500 mt-2 tabular-nums">
                                        {tok.toLocaleString()} tokens
                                    </div>
                                </div>
                            ))}
                            {Object.keys(summary.models).length === 0 && (
                                <div className="text-slate-500 text-sm text-center py-10">No models utilized yet</div>
                            )}
                        </div>
                    </div>
                </div>

                <div className="bg-slate-900/40 backdrop-blur-xl rounded-2xl border border-white/5 pb-2 shadow-xl overflow-hidden">
                    <div className="p-5 border-b border-slate-800/60 bg-slate-900/80 flex items-center justify-between">
                        <div>
                            <h3 className="text-lg font-semibold text-white tracking-tight">Recent Sessions Data</h3>
                            <span className="text-xs text-slate-400 font-medium">Tracking the most latest events from {daysScope === 0 ? 'All Time' : `${daysScope} Days`}</span>
                        </div>

                        <div className="relative">
                            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
                            <input
                                type="text"
                                placeholder="Search by agent or model..."
                                value={sessionSearch}
                                onChange={(e) => setSessionSearch(e.target.value)}
                                className="w-64 bg-slate-950/80 border border-slate-800 rounded-lg pl-9 pr-4 py-2 text-sm text-slate-300 focus:outline-none focus:ring-1 focus:ring-indigo-500/50"
                            />
                        </div>
                    </div>

                    <div className="overflow-x-auto">
                        <table className="w-full text-left text-sm whitespace-nowrap">
                            <thead className="bg-slate-950/30 text-slate-500 text-[10px] uppercase tracking-widest font-semibold border-b border-slate-800/60">
                                <tr>
                                    <th className="px-6 py-4">Timestamp</th>
                                    <th className="px-6 py-4">Agent Key</th>
                                    <th className="px-6 py-4">Model Used</th>
                                    <th className="px-6 py-4 text-right">Prompt</th>
                                    <th className="px-6 py-4 text-right">Completion</th>
                                    <th className="px-6 py-4 text-right">Total Tokens</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-slate-800/60 text-slate-300">
                                {filteredSessions.length > 0 ? filteredSessions.map((session, i) => {
                                    const isSpike = session.usage?.totalTokens > 5000;
                                    return (
                                        <tr key={session.timestamp + i} className={`transition-colors ${isSpike ? 'bg-red-500/5 hover:bg-red-500/10' : 'hover:bg-slate-800/30'}`}>
                                            <td className="px-6 py-4 text-xs text-slate-400">{safeFormatDateTime(session.timestamp)}</td>
                                            <td className="px-6 py-4 font-mono text-xs font-semibold text-indigo-300">
                                                {session.agentId || 'gateway'}
                                            </td>
                                            <td className="px-6 py-4"><span className="bg-slate-800 text-slate-300 px-2 py-1 rounded text-xs">{session.model}</span></td>
                                            <td className="px-6 py-4 text-right font-mono text-slate-400">{session.usage?.promptTokens || 0}</td>
                                            <td className="px-6 py-4 text-right font-mono text-slate-400">{session.usage?.completionTokens || 0}</td>
                                            <td className={`px-6 py-4 text-right font-mono font-bold ${isSpike ? 'text-red-400' : 'text-emerald-400'}`}>
                                                {session.usage?.totalTokens.toLocaleString() || 0}
                                                {isSpike && <AlertTriangle className="w-3 h-3 inline-block ml-2 mb-0.5 text-red-500 animate-pulse" />}
                                            </td>
                                        </tr>
                                    );
                                }) : (
                                    <tr>
                                        <td colSpan={6} className="px-6 py-8 text-center text-slate-500 font-medium">No sessions recorded.</td>
                                    </tr>
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>

            </div>
        </div>
    );
}
