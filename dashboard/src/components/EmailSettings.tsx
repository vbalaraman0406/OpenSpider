import { useState, useEffect } from 'react';
import { Mail, Save, CheckCircle } from 'lucide-react';
import { apiFetch } from '../lib/apiFetch';

export function EmailSettings() {
    const [config, setConfig] = useState({ cronResultsTo: '', vendorEmailTo: '', cronFromEmail: '' });
    const [isLoading, setIsLoading] = useState(true);
    const [isSaving, setIsSaving] = useState(false);
    const [saveStatus, setSaveStatus] = useState<'idle' | 'saving' | 'saved'>('idle');
    const [error, setError] = useState('');

    useEffect(() => {
        apiFetch('/api/email/config')
            .then(r => r.json())
            .then(data => setConfig({ cronResultsTo: data.cronResultsTo || '', vendorEmailTo: data.vendorEmailTo || '', cronFromEmail: data.cronFromEmail || '' }))
            .catch(e => console.error("Failed to fetch email config", e))
            .finally(() => setIsLoading(false));
    }, []);

    const handleSave = async () => {
        setIsSaving(true);
        setSaveStatus('saving');
        setError('');
        try {
            const res = await apiFetch('/api/email/config', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(config)
            });
            if (!res.ok) {
                const text = await res.text();
                try {
                    const errData = JSON.parse(text);
                    setError(errData.error || `Server error (${res.status})`);
                } catch {
                    setError(`Server returned ${res.status}. Rebuild & restart the gateway to apply new API routes.`);
                }
                setSaveStatus('idle');
                return;
            }
            const data = await res.json();
            if (data.error) {
                setError(data.error);
                setSaveStatus('idle');
            } else {
                setSaveStatus('saved');
                setTimeout(() => setSaveStatus('idle'), 2500);
            }
        } catch (e) {
            setError('Cannot reach gateway. Is the server running? Rebuild with: npm run build');
            setSaveStatus('idle');
        } finally {
            setIsSaving(false);
        }
    };

    if (isLoading) {
        return <div className="p-8 text-center text-slate-500 animate-pulse">Loading Email Settings...</div>;
    }

    return (
        <div className="flex flex-col gap-6 animate-in fade-in slide-in-from-bottom-4 duration-500 mt-8">
            <div className="flex justify-between items-end mb-2">
                <div>
                    <h3 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
                        <Mail className="w-5 h-5 text-sky-400" />
                        Email Notification Settings
                    </h3>
                    <p className="text-sm text-slate-400 mt-1">
                        Configure where automated emails and notifications are delivered.
                    </p>
                </div>
                <button
                    onClick={handleSave}
                    disabled={isSaving}
                    className={`px-6 py-2.5 rounded-xl text-sm font-semibold transition-all duration-300 flex items-center gap-2 shadow-lg ${saveStatus === 'saved'
                        ? 'bg-emerald-600 hover:bg-emerald-500 text-white shadow-emerald-900/30 scale-105'
                        : saveStatus === 'saving'
                            ? 'bg-sky-800 text-sky-200 cursor-not-allowed animate-pulse'
                            : 'bg-sky-600 hover:bg-sky-500 text-white shadow-sky-900/30'
                        }`}
                >
                    {saveStatus === 'saved' ? <CheckCircle className="w-4 h-4" /> : <Save className="w-4 h-4" />}
                    {saveStatus === 'saved' ? '✓ Saved!' : isSaving ? 'Saving...' : 'Save Email Settings'}
                </button>
            </div>

            {error && (
                <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-3 text-sm text-red-400 font-medium animate-in fade-in">
                    {error}
                </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Cron Result Emails */}
                <div className="bg-slate-950/50 rounded-2xl border border-slate-800 p-6 flex flex-col shadow-inner">
                    <div className="flex items-center gap-3 mb-4">
                        <div className="p-2 rounded-lg border bg-sky-500/10 text-sky-400 border-sky-500/20 flex items-center justify-center">
                            <Mail className="w-5 h-5" />
                        </div>
                        <div>
                            <h4 className="text-base font-bold text-white">Cron Job Results</h4>
                            <p className="text-xs text-slate-500">Receive automated job results by email</p>
                        </div>
                    </div>
                    <label className="text-[10px] uppercase tracking-widest text-slate-500 font-bold mb-2">To: Email Address</label>
                    <input
                        type="email"
                        placeholder="admin@example.com"
                        value={config.cronResultsTo}
                        onChange={e => setConfig({ ...config, cronResultsTo: e.target.value })}
                        className="w-full bg-slate-900 border border-slate-800 rounded-lg p-3 text-sm text-slate-200 focus:ring-1 focus:ring-sky-500 focus:border-sky-500 outline-none font-mono"
                    />
                    <p className="text-[10px] text-slate-500 mt-2 leading-snug">
                        Leave empty to disable email delivery of cron job results.
                    </p>
                </div>

                {/* Vendor / Friend Emails */}
                <div className="bg-slate-950/50 rounded-2xl border border-slate-800 p-6 flex flex-col shadow-inner">
                    <div className="flex items-center gap-3 mb-4">
                        <div className="p-2 rounded-lg border bg-amber-500/10 text-amber-400 border-amber-500/20 flex items-center justify-center">
                            <Mail className="w-5 h-5" />
                        </div>
                        <div>
                            <h4 className="text-base font-bold text-white">Vendor & Friends</h4>
                            <p className="text-xs text-slate-500">Default recipient for outbound emails</p>
                        </div>
                    </div>
                    <label className="text-[10px] uppercase tracking-widest text-slate-500 font-bold mb-2">To: Email Address</label>
                    <input
                        type="email"
                        placeholder="vendor@example.com"
                        value={config.vendorEmailTo}
                        onChange={e => setConfig({ ...config, vendorEmailTo: e.target.value })}
                        className="w-full bg-slate-900 border border-slate-800 rounded-lg p-3 text-sm text-slate-200 focus:ring-1 focus:ring-amber-500 focus:border-amber-500 outline-none font-mono"
                    />
                    <p className="text-[10px] text-slate-500 mt-2 leading-snug">
                        Default email address used when the agent sends emails to vendors, friends, or external parties.
                    </p>
                </div>
            </div>

            {/* Cron From Alias */}
            <div className="bg-slate-950/50 rounded-2xl border border-violet-800/30 p-6 flex flex-col shadow-inner">
                <div className="flex items-center gap-3 mb-4">
                    <div className="p-2 rounded-lg border bg-violet-500/10 text-violet-400 border-violet-500/20 flex items-center justify-center">
                        <Mail className="w-5 h-5" />
                    </div>
                    <div>
                        <h4 className="text-base font-bold text-white">Cron Job Sender Alias</h4>
                        <p className="text-xs text-slate-500">The "From" address used when the agent sends automated cron emails</p>
                    </div>
                </div>
                <label className="text-[10px] uppercase tracking-widest text-slate-500 font-bold mb-2">From: Email Address (Alias)</label>
                <input
                    type="email"
                    placeholder="agent@gmail.com"
                    value={config.cronFromEmail}
                    onChange={e => setConfig({ ...config, cronFromEmail: e.target.value })}
                    className="w-full bg-slate-900 border border-slate-800 rounded-lg p-3 text-sm text-slate-200 focus:ring-1 focus:ring-violet-500 focus:border-violet-500 outline-none font-mono"
                />
                <p className="text-[10px] text-slate-500 mt-2 leading-snug">
                    Must be a verified Gmail alias on the sender account. Leave empty to use default sender.
                </p>
            </div>
        </div>
    );
}
