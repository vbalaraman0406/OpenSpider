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
            // Migrate legacy: convert plain string allowedDMs to objects
            if (data.allowedDMs && data.allowedDMs.length > 0) {
                data.allowedDMs = data.allowedDMs.map((entry: any) => {
                    if (typeof entry === 'string') {
                        return { number: entry, mode: 'always' };
                    }
                    return entry;
                });
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
            }
            // Accept international numbers (5-15 digits)
            if (val.length < 5 || val.length > 15) {
                setDmError('Please enter a valid phone number (5-15 digits).');
                return;
            }

            const exists = config.allowedDMs.some((entry: any) =>
                (entry.number || '').replace(/\D/g, '') === val
            );
            if (!exists) {
                setConfig({ ...config, allowedDMs: [...config.allowedDMs, { number: val, mode: 'mention' }] });
            }
            setDmInput('');
            setDmError('');
        }
    };

    const removeDmTag = (number: string) => {
        setConfig({ ...config, allowedDMs: config.allowedDMs.filter((entry: any) => (entry.number || entry) !== number) });
    };

    const setDmMode = (number: string, mode: string) => {
        setConfig({
            ...config,
            allowedDMs: config.allowedDMs.map((entry: any) => (entry.number || entry) === number ? { ...entry, mode } : entry)
        });
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
                            <div className="flex flex-col gap-3 animate-in fade-in slide-in-from-top-2">
                                <label className="text-[10px] uppercase tracking-widest text-slate-500 font-bold">Allowed Contacts</label>

                                {/* Per-contact list with individual mode toggles */}
                                {config.allowedDMs.length > 0 && (
                                    <div className="flex flex-col gap-2">
                                        {config.allowedDMs.map((entry: any) => {
                                            const number = entry.number || entry;
                                            const isAlways = (entry.mode || 'always') === 'always';
                                            return (
                                                <div key={number} className="bg-slate-900/80 border border-slate-800 rounded-xl p-3 flex items-center justify-between gap-3 group hover:border-slate-700 transition-colors">
                                                    <div className="flex items-center gap-2.5 min-w-0 flex-1">
                                                        <MessageSquare className="w-4 h-4 text-slate-500 shrink-0" />
                                                        <div className="min-w-0">
                                                            <div className="text-sm font-medium text-white font-mono">+{number}</div>
                                                            {entry.lid && <div className="text-[10px] font-mono text-slate-500 truncate">LID: {entry.lid}</div>}
                                                        </div>
                                                    </div>
                                                    <div className="flex items-center gap-2 shrink-0">
                                                        <div className="flex bg-slate-950 rounded-lg p-0.5 border border-slate-800">
                                                            <button
                                                                onClick={() => setDmMode(number, 'mention')}
                                                                className={`px-3 py-1 text-[10px] uppercase tracking-wider font-bold rounded-md transition-all ${!isAlways ? 'bg-indigo-600/20 text-indigo-400 border border-indigo-500/30 shadow-sm' : 'text-slate-500 hover:text-slate-300'}`}
                                                            >
                                                                Mention
                                                            </button>
                                                            <button
                                                                onClick={() => setDmMode(number, 'always')}
                                                                className={`px-3 py-1 text-[10px] uppercase tracking-wider font-bold rounded-md transition-all ${isAlways ? 'bg-emerald-600/20 text-emerald-400 border border-emerald-500/30 shadow-sm' : 'text-slate-500 hover:text-slate-300'}`}
                                                            >
                                                                Always
                                                            </button>
                                                        </div>
                                                        <button
                                                            onClick={() => removeDmTag(number)}
                                                            className="p-1 text-slate-600 hover:text-red-400 transition-colors"
                                                            title="Remove contact"
                                                        >
                                                            &times;
                                                        </button>
                                                    </div>
                                                </div>
                                            );
                                        })}
                                    </div>
                                )}

                                {/* Add DM input */}
                                <div className="bg-slate-900 border border-slate-800 rounded-lg p-3 focus-within:border-indigo-500/50 focus-within:ring-1 focus-within:ring-indigo-500/50 transition-all cursor-text" onClick={() => document.getElementById('dm-input')?.focus()}>
                                    <input
                                        id="dm-input"
                                        type="text"
                                        placeholder={config.allowedDMs.length === 0 ? "Type phone number & press Enter..." : "Add another number..."}
                                        value={dmInput}
                                        onChange={(e) => { setDmInput(e.target.value); setDmError(''); }}
                                        onKeyDown={addDmTag}
                                        className="w-full bg-transparent border-none outline-none text-sm text-slate-300 font-mono placeholder:font-sans placeholder:text-slate-600"
                                    />
                                </div>
                                {dmError && <p className="text-xs text-red-500 font-medium animate-in fade-in">{dmError}</p>}
                                <div className="text-[10px] text-slate-500 leading-snug flex items-start gap-1.5 mt-1 bg-slate-950/50 p-3 rounded-lg border border-slate-800">
                                    <Fingerprint className="w-3 h-3 shrink-0 mt-0.5" />
                                    <span><strong className="text-indigo-400">Mention:</strong> Agent only responds when @mentioned. <strong className="text-emerald-400">Always:</strong> Agent responds to every message. LIDs auto-discovered on first contact.</span>
                                </div>
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

            {/* LID Identity Mappings Card */}
            <LidMappingsPanel />

            {/* Global Bot Attention Span removed — now per-group via individual toggles above */}
        </div>
    );
}

function LidMappingsPanel() {
    const [mappings, setMappings] = useState<Record<string, string>>({});
    const [pendingLids, setPendingLids] = useState<string[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [phoneInputs, setPhoneInputs] = useState<Record<string, string>>({});
    const [error, setError] = useState('');
    const [successMsg, setSuccessMsg] = useState('');

    const fetchAll = async () => {
        try {
            const [mappingsRes, pendingRes] = await Promise.all([
                apiFetch('/api/whatsapp/lid-mappings'),
                apiFetch('/api/whatsapp/lid-pending')
            ]);
            const mappingsData = await mappingsRes.json();
            const pendingData = await pendingRes.json();
            setMappings(mappingsData.mappings || {});
            setPendingLids(pendingData.pending || []);
        } catch (e) {
            console.error("Failed to fetch LID data", e);
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => { fetchAll(); }, []);

    const handleMap = async (lid: string) => {
        const phone = (phoneInputs[lid] || '').trim().replace(/\D/g, '');
        if (!phone || phone.length < 5) { setError(`Enter a valid phone number (5+ digits) for LID ${lid}.`); return; }

        try {
            const res = await apiFetch('/api/whatsapp/lid-map', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ lid, phone })
            });
            const data = await res.json();
            if (data.success) {
                setPhoneInputs(prev => { const n = { ...prev }; delete n[lid]; return n; });
                setError('');
                setSuccessMsg(`Mapped LID ${lid} → +${phone}`);
                setTimeout(() => setSuccessMsg(''), 3000);
                fetchAll();
            } else {
                setError(data.error || 'Failed to add mapping');
            }
        } catch (e) {
            setError('Network error — is the gateway running?');
        }
    };

    const handleRemove = async (lid: string) => {
        try {
            await apiFetch(`/api/whatsapp/lid-map/${lid}`, { method: 'DELETE' });
            fetchAll();
        } catch (e) { }
    };

    const entries = Object.entries(mappings);

    return (
        <div className="bg-slate-950/50 rounded-2xl border border-slate-800 p-6 flex flex-col shadow-inner mt-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="flex items-center gap-3 mb-6">
                <div className="p-2 rounded-lg border bg-violet-500/10 text-violet-400 border-violet-500/20 flex items-center justify-center">
                    <Fingerprint className="w-5 h-5" />
                </div>
                <div>
                    <h4 className="text-base font-bold text-white">LID Identity Mappings</h4>
                    <p className="text-xs text-slate-500">Resolve WhatsApp Linked Identity JIDs to phone numbers</p>
                </div>
                <div className="ml-auto flex gap-2">
                    {pendingLids.length > 0 && (
                        <div className="text-xs text-amber-400 font-bold bg-amber-500/10 px-2 py-1 rounded border border-amber-500/20 animate-pulse">
                            {pendingLids.length} pending
                        </div>
                    )}
                    <div className="text-xs text-slate-500 font-mono bg-slate-900 px-2 py-1 rounded border border-slate-800">
                        {entries.length} mapped
                    </div>
                </div>
            </div>

            {isLoading ? (
                <div className="text-center text-slate-500 animate-pulse py-6">Loading mappings...</div>
            ) : (
                <>
                    {/* Pending LIDs — need phone assignment */}
                    {pendingLids.length > 0 && (
                        <div className="mb-4">
                            <div className="text-[10px] uppercase tracking-widest text-amber-400 font-bold mb-2 flex items-center gap-1.5">
                                <AlertTriangle className="w-3 h-3" />
                                Blocked — Awaiting Phone Assignment
                            </div>
                            <div className="flex flex-col gap-2">
                                {pendingLids.map(lid => (
                                    <div key={lid} className="bg-amber-500/5 border border-amber-500/20 rounded-xl p-3 flex items-center gap-3">
                                        <div className="min-w-0 flex-shrink-0">
                                            <div className="text-amber-400 text-[10px] font-bold uppercase tracking-wider">LID</div>
                                            <div className="text-slate-200 font-mono text-sm truncate max-w-[200px]" title={lid}>{lid}</div>
                                        </div>
                                        <span className="text-slate-600 shrink-0">→</span>
                                        <input
                                            type="text"
                                            placeholder="Enter phone number..."
                                            value={phoneInputs[lid] || ''}
                                            onChange={e => setPhoneInputs(prev => ({ ...prev, [lid]: e.target.value }))}
                                            onKeyDown={e => { if (e.key === 'Enter') handleMap(lid); }}
                                            className="flex-1 bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-200 font-mono focus:ring-1 focus:ring-amber-500 focus:border-amber-500 outline-none placeholder:text-slate-600"
                                        />
                                        <button
                                            onClick={() => handleMap(lid)}
                                            className="px-4 py-2 bg-amber-600 hover:bg-amber-500 text-white rounded-lg text-sm font-semibold transition-all shadow-md shadow-amber-900/30 border border-amber-500/50 whitespace-nowrap"
                                        >
                                            Map
                                        </button>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Existing mapped entries */}
                    {entries.length > 0 && (
                        <div className="flex flex-col gap-2 mb-4">
                            <div className="text-[10px] uppercase tracking-widest text-emerald-400 font-bold mb-1 flex items-center gap-1.5">
                                <CheckCircle className="w-3 h-3" />
                                Resolved Mappings
                            </div>
                            {entries.map(([lid, phone]) => (
                                <div key={lid} className="bg-slate-900/80 border border-slate-800 rounded-xl p-3 flex items-center justify-between gap-3 group hover:border-slate-700 transition-colors">
                                    <div className="flex items-center gap-3 min-w-0 flex-1 font-mono text-sm">
                                        <div className="min-w-0">
                                            <div className="text-violet-400 text-xs font-bold uppercase tracking-wider">LID</div>
                                            <div className="text-slate-200 truncate">{lid}</div>
                                        </div>
                                        <span className="text-slate-600 shrink-0">→</span>
                                        <div className="min-w-0">
                                            <div className="text-emerald-400 text-xs font-bold uppercase tracking-wider">Phone</div>
                                            <div className="text-slate-200 truncate">+{phone}</div>
                                        </div>
                                    </div>
                                    <button
                                        onClick={() => handleRemove(lid)}
                                        className="p-1.5 text-slate-600 hover:text-red-400 transition-colors rounded-lg hover:bg-red-500/10"
                                        title="Remove mapping"
                                    >
                                        &times;
                                    </button>
                                </div>
                            ))}
                        </div>
                    )}

                    {pendingLids.length === 0 && entries.length === 0 && (
                        <div className="text-center text-slate-500 text-sm py-4 bg-slate-900/50 rounded-xl border border-slate-800/50 mb-4">
                            No LID mappings yet. When someone DMs from an unknown LID, it will appear here for you to assign a phone number.
                        </div>
                    )}

                    {error && <p className="text-xs text-red-500 font-medium mt-2 animate-in fade-in">{error}</p>}
                    {successMsg && <p className="text-xs text-emerald-400 font-medium mt-2 animate-in fade-in">✓ {successMsg}</p>}

                    <div className="text-[10px] text-slate-500 leading-snug flex items-start gap-1.5 mt-3 bg-slate-950/50 p-3 rounded-lg border border-slate-800">
                        <Fingerprint className="w-3 h-3 shrink-0 mt-0.5" />
                        <span>When an unknown LID tries to DM, it's blocked and shown here as <strong className="text-amber-400">pending</strong>. Type the phone number and click Map to allow. Or use WhatsApp: <strong className="text-violet-400">map &lt;LID&gt; &lt;PHONE&gt;</strong></span>
                    </div>
                </>
            )}
        </div>
    );
}

