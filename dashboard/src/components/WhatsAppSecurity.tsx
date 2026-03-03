import { useState, useEffect } from 'react';
import { Shield, ShieldAlert, ShieldCheck, Save, Users, MessageSquare, AlertTriangle, Fingerprint, CheckCircle } from 'lucide-react';
import { apiFetch } from '../lib/apiFetch';

export function WhatsAppSecurity({ isRunning }: { isRunning: boolean }) {
    const [config, setConfig] = useState<any>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [isSaving, setIsSaving] = useState(false);
    const [saveStatus, setSaveStatus] = useState<'idle' | 'saving' | 'saved'>('idle');

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
            const res = await apiFetch('/api/whatsapp/groups');
            const data = await res.json();
            if (data.groups) setAvailableGroups(data.groups);
        } catch (e) {
            console.error("Failed to fetch available groups", e);
        }
    };

    const fetchConfig = async () => {
        setIsLoading(true);
        try {
            const res = await apiFetch('/api/whatsapp/config');
            const data = await res.json();
            // Migrate legacy: convert plain string allowedGroups to objects
            if (data.allowedGroups && data.allowedGroups.length > 0 && typeof data.allowedGroups[0] === 'string') {
                data.allowedGroups = data.allowedGroups.map((jid: string) => ({
                    jid,
                    mode: data.botMode || 'mention'
                }));
            }
            setConfig(data);
        } catch (e) {
            console.error("Failed to fetch WhatsApp config", e);
        } finally {
            setIsLoading(false);
        }
    };

    const handleSave = async () => {
        setIsSaving(true);
        setSaveStatus('saving');
        try {
            await apiFetch('/api/whatsapp/config', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(config)
            });
            setSaveStatus('saved');
            setTimeout(() => setSaveStatus('idle'), 2500);
        } catch (e) {
            alert('Failed to save configuration');
            setSaveStatus('idle');
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
            const jid = targetValue.includes('@') ? targetValue : `${targetValue}@g.us`;
            const alreadyExists = config.allowedGroups.some((g: any) => g.jid === jid);
            if (!alreadyExists) {
                setConfig({ ...config, allowedGroups: [...config.allowedGroups, { jid, mode: 'mention' }] });
            }
            if (!val) setGroupInput('');
        }
    };

    const removeGroupTag = (jid: string) => {
        setConfig({ ...config, allowedGroups: config.allowedGroups.filter((g: any) => g.jid !== jid) });
    };

    const setGroupMode = (jid: string, mode: string) => {
        setConfig({
            ...config,
            allowedGroups: config.allowedGroups.map((g: any) => g.jid === jid ? { ...g, mode } : g)
        });
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
                    className={`px-6 py-2.5 rounded-xl text-sm font-semibold transition-all duration-300 flex items-center gap-2 shadow-lg ${saveStatus === 'saved'
                        ? 'bg-emerald-600 hover:bg-emerald-500 text-white shadow-emerald-900/30 scale-105'
                        : saveStatus === 'saving'
                            ? 'bg-amber-800 text-amber-200 cursor-not-allowed animate-pulse'
                            : 'bg-amber-600 hover:bg-amber-500 text-white shadow-amber-900/30'
                        }`}
                >
                    {saveStatus === 'saved' ? <CheckCircle className="w-4 h-4" /> : <Save className="w-4 h-4" />}
                    {saveStatus === 'saved' ? '✓ Rules Applied!' : isSaving ? 'Saving...' : 'Apply Security Rules'}
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
                            <div className="flex flex-col gap-3 animate-in fade-in slide-in-from-top-2">
                                <label className="text-[10px] uppercase tracking-widest text-slate-500 font-bold">Allowed Groups</label>

                                {/* Per-group list with individual mode toggles */}
                                {config.allowedGroups.length > 0 && (
                                    <div className="flex flex-col gap-2">
                                        {config.allowedGroups.map((group: any) => {
                                            const knownGroup = availableGroups.find(g => g.id === group.jid);
                                            const displayName = knownGroup ? knownGroup.subject : group.jid;
                                            const isListen = group.mode === 'listen';
                                            return (
                                                <div key={group.jid} title={group.jid} className="bg-slate-900/80 border border-slate-800 rounded-xl p-3 flex items-center justify-between gap-3 group hover:border-slate-700 transition-colors">
                                                    <div className="flex items-center gap-2.5 min-w-0 flex-1">
                                                        <Users className="w-4 h-4 text-slate-500 shrink-0" />
                                                        <div className="min-w-0">
                                                            <div className="text-sm font-medium text-white truncate">{displayName}</div>
                                                            {knownGroup && <div className="text-[10px] font-mono text-slate-500 truncate">{group.jid}</div>}
                                                        </div>
                                                    </div>
                                                    <div className="flex items-center gap-2 shrink-0">
                                                        <div className="flex bg-slate-950 rounded-lg p-0.5 border border-slate-800">
                                                            <button
                                                                onClick={() => setGroupMode(group.jid, 'mention')}
                                                                className={`px-3 py-1 text-[10px] uppercase tracking-wider font-bold rounded-md transition-all ${!isListen ? 'bg-indigo-600/20 text-indigo-400 border border-indigo-500/30 shadow-sm' : 'text-slate-500 hover:text-slate-300'
                                                                    }`}
                                                            >
                                                                Mention
                                                            </button>
                                                            <button
                                                                onClick={() => setGroupMode(group.jid, 'listen')}
                                                                className={`px-3 py-1 text-[10px] uppercase tracking-wider font-bold rounded-md transition-all ${isListen ? 'bg-emerald-600/20 text-emerald-400 border border-emerald-500/30 shadow-sm' : 'text-slate-500 hover:text-slate-300'
                                                                    }`}
                                                            >
                                                                Listen
                                                            </button>
                                                        </div>
                                                        <button
                                                            onClick={() => removeGroupTag(group.jid)}
                                                            className="p-1 text-slate-600 hover:text-red-400 transition-colors"
                                                            title="Remove group"
                                                        >
                                                            &times;
                                                        </button>
                                                    </div>
                                                </div>
                                            );
                                        })}
                                    </div>
                                )}

                                {/* Add group input */}
                                <div className="bg-slate-900 border border-slate-800 rounded-lg p-3 focus-within:border-rose-500/50 focus-within:ring-1 focus-within:ring-rose-500/50 transition-all cursor-text" onClick={() => document.getElementById('group-input')?.focus()}>
                                    <input
                                        id="group-input"
                                        type="text"
                                        placeholder={config.allowedGroups.length === 0 ? "Paste Group JID & press Enter..." : "Add another group JID..."}
                                        value={groupInput}
                                        onChange={(e) => setGroupInput(e.target.value)}
                                        onKeyDown={(e) => addGroupTag(e)}
                                        className="w-full bg-transparent border-none outline-none text-sm text-slate-300 font-mono placeholder:font-sans placeholder:text-slate-600"
                                    />
                                </div>

                                {/* Known groups dropdown */}
                                {availableGroups.length > 0 && (
                                    <div className="flex flex-col gap-1.5">
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
                                            {availableGroups.filter(g => !config.allowedGroups.some((ag: any) => ag.jid === g.id)).map(g => (
                                                <option key={g.id} value={g.id}>{g.subject} ({g.id})</option>
                                            ))}
                                        </select>
                                    </div>
                                )}

                                <div className="text-[10px] text-slate-500 leading-snug flex items-start gap-1.5 mt-1 bg-slate-950/50 p-3 rounded-lg border border-slate-800">
                                    <Fingerprint className="w-3 h-3 shrink-0 mt-0.5" />
                                    <span><strong className="text-indigo-400">Mention:</strong> Agent responds only when @tagged. <strong className="text-emerald-400">Listen:</strong> Agent reads and responds to every message (⚠️ burns tokens).</span>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </div>

            {/* Global Bot Attention Span removed — now per-group via individual toggles above */}
        </div>
    );
}
