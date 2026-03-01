import { useState, useEffect } from 'react';
import { Activity, RefreshCw, XCircle, AlertTriangle, Terminal, Cpu } from 'lucide-react';

interface ProcessInfo {
    uid: string;
    pid: string;
    ppid: string;
    stime: string;
    time: string;
    cmd: string;
}

export function ProcessMonitor() {
    const [processes, setProcesses] = useState<ProcessInfo[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [killing, setKilling] = useState<string | null>(null);

    const fetchProcesses = async () => {
        setLoading(true);
        setError('');
        try {
            const res = await fetch('/api/processes');
            if (!res.ok) throw new Error(await res.text());
            const data = await res.json();
            setProcesses(data);
        } catch (e: any) {
            setError(e.message || 'Failed to load processes');
        } finally {
            setLoading(false);
        }
    };

    const killProcess = async (pid: string) => {
        if (!confirm(`Are you sure you want to terminate process ${pid}? This cannot be undone.`)) return;

        setKilling(pid);
        try {
            const res = await fetch(`/api/processes/${pid}`, { method: 'DELETE' });
            if (!res.ok) throw new Error(await res.text());
            await fetchProcesses();
        } catch (e: any) {
            alert('Failed to kill process: ' + (e.message || 'Unknown error'));
        } finally {
            setKilling(null);
        }
    };

    useEffect(() => {
        fetchProcesses();
        const interval = setInterval(fetchProcesses, 10000); // Poll every 10s
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="flex-1 p-10 overflow-y-auto fade-in">
            <div className="max-w-6xl mx-auto">
                <header className="mb-10 flex justify-between items-end">
                    <div>
                        <h2 className="text-3xl font-bold text-white tracking-tight flex items-center gap-3">
                            <Activity className="w-8 h-8 text-indigo-400" />
                            Process Monitor
                        </h2>
                        <p className="text-slate-400 mt-2 text-sm max-w-2xl leading-relaxed">
                            View and manage background Node, Python, and Playwright processes spawned by OpenSpider agents.
                        </p>
                    </div>

                    <div className="flex items-center gap-4">
                        <button onClick={fetchProcesses} className="p-2.5 rounded-lg bg-slate-800/50 hover:bg-slate-700 text-slate-400 hover:text-white transition-colors border border-transparent hover:border-slate-600 shadow-md flex items-center gap-2">
                            <RefreshCw className={`w-4 h-4 ${loading && !killing ? 'animate-spin' : ''}`} />
                            <span className="text-xs font-semibold">Refresh</span>
                        </button>
                    </div>
                </header>

                {error && (
                    <div className="mb-6 p-4 rounded-xl border border-red-500/20 bg-red-500/10 flex items-start gap-3">
                        <AlertTriangle className="w-5 h-5 text-red-400 shrink-0 mt-0.5" />
                        <div>
                            <h4 className="text-sm font-semibold text-red-200">Error fetching processes</h4>
                            <p className="text-xs text-red-400/80 mt-1">{error}</p>
                        </div>
                    </div>
                )}

                <div className="bg-slate-900/40 backdrop-blur-xl rounded-2xl border border-white/5 pb-2 shadow-xl overflow-hidden">
                    <div className="p-5 border-b border-slate-800/60 bg-slate-900/80 flex items-center justify-between">
                        <div>
                            <h3 className="text-lg font-semibold text-white tracking-tight flex items-center gap-2">
                                <Terminal className="w-5 h-5 text-slate-400" />
                                Active System Processes
                            </h3>
                            <span className="text-xs text-slate-400 font-medium">{processes.length} matched processes running</span>
                        </div>
                    </div>

                    <div className="overflow-x-auto min-h-[400px]">
                        <table className="w-full text-left text-sm whitespace-nowrap">
                            <thead className="bg-slate-950/30 text-slate-500 text-[10px] uppercase tracking-widest font-semibold border-b border-slate-800/60 sticky top-0">
                                <tr>
                                    <th className="px-6 py-4">PID</th>
                                    <th className="px-6 py-4">User</th>
                                    <th className="px-6 py-4">CPU Time</th>
                                    <th className="px-6 py-4">Started</th>
                                    <th className="px-6 py-4 w-full">Command</th>
                                    <th className="px-6 py-4 text-right">Actions</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-slate-800/60 text-slate-300">
                                {processes.length > 0 ? processes.map((proc, i) => (
                                    <tr key={proc.pid + i} className="hover:bg-slate-800/30 transition-colors group">
                                        <td className="px-6 py-4 font-mono text-xs text-indigo-300">{proc.pid}</td>
                                        <td className="px-6 py-4 text-xs text-slate-400">{proc.uid}</td>
                                        <td className="px-6 py-4 text-xs text-slate-400 flex items-center gap-1.5"><Cpu className="w-3 h-3 text-slate-500" /> {proc.time}</td>
                                        <td className="px-6 py-4 text-xs text-slate-400">{proc.stime}</td>
                                        <td className="px-6 py-4 font-mono text-[11px] text-emerald-400/90 truncate max-w-lg" title={proc.cmd}>
                                            {proc.cmd}
                                        </td>
                                        <td className="px-6 py-4 text-right">
                                            <button
                                                onClick={() => killProcess(proc.pid)}
                                                disabled={killing === proc.pid}
                                                className="opacity-0 group-hover:opacity-100 transition-opacity p-1.5 rounded bg-red-500/10 text-red-400 hover:bg-red-500 hover:text-white disabled:opacity-50"
                                                title="Force Kill (SIGKILL)"
                                            >
                                                {killing === proc.pid ? <RefreshCw className="w-4 h-4 animate-spin" /> : <XCircle className="w-4 h-4" />}
                                            </button>
                                        </td>
                                    </tr>
                                )) : !loading ? (
                                    <tr>
                                        <td colSpan={6} className="px-6 py-12 text-center text-slate-500">
                                            <div className="flex flex-col items-center justify-center gap-3">
                                                <Activity className="w-8 h-8 text-slate-600/50" />
                                                <p className="text-sm font-medium">No background processes found.</p>
                                                <p className="text-xs opacity-70">Monitored processes include node, python, and playwright instances.</p>
                                            </div>
                                        </td>
                                    </tr>
                                ) : (
                                    <tr>
                                        <td colSpan={6} className="px-6 py-12 text-center text-slate-500">
                                            <div className="flex flex-col items-center justify-center gap-3">
                                                <RefreshCw className="w-6 h-6 animate-spin text-indigo-500/50" />
                                                <p className="text-sm">Scanning system...</p>
                                            </div>
                                        </td>
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
