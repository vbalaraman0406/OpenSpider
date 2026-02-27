import { useState, useEffect } from 'react';
import { Shield, ShieldAlert, ShieldCheck, Save, Users, MessageSquare, AlertTriangle, Fingerprint } from 'lucide-react';

export function WhatsAppSecurity({ isRunning }: { isRunning: boolean }) {
    const [config, setConfig] = useState<any>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [isSaving, setIsSaving] = useState(false);

    // Tag Input States
    const [dmInput, setDmInput] = useState('');
    const [dmError, setDmError] = useState('');
    const [groupInput, setGroupInput] = useState('');
    const [availableGroups, setAvailableGroups] = useState<{ id: string, subject: string }[]>([]);

    useEffect(() => {
        fetchConfig();
        fetchGroups();
    }, []);

    const fetchGroups = async () => {
        try {
            const res = await fetch('/api/whatsapp/groups');
            const data = await res.json();
            if (data.groups) setAvailableGroups(data.groups);
        } catch (e) {
            console.error("Failed to fetch available groups", e);
        }
    };

    const fetchConfig = async () => {
        setIsLoading(true);
        try {
            const res = await fetch('/api/whatsapp/config');
            const data = await res.json();
            setConfig(data);
        } catch (e) {
            console.error("Failed to fetch WhatsApp config", e);
        } finally {
            setIsLoading(false);
        }
    };

    const handleSave = async () => {
        setIsSaving(true);
        try {
            await fetch('/api/whatsapp/config', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(config)
            });
            // Show a success animation or toast here if global context allows
        } catch (e) {
            alert('Failed to save configuration');
        } finally {
            setIsSaving(false);
        }
    };

    const addDmTag = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && dmInput.trim() !== '') {
            e.preventDefault();
            let val = dmInput.trim().replace(/\D/g, ''); // strip non-numeric

            if (val.length === 10) {
                val = '1' + val; // Auto-prepend US country code
            } else if (val.length !== 11 || !val.startsWith('1')) {
                setDmError('Please enter a valid 10-digit US phone number (e.g. 555-123-4567).');
                return;
            }

            if (val && !config.allowedDMs.includes(val)) {
                setConfig({ ...config, allowedDMs: [...config.allowedDMs, val] });
            }
            setDmInput('');
            setDmError('');
        }
    };

    const removeDmTag = (tag: string) => {
        setConfig({ ...config, allowedDMs: config.allowedDMs.filter((t: string) => t !== tag) });
    };

    const addGroupTag = (e?: React.KeyboardEvent, val?: string) => {
        const targetValue = val || (e ? groupInput.trim() : '');
        if ((!e || e.key === 'Enter') && targetValue !== '') {
            if (e) e.preventDefault();
            // Basic sanity check, WhatsApp group JIDs end in @g.us
            if (!config.allowedGroups.includes(targetValue)) {
                setConfig({ ...config, allowedGroups: [...config.allowedGroups, targetValue.includes('@') ? targetValue : `${targetValue}@g.us`] });
            }
            if (!val) setGroupInput('');
        }
    };

    const removeGroupTag = (tag: string) => {
        setConfig({ ...config, allowedGroups: config.allowedGroups.filter((t: string) => t !== tag) });
    };

    if (isLoading || !config) {
        return <div className="p-8 text-center text-slate-500 animate-pulse">Loading Security Policies...</div>;
    }

    return (
        <div className="flex flex-col gap-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="flex justify-between items-end mb-2">
                <div>
                    <h3 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
                        <Shield className="w-5 h-5 text-indigo-400" />
                        Access Control Firewall
                    </h3>
                    <p className="text-sm text-slate-400 mt-1">
                        Secure your gateway. Drop unauthorized packets before they reach the LLM.
                    </p>
                </div>
                <button
                    onClick={handleSave}
                    disabled={isSaving}
                    className={`px-6 py-2.5 rounded-xl text-sm font-semibold transition-all flex items-center gap-2 shadow-lg ${isSaving ? 'bg-indigo-800 text-indigo-300 cursor-not-allowed' : 'bg-indigo-600 hover:bg-indigo-500 text-white shadow-indigo-900/20'}`}
                >
                    <Save className="w-4 h-4" />
                    {isSaving ? 'Saving...' : 'Apply Security Rules'}
                </button>
            </div>

            {!isRunning && (
                <div className="bg-amber-500/10 border border-amber-500/20 rounded-xl p-4 flex items-start gap-3">
                    <AlertTriangle className="w-5 h-5 text-amber-500 shrink-0 mt-0.5" />
                    <div>
                        <h4 className="text-sm font-semibold text-amber-400 leading-none mb-1">Gateway Offline</h4>
                        <p className="text-xs text-amber-500/80 leading-relaxed">Changes will be saved to disk, but won't actively filter traffic until the WhatsApp channel is restarted.</p>
                    </div>
                </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

                {/* Direct Messages Card */}
                <div className="bg-slate-950/50 rounded-2xl border border-slate-800 p-6 flex flex-col shadow-inner">
                    <div className="flex items-center gap-3 mb-6">
                        <div className={`p-2 rounded-lg border flex items-center justify-center ${config.dmPolicy === 'allowlist' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : config.dmPolicy === 'disabled' ? 'bg-red-500/10 text-red-500 border-red-500/20' : 'bg-slate-800 text-slate-400 border-slate-700'}`}>
                            {config.dmPolicy === 'disabled' ? <ShieldAlert className="w-5 h-5" /> : <MessageSquare className="w-5 h-5" />}
                        </div>
                        <div>
                            <h4 className="text-base font-bold text-white">Direct Messages</h4>
                            <p className="text-xs text-slate-500">1-on-1 SMS conversations</p>
                        </div>
                    </div>

                    <div className="space-y-5">
                        <div className="flex flex-col gap-2">
                            <label className="text-[10px] uppercase tracking-widest text-slate-500 font-bold">Policy Mode</label>
                            <div className="flex bg-slate-900 rounded-lg p-1 border border-slate-800/80 auto-cols-auto">
                                <button onClick={() => setConfig({ ...config, dmPolicy: 'open' })} className={`flex-1 px-3 py-1.5 text-xs font-semibold rounded-md transition-colors ${config.dmPolicy === 'open' ? 'bg-slate-800 text-white shadow-sm' : 'text-slate-500 hover:text-slate-300'}`}>Open</button>
                                <button onClick={() => setConfig({ ...config, dmPolicy: 'allowlist' })} className={`flex-1 flex items-center justify-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-md transition-colors ${config.dmPolicy === 'allowlist' ? 'bg-emerald-600/20 text-emerald-400 shadow-sm border border-emerald-500/20' : 'text-slate-500 hover:text-slate-300'}`}>Allowlist</button>
                                <button onClick={() => setConfig({ ...config, dmPolicy: 'disabled' })} className={`flex-1 px-3 py-1.5 text-xs font-semibold rounded-md transition-colors ${config.dmPolicy === 'disabled' ? 'bg-red-900/40 text-red-400 shadow-sm' : 'text-slate-500 hover:text-slate-300'}`}>Disabled</button>
                            </div>
                        </div>

                        {config.dmPolicy === 'allowlist' && (
                            <div className="flex flex-col gap-2 animate-in fade-in slide-in-from-top-2">
                                <label className="text-[10px] uppercase tracking-widest text-slate-500 font-bold">Allowed Numbers</label>
                                <div className="bg-slate-900 border border-slate-800 rounded-lg p-3 min-h-[100px] flex flex-wrap content-start gap-2 focus-within:border-indigo-500/50 focus-within:ring-1 focus-within:ring-indigo-500/50 transition-all cursor-text" onClick={() => document.getElementById('dm-input')?.focus()}>
                                    {config.allowedDMs.map((phone: string) => (
                                        <div key={phone} className="flex items-center gap-1.5 bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 px-2.5 py-1 rounded-md text-xs font-mono font-medium group">
                                            +{phone}
                                            <button onClick={(e) => { e.stopPropagation(); removeDmTag(phone); }} className="opacity-50 hover:opacity-100 hover:text-red-400 transition-colors">
                                                &times;
                                            </button>
                                        </div>
                                    ))}
                                    <input
                                        id="dm-input"
                                        type="text"
                                        placeholder={config.allowedDMs.length === 0 ? "Type US number & press Enter..." : ""}
                                        value={dmInput}
                                        onChange={(e) => { setDmInput(e.target.value); setDmError(''); }}
                                        onKeyDown={addDmTag}
                                        className="bg-transparent border-none outline-none text-sm text-slate-300 min-w-[120px] flex-1 font-mono placeholder:font-sans placeholder:text-slate-600"
                                    />
                                </div>
                                {dmError && <p className="text-xs text-red-500 font-medium animate-in fade-in">{dmError}</p>}
                                <p className="text-[10px] text-slate-600 leading-snug">Type a standard 10-digit US phone number. Non-numeric characters are ignored.</p>
                            </div>
                        )}
                    </div>
                </div>

                {/* Groups Card */}
                <div className="bg-slate-950/50 rounded-2xl border border-slate-800 p-6 flex flex-col shadow-inner">
                    <div className="flex items-center gap-3 mb-6">
                        <div className={`p-2 rounded-lg border flex items-center justify-center ${config.groupPolicy === 'allowlist' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : config.groupPolicy === 'disabled' ? 'bg-red-500/10 text-red-500 border-red-500/20' : 'bg-slate-800 text-slate-400 border-slate-700'}`}>
                            {config.groupPolicy === 'disabled' ? <ShieldAlert className="w-5 h-5" /> : <Users className="w-5 h-5" />}
                        </div>
                        <div>
                            <h4 className="text-base font-bold text-white">Group Chats</h4>
                            <p className="text-xs text-slate-500">Multi-user environments</p>
                        </div>
                    </div>

                    <div className="space-y-5">
                        <div className="flex flex-col gap-2">
                            <label className="text-[10px] uppercase tracking-widest text-slate-500 font-bold">Policy Mode</label>
                            <div className="flex bg-slate-900 rounded-lg p-1 border border-slate-800/80 auto-cols-auto">
                                <button onClick={() => setConfig({ ...config, groupPolicy: 'open' })} className={`flex-1 px-3 py-1.5 text-xs font-semibold rounded-md transition-colors ${config.groupPolicy === 'open' ? 'bg-slate-800 text-white shadow-sm' : 'text-slate-500 hover:text-slate-300'}`}>Open</button>
                                <button onClick={() => setConfig({ ...config, groupPolicy: 'allowlist' })} className={`flex-1 flex items-center justify-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-md transition-colors ${config.groupPolicy === 'allowlist' ? 'bg-emerald-600/20 text-emerald-400 shadow-sm border border-emerald-500/20' : 'text-slate-500 hover:text-slate-300'}`}>Allowlist</button>
                                <button onClick={() => setConfig({ ...config, groupPolicy: 'disabled' })} className={`flex-1 px-3 py-1.5 text-xs font-semibold rounded-md transition-colors ${config.groupPolicy === 'disabled' ? 'bg-red-900/40 text-red-400 shadow-sm' : 'text-slate-500 hover:text-slate-300'}`}>Disabled</button>
                            </div>
                        </div>

                        {config.groupPolicy === 'allowlist' && (
                            <div className="flex flex-col gap-2 animate-in fade-in slide-in-from-top-2">
                                <label className="text-[10px] uppercase tracking-widest text-slate-500 font-bold">Allowed Group JIDs</label>
                                <div className="bg-slate-900 border border-slate-800 rounded-lg p-3 min-h-[100px] flex flex-wrap content-start gap-2 focus-within:border-rose-500/50 focus-within:ring-1 focus-within:ring-rose-500/50 transition-all cursor-text" onClick={() => document.getElementById('group-input')?.focus()}>
                                    {config.allowedGroups.map((jid: string) => {
                                        const knownGroup = availableGroups.find(g => g.id === jid);
                                        const displayName = knownGroup ? knownGroup.subject : jid;
                                        return (
                                            <div key={jid} title={jid} className="flex items-center gap-1.5 bg-rose-500/10 border border-rose-500/20 text-rose-300 px-2.5 py-1 rounded-md text-[11px] font-mono font-medium group max-w-full">
                                                <span className="truncate">{displayName}</span>
                                                <button onClick={(e) => { e.stopPropagation(); removeGroupTag(jid); }} className="opacity-50 hover:opacity-100 hover:text-red-400 transition-colors shrink-0">
                                                    &times;
                                                </button>
                                            </div>
                                        );
                                    })}
                                    <input
                                        id="group-input"
                                        type="text"
                                        placeholder={config.allowedGroups.length === 0 ? "Paste JID & press Enter..." : (availableGroups.length > 0 ? "Or type JID manually..." : "Paste JID & press Enter...")}
                                        value={groupInput}
                                        onChange={(e) => setGroupInput(e.target.value)}
                                        onKeyDown={(e) => addGroupTag(e)}
                                        className="bg-transparent border-none outline-none text-sm text-slate-300 min-w-[120px] flex-1 font-mono placeholder:font-sans placeholder:text-slate-600"
                                    />
                                </div>
                                {availableGroups.length > 0 && (
                                    <div className="mt-2 flex flex-col gap-1.5">
                                        <label className="text-[10px] uppercase tracking-widest text-slate-400 font-bold">Recently Seen Groups</label>
                                        <select
                                            onChange={(e) => {
                                                if (e.target.value) {
                                                    addGroupTag(undefined, e.target.value);
                                                    e.target.value = '';
                                                }
                                            }}
                                            className="w-full bg-slate-950/80 border border-slate-800 text-slate-300 text-sm rounded-lg p-2 focus:ring-1 focus:ring-rose-500 outline-none appearance-none"
                                        >
                                            <option value="">Select a group to allow...</option>
                                            {availableGroups.filter(g => !config.allowedGroups.includes(g.id)).map(g => (
                                                <option key={g.id} value={g.id}>{g.subject} ({g.id})</option>
                                            ))}
                                        </select>
                                    </div>
                                )}
                                <div className="text-[10px] text-slate-600 leading-snug flex items-start gap-1.5 mt-2">
                                    <Fingerprint className="w-3 h-3 shrink-0 mt-0.5" />
                                    <span>WhatsApp Groups use internal JIDs (e.g. 12036315xxxx@g.us). Check the System Logs tab when someone messages the group to find its ID.</span>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </div>

            {(config.groupPolicy !== 'disabled') && (
                <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-inner animate-in fade-in">
                    <div className="flex justify-between items-center mb-4">
                        <div>
                            <h4 className="text-sm font-bold text-white mb-1">Bot Attention Span</h4>
                            <p className="text-xs text-slate-500">How the LLM decides to respond in authorized groups.</p>
                        </div>
                        <div className="flex bg-slate-950 rounded-lg p-1 border border-slate-800 max-w-[300px]">
                            <button onClick={() => setConfig({ ...config, botMode: 'mention' })} className={`flex-1 px-4 py-2 text-xs font-semibold rounded-md transition-colors ${config.botMode === 'mention' ? 'bg-indigo-600/20 text-indigo-400 font-bold border border-indigo-500/30 shadow-sm' : 'text-slate-500 hover:text-slate-300'}`}>Mention Only</button>
                            <button onClick={() => setConfig({ ...config, botMode: 'listen' })} className={`flex-1 px-4 py-2 text-xs font-semibold rounded-md transition-colors ${config.botMode === 'listen' ? 'bg-emerald-600/20 text-emerald-400 font-bold border border-emerald-500/30 shadow-sm' : 'text-slate-500 hover:text-slate-300'}`}>Full Listen</button>
                        </div>
                    </div>
                    <p className="text-xs text-slate-400 bg-slate-950/50 p-3 rounded-lg border border-slate-800">
                        {config.botMode === 'mention'
                            ? "Agent will ONLY process messages where it is explicitly tagged (@Agent) or mentioned by name. This prevents spamming."
                            : "Agent reads and responds contextually to every message sent in the group. Use with extreme caution as this burns API tokens rapidly!"}
                    </p>
                </div>
            )}
        </div>
    );
}
