import { useState, useEffect } from 'react';
import { Activity, RefreshCw, AlertTriangle, Cpu, TrendingUp, Coins } from 'lucide-react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export interface UsageSummary {
    totalTokens: number;
    totalCostEst: number;
    models: Record<string, number>;
    dailyTokens: { date: string, tokens: number }[];
    recentSessions: any[];
}

export function UsageView() {
    const [summary, setSummary] = useState<UsageSummary | null>(null);
    const [loading, setLoading] = useState(true);

    const fetchUsage = async () => {
        setLoading(true);
        try {
            const res = await fetch('/api/usage');
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
    }, []);

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
    const chartData = summary.dailyTokens.map(d => ({
        name: d.date,
        Tokens: d.tokens
    }));

    // Calculate dynamic insight
    const sortedModels = Object.entries(summary.models).sort(([, a], [, b]) => b - a);
    const topModelEntry = sortedModels.length > 0 ? sortedModels[0] : null;

    return (
        <div className="flex-1 p-10 overflow-y-auto fade-in">
            <div className="max-w-6xl mx-auto">
                <header className="mb-10 flex justify-between items-end">
                    <div>
                        <h2 className="text-3xl font-bold text-white tracking-tight">Usage Monitoring</h2>
                        <p className="text-slate-400 mt-2 text-sm max-w-2xl leading-relaxed">
                            See where tokens go, identify usage spikes, and track relative cost estimations.
                        </p>
                    </div>
                    <button onClick={fetchUsage} className="p-2.5 rounded-lg bg-slate-800/50 hover:bg-slate-700 text-slate-400 hover:text-white transition-colors border border-transparent hover:border-slate-600 shadow-md">
                        <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
                    </button>
                </header>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
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
                        <h3 className="text-lg font-semibold text-white mb-6 tracking-tight">Daily Volume</h3>

                        <div className="h-64 mt-4 -ml-4">
                            {chartData.length > 0 ? (
                                <ResponsiveContainer width="100%" height="100%">
                                    <AreaChart data={chartData} margin={{ top: 10, right: 10, left: 10, bottom: 0 }}>
                                        <defs>
                                            <linearGradient id="colorTokens" x1="0" y1="0" x2="0" y2="1">
                                                <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.6} />
                                                <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                                            </linearGradient>
                                        </defs>
                                        <XAxis dataKey="name" stroke="#475569" fontSize={11} tickMargin={10} axisLine={false} tickLine={false} />
                                        <YAxis stroke="#475569" fontSize={11} tickMargin={10} axisLine={false} tickLine={false} tickFormatter={(val) => `${val / 1000}k`} />
                                        <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                                        <Tooltip
                                            contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '0.5rem', fontSize: '13px', color: '#f8fafc' }}
                                            itemStyle={{ color: '#60a5fa' }}
                                        />
                                        <Area type="monotone" dataKey="Tokens" stroke="#3b82f6" strokeWidth={3} fillOpacity={1} fill="url(#colorTokens)" />
                                    </AreaChart>
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
                        <h3 className="text-lg font-semibold text-white tracking-tight">Recent Sessions</h3>
                        <span className="text-xs text-slate-400 font-medium">Last 50 recorded invocations</span>
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
                                {summary.recentSessions.length > 0 ? summary.recentSessions.map((session, i) => {
                                    const isSpike = session.usage?.totalTokens > 5000;
                                    return (
                                        <tr key={session.timestamp + i} className={`transition-colors ${isSpike ? 'bg-red-500/5 hover:bg-red-500/10' : 'hover:bg-slate-800/30'}`}>
                                            <td className="px-6 py-4 text-xs text-slate-400">{new Date(session.timestamp).toLocaleString()}</td>
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
