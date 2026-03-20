import { useState, useEffect } from 'react';
import { Mic, Save, CheckCircle, Volume2, Play, RefreshCw, Loader2 } from 'lucide-react';
import { apiFetch } from '../lib/apiFetch';

const ELEVENLABS_VOICES = [
    { id: '21m00Tcm4TlvDq8ikWAM', name: 'Rachel', style: 'Warm female', accent: 'American' },
    { id: 'EXAVITQu4vr4xnSDxMaL', name: 'Bella', style: 'Soft female', accent: 'American' },
    { id: 'ErXwobaYiN019PkySvjV', name: 'Antoni', style: 'Calm male', accent: 'American' },
    { id: 'VR6AewLTigWG4xSOukaG', name: 'Arnold', style: 'Deep male', accent: 'American' },
    { id: 'pNInz6obpgDQGcFmaJgB', name: 'Adam', style: 'Confident male', accent: 'American' },
    { id: 'yoZ06aMxZJJ28mfd3POQ', name: 'Sam', style: 'Clear male', accent: 'American' },
    { id: 'AZnzlk1XvdvUeBnXmlld', name: 'Domi', style: 'Strong female', accent: 'American' },
    { id: 'MF3mGyEYCl7XYWbV9V6O', name: 'Elli', style: 'Cheerful female', accent: 'American' },
    { id: 'TxGEqnHWrfWFTfGW9XjX', name: 'Josh', style: 'Deep male', accent: 'American' },
    { id: 'jBpfuIE2acCO8z3wKNLl', name: 'Gigi', style: 'Childlike female', accent: 'American' },
];

export function VoiceSettings() {
    const [config, setConfig] = useState<any>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [saveStatus, setSaveStatus] = useState<'idle' | 'saving' | 'saved'>('idle');
    const [previewVoice, setPreviewVoice] = useState<string | null>(null);
    const [customVoices, setCustomVoices] = useState<typeof ELEVENLABS_VOICES>([]);
    const [isFetchingVoices, setIsFetchingVoices] = useState(false);

    useEffect(() => {
        fetchConfig();
    }, []);

    const fetchConfig = async () => {
        setIsLoading(true);
        try {
            const res = await apiFetch('/api/voice/config');
            const data = await res.json();
            setConfig(data);
            if (data.elevenlabsApiKey) {
                fetchCustomVoices(data.elevenlabsApiKey);
            }
        } catch (e) {
            console.error("Failed to fetch voice config", e);
            setConfig({
                voiceId: '21m00Tcm4TlvDq8ikWAM',
                voiceName: 'Rachel',
                elevenlabsApiKey: '',
                whisperModel: 'base'
            });
        } finally {
            setIsLoading(false);
        }
    };

    const fetchCustomVoices = async (apiKey: string) => {
        if (!apiKey) return;
        setIsFetchingVoices(true);
        try {
            const res = await fetch('https://api.elevenlabs.io/v1/voices', {
                headers: { 'xi-api-key': apiKey }
            });
            if (res.ok) {
                const data = await res.json();
                const custom = data.voices.filter((v: any) => v.category !== 'premade');
                setCustomVoices(
                    custom.map((v: any) => ({
                        id: v.voice_id,
                        name: v.name,
                        style: v.labels?.description || 'Custom',
                        accent: v.labels?.accent || 'Personal'
                    }))
                );
            }
        } catch (e) {
            console.error("Failed to fetch user voices from ElevenLabs", e);
        } finally {
            setIsFetchingVoices(false);
        }
    };

    const handleSave = async () => {
        setSaveStatus('saving');
        try {
            await apiFetch('/api/voice/config', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(config)
            });
            setSaveStatus('saved');
            setTimeout(() => setSaveStatus('idle'), 2500);
        } catch (e) {
            alert('Failed to save voice configuration');
            setSaveStatus('idle');
        }
    };

    const selectVoice = (voice: typeof ELEVENLABS_VOICES[0]) => {
        setConfig({ ...config, voiceId: voice.id, voiceName: voice.name });
    };

    if (isLoading || !config) {
        return <div className="p-8 text-center text-slate-500 animate-pulse">Loading Voice Settings...</div>;
    }

    const allVoices = [...ELEVENLABS_VOICES, ...customVoices];

    return (
        <div className="flex flex-col gap-6 animate-in fade-in slide-in-from-bottom-4 duration-500 mt-8">
            <div className="flex justify-between items-end mb-2">
                <div>
                    <h3 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
                        <Volume2 className="w-5 h-5 text-violet-400" />
                        Voice Configuration
                    </h3>
                    <p className="text-sm text-slate-400 mt-1">
                        Configure text-to-speech voice for agent audio replies via ElevenLabs.
                    </p>
                </div>
                <button
                    onClick={handleSave}
                    className={`px-6 py-2.5 rounded-xl text-sm font-semibold transition-all duration-300 flex items-center gap-2 shadow-lg ${saveStatus === 'saved'
                        ? 'bg-emerald-600 hover:bg-emerald-500 text-white shadow-emerald-900/30 scale-105'
                        : saveStatus === 'saving'
                            ? 'bg-violet-800 text-violet-200 cursor-not-allowed animate-pulse'
                            : 'bg-violet-600 hover:bg-violet-500 text-white shadow-violet-900/30'
                        }`}
                >
                    {saveStatus === 'saved' ? <CheckCircle className="w-4 h-4" /> : <Save className="w-4 h-4" />}
                    {saveStatus === 'saved' ? '✓ Saved!' : saveStatus === 'saving' ? 'Saving...' : 'Save Voice Settings'}
                </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Voice Selection Card */}
                <div className="bg-slate-950/50 rounded-2xl border border-slate-800 p-6 flex flex-col shadow-inner md:col-span-2">
                    <div className="flex items-center gap-3 mb-6">
                        <div className="p-2 rounded-lg border bg-violet-500/10 text-violet-400 border-violet-500/20 flex items-center justify-center">
                            <Mic className="w-5 h-5" />
                        </div>
                        <div>
                            <h4 className="text-base font-bold text-white">Agent Voice</h4>
                            <p className="text-xs text-slate-500">Select the voice your agent uses for audio replies</p>
                        </div>
                    </div>

                    <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
                        {allVoices.map(voice => {
                            const isSelected = config.voiceId === voice.id;
                            return (
                                <button
                                    key={voice.id}
                                    onClick={() => selectVoice(voice)}
                                    className={`relative flex flex-col items-center gap-2 p-4 rounded-xl border transition-all duration-300 group ${isSelected
                                        ? 'bg-violet-500/15 border-violet-500/40 ring-2 ring-violet-500/30 shadow-[0_0_20px_rgba(139,92,246,0.15)]'
                                        : 'bg-slate-900/60 border-slate-800 hover:border-slate-700 hover:bg-slate-900'
                                        }`}
                                >
                                    <div className={`w-12 h-12 rounded-full flex items-center justify-center text-lg font-bold transition-all ${isSelected
                                        ? 'bg-violet-500/20 text-violet-300 border-2 border-violet-500/40'
                                        : 'bg-slate-800 text-slate-400 border-2 border-slate-700 group-hover:border-slate-600'
                                        }`}>
                                        {voice.name.charAt(0)}
                                    </div>
                                    <div className="text-center">
                                        <div className={`text-sm font-semibold flex items-center justify-center gap-1 ${isSelected ? 'text-violet-300' : 'text-slate-300'}`}>
                                            {voice.name}
                                            {customVoices.some(cv => cv.id === voice.id) && (
                                                <span className="w-1.5 h-1.5 rounded-full bg-amber-400 inline-block ml-0.5" title="Custom Voice"></span>
                                            )}
                                        </div>
                                        <div className="text-[10px] text-slate-500 mt-0.5">{voice.style}</div>
                                    </div>
                                    {isSelected && (
                                        <div className="absolute top-2 right-2">
                                            <CheckCircle className="w-4 h-4 text-violet-400" />
                                        </div>
                                    )}
                                </button>
                            );
                        })}
                    </div>

                    {/* Custom Voice ID */}
                    <div className="mt-6 flex flex-col gap-2">
                        <label className="text-[10px] uppercase tracking-widest text-slate-500 font-bold">Custom Voice ID</label>
                        <input
                            type="text"
                            value={config.voiceId || ''}
                            onChange={(e) => setConfig({ ...config, voiceId: e.target.value, voiceName: 'Custom' })}
                            placeholder="Paste an ElevenLabs voice ID..."
                            className="w-full bg-slate-900 border border-slate-800 rounded-lg p-3 text-sm text-slate-300 font-mono focus:ring-1 focus:ring-violet-500 focus:border-violet-500 outline-none placeholder:font-sans placeholder:text-slate-600"
                        />
                        <p className="text-[10px] text-slate-600 leading-snug">You can use any voice from your ElevenLabs library. Paste the voice ID here or select a preset above.</p>
                    </div>
                </div>

                {/* API Key Card */}
                <div className="bg-slate-950/50 rounded-2xl border border-slate-800 p-6 flex flex-col shadow-inner">
                    <div className="flex items-center gap-3 mb-6">
                        <div className="p-2 rounded-lg border bg-amber-500/10 text-amber-400 border-amber-500/20 flex items-center justify-center">
                            <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M15 7h2a5 5 0 013 9h-2M9 12H4M9 12a3 3 0 100 6 3 3 0 000-6z" /></svg>
                        </div>
                        <div>
                            <h4 className="text-base font-bold text-white">ElevenLabs API Key</h4>
                            <p className="text-xs text-slate-500">Required for voice message replies</p>
                        </div>
                    </div>
                    <input
                        type="password"
                        value={config.elevenlabsApiKey || ''}
                        onChange={(e) => setConfig({ ...config, elevenlabsApiKey: e.target.value })}
                        placeholder="sk_..."
                        className="w-full bg-slate-900 border border-slate-800 rounded-lg p-3 text-sm text-slate-300 font-mono focus:ring-1 focus:ring-amber-500 focus:border-amber-500 outline-none placeholder:text-slate-600"
                    />
                    <div className="flex justify-between items-start mt-2">
                        <p className="text-[10px] text-slate-600 leading-snug">Get your API key from <a href="https://elevenlabs.io" target="_blank" rel="noreferrer" className="text-amber-400 hover:underline">elevenlabs.io</a>.</p>
                        {config.elevenlabsApiKey && (
                            <button 
                                onClick={() => fetchCustomVoices(config.elevenlabsApiKey)}
                                disabled={isFetchingVoices}
                                className="text-[10px] flex items-center gap-1.5 text-amber-500 hover:text-amber-400 font-bold transition-colors disabled:opacity-50 bg-amber-500/10 px-2 py-1 rounded border border-amber-500/20 shadow-sm whitespace-nowrap"
                            >
                                {isFetchingVoices ? <Loader2 className="w-3 h-3 animate-spin"/> : <RefreshCw className="w-3 h-3"/>}
                                {isFetchingVoices ? 'Syncing...' : 'Sync Custom Voices'}
                            </button>
                        )}
                    </div>
                </div>

                {/* Whisper Model Card */}
                <div className="bg-slate-950/50 rounded-2xl border border-slate-800 p-6 flex flex-col shadow-inner">
                    <div className="flex items-center gap-3 mb-6">
                        <div className="p-2 rounded-lg border bg-cyan-500/10 text-cyan-400 border-cyan-500/20 flex items-center justify-center">
                            <Mic className="w-5 h-5" />
                        </div>
                        <div>
                            <h4 className="text-base font-bold text-white">Whisper Model</h4>
                            <p className="text-xs text-slate-500">Speech-to-text model for incoming voice messages</p>
                        </div>
                    </div>
                    <div className="flex bg-slate-900 rounded-lg p-1 border border-slate-800/80">
                        {(['tiny', 'base', 'small', 'medium'] as const).map(model => (
                            <button
                                key={model}
                                onClick={() => setConfig({ ...config, whisperModel: model })}
                                className={`flex-1 px-3 py-2 text-xs font-semibold rounded-md transition-colors capitalize ${config.whisperModel === model
                                    ? 'bg-cyan-600/20 text-cyan-400 shadow-sm border border-cyan-500/20'
                                    : 'text-slate-500 hover:text-slate-300'
                                    }`}
                            >
                                {model}
                            </button>
                        ))}
                    </div>
                    <div className="mt-3 text-[10px] text-slate-600 leading-snug space-y-1">
                        <p><strong className="text-slate-400">tiny</strong> (~40MB) — Fastest, lowest accuracy</p>
                        <p><strong className="text-cyan-400">base</strong> (~150MB) — Good balance of speed and accuracy</p>
                        <p><strong className="text-slate-400">small</strong> (~500MB) — Better accuracy, slower</p>
                        <p><strong className="text-slate-400">medium</strong> (~1.5GB) — Best accuracy, slowest</p>
                    </div>
                </div>
            </div>
        </div>
    );
}
