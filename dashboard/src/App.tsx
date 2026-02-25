import { useState, useEffect, useRef } from 'react';
import { Activity, Terminal, CheckCircle2, Server, Key, Bot } from 'lucide-react';

interface LogMessage {
    type: string;
    data: string;
    timestamp: string;
}

export default function App() {
    const [logs, setLogs] = useState<LogMessage[]>([]);
    const [config, setConfig] = useState({ provider: 'Loading...', status: 'connecting' });
    const [skills, setSkills] = useState<string[]>([]);
    const scrollRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        // Fetch initial config
        fetch('/api/config')
            .then(r => r.json())
            .then(data => setConfig(data))
            .catch(e => console.error("Could not fetch config API", e));

        fetch('/api/skills')
            .then(r => r.json())
            .then(data => setSkills(data.skills))
            .catch(e => console.error("Could not fetch skills API", e));

        // Connect WebSocket for live logs
        const ws = new WebSocket('ws://localhost:4000');

        ws.onmessage = (event) => {
            try {
                const msg = JSON.parse(event.data);
                if (msg.type === 'log') {
                    setLogs(prev => [...prev.slice(-499), msg]); // Keep last 500 logs
                }
            } catch (e) { }
        };

        ws.onopen = () => setConfig(prev => ({ ...prev, status: 'connected' }));
        ws.onclose = () => setConfig(prev => ({ ...prev, status: 'disconnected' }));

        return () => ws.close();
    }, []);

    // Auto-scroll logs
    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [logs]);

    return (
        <div className="min-h-screen bg-slate-950 flex flex-col font-sans text-slate-300">
            {/* Header */}
            <header className="bg-slate-900 border-b border-slate-800 p-4 flex items-center justify-between sticky top-0 z-10 transition-all shadow-sm">
                <div className="flex items-center gap-3">
                    <div className="p-2 bg-blue-500/10 rounded-lg">
                        <Bot className="w-6 h-6 text-blue-400" />
                    </div>
                    <div>
                        <h1 className="text-xl font-semibold text-white tracking-tight">OpenSpider Dashboard</h1>
                        <p className="text-xs text-slate-400 tracking-wide font-medium">Autonomous Multi-Agent Engine</p>
                    </div>
                </div>

                <div className="flex gap-4">
                    <div className="flex flex-col items-end">
                        <div className="flex items-center gap-2">
                            <span className="text-sm font-medium">LLM Provider</span>
                        </div>
                        <span className="text-xs font-mono text-blue-400 bg-blue-500/10 px-2 py-0.5 rounded-full mt-1 border border-blue-500/20">{config.provider.toUpperCase()}</span>
                    </div>
                    <div className="h-10 w-px bg-slate-800 mx-2"></div>
                    <div className="flex flex-col items-end">
                        <div className="flex items-center gap-2">
                            <div className={\`w-2 h-2 rounded-full \${config.status === 'connected' ? 'bg-emerald-500 animate-pulse' : 'bg-red-500'}\`}></div>
                        <span className="text-sm font-medium">Engine Status</span>
                    </div>
                    <span className="text-xs text-slate-400 capitalize mt-1 tracking-wide">{config.status}</span>
                </div>
        </div>
      </header >

        {/* Main Content */ }
        < main className = "flex-1 p-6 flex gap-6 overflow-hidden max-w-[1600px] w-full mx-auto" >

            {/* Left Column: Logs */ }
            < section className = "flex-1 flex flex-col bg-slate-900/50 rounded-xl border border-slate-800/60 overflow-hidden shadow-lg backdrop-blur-sm" >
          <div className="p-4 border-b border-slate-800/60 flex items-center gap-2 bg-slate-900">
            <Terminal className="w-5 h-5 text-slate-400" />
            <h2 className="font-semibold text-slate-200">Live Agent Communications</h2>
          </div>
          <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 font-mono text-sm space-y-2">
            {logs.length === 0 ? (
                <div className="text-slate-500 flex flex-col items-center justify-center h-full opacity-60">
                    <Activity className="w-12 h-12 mb-4 animate-pulse" />
                    <span>Awaiting agent activity...</span>
                </div>
            ) : logs.map((log, i) => (
              <div key={i} className="flex gap-3 hover:bg-slate-800/30 p-1.5 rounded transition-colors group">
                <span className="text-slate-500 shrink-0 select-none text-xs mt-0.5">
                  {new Date(log.timestamp).toLocaleTimeString([], { hour12: false, hour: '2-digit', minute:'2-digit', second:'2-digit' })}
                </span>
                <span className={\`break-all leading-relaxed \${
                    log.data.includes('[Manager]') ? 'text-amber-300' :
                    log.data.includes('[Worker') ? 'text-emerald-300' :
                    log.data.includes('[WhatsApp]') ? 'text-blue-300' :
                    log.data.includes('Error') ? 'text-red-400 font-semibold' : 'text-slate-300'
                }\`}>
                  {log.data}
                </span>
              </div>
            ))
}
          </div >
        </section >

    {/* Right Column: Diagnostics */ }
    < aside className = "w-[380px] flex flex-col gap-6" >

        {/* Dynamic Skills */ }
        < div className = "bg-slate-900/50 rounded-xl border border-slate-800/60 p-5 shadow-lg backdrop-blur-sm" >
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

    {/* System Info */ }
    < div className = "bg-slate-900/50 rounded-xl border border-slate-800/60 p-5 shadow-lg backdrop-blur-sm" >
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

      </main >
    </div >
  );
}
