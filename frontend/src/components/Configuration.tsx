import React, { useState, useEffect } from 'react';
import {
    Settings, Key, Globe, Database, Activity, CheckCircle2, AlertCircle, Loader2,
    Bug, Terminal, Copy, Download, RefreshCw, ChevronDown, ChevronRight, Save,
    Cpu, Layers, ChevronUp, ExternalLink, Coins, Palette
} from 'lucide-react';
import { API_BASE } from '../utils/api';

const STORYBOARD_STYLES = [
    { id: 'oscar_prestige', name: 'Oscar-Level Prestige', category: 'Prestige Cinema', desc: 'Lubezki natural light. Deakins master control.' },
    { id: 'classic_pencil', name: 'Classic Pencil & Charcoal', category: 'Traditional', desc: 'Loose gestural pencil work, cross-hatching.' },
    { id: 'film_noir', name: 'Film Noir Expressionist', category: 'Classic Cinema', desc: 'High contrast B&W. Venetian blind shadows.' },
    { id: 'comic_book', name: 'Comic Book Ink', category: 'Graphic Novel', desc: 'Bold ink lines, Ben-Day dots, Marvel energy.' },
    { id: 'anime_cinematic', name: 'Anime Cinematic', category: 'Animation', desc: 'Miyazaki warmth meets Kon psychological depth.' },
    { id: 'european_graphic_novel', name: 'European Graphic Novel', category: 'Graphic Novel', desc: 'Moebius ligne claire. Metal Hurlant aesthetic.' },
    { id: 'pixar_previs', name: 'Pixar / DreamWorks Pre-vis', category: 'Animation', desc: 'Warm CG lighting, appeal-driven staging.' },
    { id: 'concept_art_digital', name: 'Concept Art / Syd Mead', category: 'Concept Art', desc: 'Industrial realism. Atmospheric perspective.' },
    { id: 'painted_realism', name: 'Golden Age Painted Realism', category: 'Classic Art', desc: 'Norman Rockwell. N.C. Wyeth. Oil painting.' },
    { id: 'neo_noir_neon', name: 'Neo-Noir / Cyberpunk Neon', category: 'Modern Cinema', desc: 'Blade Runner wet streets. Villeneuve darkness.' },
    { id: 'wes_anderson', name: 'Wes Anderson Symmetry', category: 'Modern Cinema', desc: 'Perfect symmetry. Pastel palette. Deadpan.' },
    { id: 'dogme_naturalist', name: 'Dogme / Naturalist', category: 'Independent Film', desc: 'Handheld urgency. Available light only.' },
    { id: 'expressionist_horror', name: 'Expressionist Horror', category: 'Classic Cinema', desc: 'Nosferatu angles. Shadow as monster.' },
    { id: 'golden_age_hollywood', name: 'Golden Age Hollywood', category: 'Classic Cinema', desc: '1940s studio glamour. Technicolor dreams.' },
    { id: 'manga_kinetic', name: 'Manga / Kinetic Ink', category: 'Animation', desc: 'Speed lines. Impact frames. Otomo precision.' },
    { id: 'wong_kar_wai', name: 'Wong Kar-wai Impressionist', category: 'Independent Film', desc: 'Motion blur poetry. Christopher Doyle lens.' },
];

interface ConfigurationProps {
    onSave: (config: any) => void;
}

export const Configuration: React.FC<ConfigurationProps> = ({ onSave }) => {
    const [apiKey, setApiKey] = useState('');
    const [hasSavedApiKey, setHasSavedApiKey] = useState(false);
    const [balanceInfo, setBalanceInfo] = useState<any>(null);
    const [isBalanceLoading, setIsBalanceLoading] = useState(false);
    const [baseUrl, setBaseUrl] = useState('http://localhost:11434');
    const [provider, setProvider] = useState<'openai' | 'local' | 'anthropic' | 'google' | 'openrouter' | 'groq'>('openai');
    const [models, setModels] = useState<any[]>([]);
    const [selectedModel, setSelectedModel] = useState('');
    const [storyboardStyle, setStoryboardStyle] = useState('oscar_prestige');
    const [testStatus, setTestStatus] = useState<'idle' | 'testing' | 'success' | 'error'>('idle');
    const [testMessage, setTestMessage] = useState('');
    const [lastDuration, setLastDuration] = useState('');
    const [activityLog, setActivityLog] = useState<{ time: string, msg: string, type: 'info' | 'error' }[]>([]);
    const [networkLogs, setNetworkLogs] = useState<{ time: string, method: string, url: string, status?: number, error?: string, duration?: string }[]>([]);
    const [showDiagnostics, setShowDiagnostics] = useState(false);
    const [systemInfo, setSystemInfo] = useState<any>(null);

    const addLog = (msg: string, type: 'info' | 'error' = 'info') => {
        const time = new Date().toLocaleTimeString();
        setActivityLog(prev => [{ time, msg, type }, ...prev].slice(0, 50));
    };

    const addNetworkLog = (log: any) => {
        const time = new Date().toLocaleTimeString();
        setNetworkLogs(prev => [{ time, ...log }, ...prev].slice(0, 20));
    };

    const configLoadedRef = React.useRef(false);

    useEffect(() => {
        fetchConfig().then(() => {
            configLoadedRef.current = true;
        });
    }, []);

    useEffect(() => {
        // Skip redundant fetches during the initial config load
        if (!configLoadedRef.current) return;

        // Only fetch if we have an API key or if it's local
        if (provider === 'local' || (apiKey && apiKey.length > 5)) {
            fetchModels(provider, apiKey, baseUrl);
        } else {
            if (['openai', 'anthropic', 'google', 'groq'].includes(provider)) {
                fetchModels(provider, '', baseUrl);
            } else {
                setModels([]);
            }
        }
    }, [provider, baseUrl]);

    const fetchModels = async (
        currentProvider?: string,
        currentApiKey?: string,
        currentBaseUrl?: string,
        preferredModel?: string
    ): Promise<string> => {
        const p = currentProvider || provider;
        addLog(`Fetching models for ${p}...`);
        try {
            const targetModel = (preferredModel || selectedModel || '').trim();
            const config = {
                type: p,
                api_key: currentApiKey || apiKey,
                base_url: currentBaseUrl || baseUrl,
                model_name: ''
            };

            const startTime = Date.now();
            const resp = await fetch(`${API_BASE}/providers/models`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(config)
            });

            const duration = (Date.now() - startTime) / 1000;
            addNetworkLog({ method: 'POST', url: '/providers/models', status: resp.status, duration: `${duration.toFixed(2)}s` });

            if (resp.ok) {
                const data = await resp.json();
                setModels(data);
                addLog(`Discovered ${data.length} models for ${p}`);
                if (data.length > 0) {
                    const exists = data.find((m: any) => m.id === targetModel);
                    const resolvedModel = exists ? targetModel : data[0].id;
                    setSelectedModel(resolvedModel);
                    return resolvedModel;
                }
                return targetModel;
            } else {
                addLog(`Model discovery failed for ${p}`, 'error');
                return targetModel;
            }
        } catch (e: any) {
            addNetworkLog({ method: 'POST', url: '/providers/models', error: e.message });
            addLog(`Model discovery error: ${e.message}`, 'error');
            console.error('Failed to fetch models', e);
            return (preferredModel || selectedModel || '').trim();
        }
    };

    const fetchConfig = async () => {
        try {
            addLog(`Loading persistent configuration...`);
            const resp = await fetch(`${API_BASE}/providers/config`);
            if (resp.ok) {
                const data = await resp.json();
                if (data) {
                    const type = data.type as any;
                    setProvider(type);
                    setApiKey('');
                    setHasSavedApiKey(Boolean(data.has_api_key));
                    setStoryboardStyle(data.storyboard_style || 'oscar_prestige');

                    const defaults: Record<string, string> = {
                        openai: 'https://api.openai.com/v1',
                        anthropic: 'https://api.anthropic.com',
                        openrouter: 'https://openrouter.ai/api/v1',
                        groq: 'https://api.groq.com',
                        local: 'http://localhost:11434',
                        google: ''
                    };
                    setBaseUrl(data.base_url || defaults[type] || '');
                    const savedModel = (data.model_name || '').trim();
                    setSelectedModel(savedModel);
                    addLog(`Config loaded: ${data.type}`);
                    // Fetch models for the saved config and keep/pick a valid model.
                    const resolvedModel = await fetchModels(data.type, '', data.base_url, savedModel);
                    onSave({ ...data, model_name: resolvedModel || savedModel });
                }
            }
        } catch (e) {
            addLog(`Failed to load config: ${e}`, 'error');
            console.error('Failed to fetch config', e);
        }
    };

    const handleTestConnection = async () => {
        setTestStatus('testing');
        const p = provider;
        addLog(`Testing ${p} connection...`);
        try {
            const resolvedModel = await fetchModels(p, apiKey, baseUrl, selectedModel);
            const config = {
                id: p,
                name: p.charAt(0).toUpperCase() + p.slice(1),
                type: p,
                api_key: apiKey.trim(),
                base_url: baseUrl,
                model_name: resolvedModel || selectedModel,
                storyboard_style: storyboardStyle,
            };

            const startTime = Date.now();
            const resp = await fetch(`${API_BASE}/providers/test`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(config)
            });

            const networkDuration = (Date.now() - startTime) / 1000;
            addNetworkLog({ method: 'POST', url: '/providers/test', status: resp.status, duration: `${networkDuration.toFixed(2)}s` });

            const data = await resp.json();
            if (data.status === 'success') {
                setTestStatus('success');
                setLastDuration(data.duration || '');
                addLog(`Connection successful (${data.duration})`);
                setHasSavedApiKey(Boolean(apiKey.trim()) || hasSavedApiKey);
                onSave(config);
            } else {
                setTestStatus('error');
                setTestMessage(data.message);
                setLastDuration(data.duration || '');
                addLog(`Connection failed: ${data.message} (${data.duration})`, 'error');
            }
        } catch (e: any) {
            addNetworkLog({ method: 'POST', url: '/providers/test', error: e.message });
            setTestStatus('error');
            setTestMessage(e.message === 'Failed to fetch'
                ? 'Backend Unreachable. Ensure the Storyboard Server is running on port 8000.'
                : e.message
            );
            addLog(`Test error: ${e.message}`, 'error');
        }
    };

    const handleSaveConfig = async () => {
        const p = provider;
        addLog(`Saving ${p} configuration...`);
        try {
            // Resolve provider model list first so we persist a valid model selection.
            const resolvedModel = await fetchModels(p, apiKey, baseUrl, selectedModel);
            const config = {
                id: p,
                name: p.charAt(0).toUpperCase() + p.slice(1),
                type: p,
                api_key: apiKey.trim(),
                base_url: baseUrl,
                model_name: resolvedModel || selectedModel,
                storyboard_style: storyboardStyle,
            };

            const startTime = Date.now();
            const resp = await fetch(`${API_BASE}/providers/save`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(config)
            });

            const networkDuration = (Date.now() - startTime) / 1000;
            addNetworkLog({ method: 'POST', url: '/providers/save', status: resp.status, duration: `${networkDuration.toFixed(2)}s` });

            if (resp.ok) {
                addLog(`Configuration saved for ${p}`);
                setHasSavedApiKey(Boolean(apiKey.trim()) || hasSavedApiKey);
                onSave(config);
                // Refresh once more after save to capture any provider-side changes.
                await fetchModels(p, apiKey, baseUrl, config.model_name);
            } else {
                addLog(`Failed to save configuration`, 'error');
            }
        } catch (e: any) {
            addNetworkLog({ method: 'POST', url: '/providers/save', error: e.message });
            addLog(`Save error: ${e.message}`, 'error');
        }
    };

    const handleCheckBalance = async () => {
        setIsBalanceLoading(true);
        try {
            const config = {
                type: provider,
                api_key: apiKey.trim(),
                base_url: baseUrl,
                model_name: selectedModel,
                storyboard_style: storyboardStyle,
            };
            const resp = await fetch(`${API_BASE}/providers/balance`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(config)
            });
            const data = await resp.json();
            setBalanceInfo(data);
            addNetworkLog({ method: 'POST', url: '/providers/balance', status: resp.status, duration: '0s' });
        } catch (e: any) {
            console.error(e);
            setBalanceInfo({ status: 'error', message: e.message });
        } finally {
            setIsBalanceLoading(false);
        }
    };

    const copyDebugInfo = () => {
        const info = {
            timestamp: new Date().toISOString(),
            provider,
            baseUrl,
            testStatus,
            lastDuration,
            activityLog,
            networkLogs,
            userAgent: navigator.userAgent
        };
        navigator.clipboard.writeText(JSON.stringify(info, null, 2));
        addLog('Debug info copied to clipboard!');
    };

    return (
        <div className="max-w-4xl mx-auto space-y-8">
            <div className="flex items-center gap-3">
                <div className="p-3 bg-indigo-500/10 rounded-2xl">
                    <Settings className="w-8 h-8 text-indigo-500" />
                </div>
                <div>
                    <h3 className="text-3xl font-black tracking-tight">AI Provider Management</h3>
                    <p className="text-slate-400">Configure your LLM and Image Generation engines</p>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                <div className="md:col-span-2 space-y-6">
                    <div className="glass-morphism rounded-3xl p-8 border border-white/5 space-y-8">
                        <div className="space-y-4">
                            <label className="text-sm font-bold text-slate-500 uppercase tracking-widest flex items-center gap-2">
                                <Globe className="w-4 h-4" />
                                Select Provider
                            </label>
                            <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
                                {[
                                    { id: 'openai', name: 'OpenAI', desc: 'GPT & DALL-E' },
                                    { id: 'anthropic', name: 'Anthropic', desc: 'Claude 3.5' },
                                    { id: 'google', name: 'Google', desc: 'Gemini & Banana' },
                                    { id: 'openrouter', name: 'OpenRouter', desc: 'Any Model' },
                                    { id: 'groq', name: 'Groq', desc: 'Free & Fast' },
                                    { id: 'local', name: 'Local', desc: 'Ollama' },
                                ].map((p) => (
                                    <div key={p.id} className="has-tooltip">
                                        <span className="tooltip">{p.desc}</span>
                                        <button
                                            onClick={() => {
                                                setProvider(p.id as any);
                                                setModels([]);
                                                setSelectedModel('');
                                                setBalanceInfo(null);
                                                setApiKey('');
                                                setHasSavedApiKey(false);
                                                const defaults: Record<string, string> = {
                                                    openai: 'https://api.openai.com/v1',
                                                    anthropic: 'https://api.anthropic.com',
                                                    openrouter: 'https://openrouter.ai/api/v1',
                                                    groq: 'https://api.groq.com',
                                                    local: 'http://localhost:11434',
                                                    google: ''
                                                };
                                                if (defaults[p.id]) setBaseUrl(defaults[p.id]);
                                                addLog(`Switched provider to ${p.id}`);
                                            }}
                                            className={`w-full p-4 rounded-2xl border transition-all text-left space-y-1 ${provider === p.id
                                                ? 'bg-indigo-500/10 border-indigo-500/50 ring-1 ring-indigo-500/50'
                                                : 'bg-slate-900/50 border-white/5 hover:border-white/10'
                                                }`}
                                        >
                                            <div className="font-bold text-sm">{p.name}</div>
                                            <div className="text-[10px] text-slate-500 uppercase tracking-tighter">{p.desc}</div>
                                        </button>
                                    </div>
                                ))}
                            </div>
                        </div>

                        <div className="space-y-6 animate-in fade-in slide-in-from-top-2">
                            {provider !== 'local' && (
                                <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                                    <div className="space-y-4">
                                        <label className="text-sm font-bold text-slate-500 uppercase tracking-widest flex items-center gap-2">
                                            <Key className="w-4 h-4" />
                                            {provider === 'google' ? 'Google API Key' : provider.charAt(0).toUpperCase() + provider.slice(1) + ' Key'}
                                        </label>
                                        <input
                                            type="password"
                                            value={apiKey}
                                            onChange={(e) => setApiKey(e.target.value)}
                                            placeholder={hasSavedApiKey ? 'Using saved key (enter to replace)...' : 'sk-...'}
                                            className="w-full bg-slate-950 border border-white/5 rounded-2xl px-6 py-4 outline-none focus:border-indigo-500/50 focus:ring-1 focus:ring-indigo-500/50 transition-all font-mono text-white"
                                        />
                                        {hasSavedApiKey && !apiKey.trim() && (
                                            <p className="text-[10px] text-slate-500 italic">
                                                A key is already saved for this provider. Leave blank to keep it.
                                            </p>
                                        )}
                                    </div>
                                    <div className="space-y-4">
                                        <label className="text-sm font-bold text-slate-500 uppercase tracking-widest flex items-center gap-2">
                                            <Globe className="w-4 h-4" />
                                            API Endpoint Override
                                        </label>
                                        <input
                                            type="text"
                                            value={baseUrl}
                                            onChange={(e) => setBaseUrl(e.target.value)}
                                            placeholder={
                                                provider === 'openai' ? 'https://api.openai.com/v1' :
                                                    provider === 'anthropic' ? 'https://api.anthropic.com' :
                                                        provider === 'openrouter' ? 'https://openrouter.ai/api/v1' :
                                                            provider === 'groq' ? 'https://api.groq.com' :
                                                                'Enter endpoint URL...'
                                            }
                                            className="w-full bg-slate-950 border border-white/5 rounded-2xl px-6 py-4 outline-none focus:border-indigo-500/50 transition-all font-mono text-white"
                                        />
                                    </div>
                                </div>
                            )}

                            {provider === 'openrouter' && (
                                <div className="p-4 rounded-2xl bg-indigo-500/5 border border-indigo-500/10 text-xs text-indigo-300 leading-relaxed italic">
                                    Note: You can use free models like `meta-llama/llama-3.1-8b-instruct:free` on OpenRouter.
                                </div>
                            )}

                            {provider === 'local' && (
                                <div className="space-y-4">
                                    <label className="text-sm font-bold text-slate-500 uppercase tracking-widest flex items-center gap-2">
                                        <Database className="w-4 h-4" />
                                        Ollama Base URL
                                    </label>
                                    <input
                                        type="text"
                                        value={baseUrl}
                                        onChange={(e) => setBaseUrl(e.target.value)}
                                        placeholder="http://localhost:11434"
                                        className="w-full bg-slate-950 border border-white/5 rounded-2xl px-6 py-4 outline-none focus:border-indigo-500/50 transition-all font-mono text-white"
                                    />
                                </div>
                            )}

                            <div className="space-y-4">
                                <label className="text-sm font-bold text-slate-500 uppercase tracking-widest flex items-center gap-2">
                                    <Activity className="w-4 h-4" />
                                    Active Model & Target Endpoint
                                </label>
                                <div className="space-y-2">
                                    <div className="relative">
                                        {models.length > 0 ? (
                                            <select
                                                value={selectedModel}
                                                onChange={(e) => setSelectedModel(e.target.value)}
                                                className="w-full bg-slate-950 border border-white/5 rounded-2xl px-6 py-4 outline-none focus:border-indigo-500/50 transition-all appearance-none text-white cursor-pointer pr-12"
                                            >
                                                {models.map((m) => (
                                                    <option key={m.id} value={m.id} className="bg-slate-900">{m.name || m.id}</option>
                                                ))}
                                            </select>
                                        ) : (
                                            <input
                                                type="text"
                                                value={selectedModel}
                                                onChange={(e) => setSelectedModel(e.target.value)}
                                                placeholder="Enter model name (e.g. gpt-4o)..."
                                                className="w-full bg-slate-950 border border-white/5 rounded-2xl px-6 py-4 outline-none focus:border-indigo-500/50 transition-all font-mono text-white"
                                            />
                                        )}
                                        {models.length > 0 && (
                                            <div className="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none flex items-center gap-2 text-slate-500">
                                                <Globe className="w-4 h-4" />
                                                <ChevronDown className="w-4 h-4" />
                                            </div>
                                        )}
                                    </div>
                                    <div className="flex items-center gap-2 px-4 py-2 bg-slate-900/30 rounded-xl border border-white/5 overflow-hidden">
                                        <div className="w-1.5 h-1.5 rounded-full bg-indigo-500 animate-pulse shrink-0" />
                                        <code className="text-[10px] text-slate-500 truncate font-mono">
                                            {baseUrl || (
                                                provider === 'openai' ? 'https://api.openai.com/v1' :
                                                    provider === 'anthropic' ? 'https://api.anthropic.com' :
                                                        provider === 'openrouter' ? 'https://openrouter.ai/api/v1' :
                                                            provider === 'groq' ? 'https://api.groq.com' :
                                                                provider === 'local' ? 'http://localhost:11434' :
                                                                    'Default Endpoint'
                                            )}
                                        </code>
                                    </div>
                                </div>
                                {provider === 'openrouter' && models.length === 0 && (
                                    <p className="text-[10px] text-slate-500 italic">
                                        Tip: Press "Test & Save" to fetch the latest model list from OpenRouter.
                                    </p>
                                )}
                            </div>
                        </div>

                        {/* ─── Storyboard Art Style Picker ─────────────────────────── */}
                        <div className="space-y-4 border-t border-white/5 pt-6">
                            <label className="text-sm font-bold text-slate-500 uppercase tracking-widest flex items-center gap-2">
                                <Palette className="w-4 h-4" />
                                Storyboard Art Style
                            </label>
                            <p className="text-xs text-slate-600">
                                Defines the visual language for all generated storyboard frames.
                            </p>
                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-h-72 overflow-y-auto pr-1 styled-scrollbar">
                                {STORYBOARD_STYLES.map((style) => (
                                    <button
                                        key={style.id}
                                        onClick={() => setStoryboardStyle(style.id)}
                                        className={`text-left p-3 rounded-xl border transition-all space-y-0.5 ${storyboardStyle === style.id
                                            ? 'bg-indigo-500/10 border-indigo-500/50 ring-1 ring-indigo-500/30'
                                            : 'bg-slate-900/40 border-white/5 hover:border-white/10'
                                            }`}
                                    >
                                        <div className="flex items-center justify-between">
                                            <span className="text-xs font-bold text-white leading-tight">{style.name}</span>
                                            <span className="text-[9px] uppercase tracking-widest text-slate-600 px-1.5 py-0.5 bg-white/5 rounded-md shrink-0 ml-2">
                                                {style.category}
                                            </span>
                                        </div>
                                        <p className="text-[10px] text-slate-500 leading-snug">{style.desc}</p>
                                    </button>
                                ))}
                            </div>
                        </div>

                        <div className="pt-4 flex items-center gap-4">
                            <div className="has-tooltip flex-1">
                                <span className="tooltip">Verifies connection and retrieves model list</span>
                                <button
                                    onClick={handleTestConnection}
                                    disabled={testStatus === 'testing'}
                                    className="w-full py-4 bg-slate-800 rounded-2xl font-bold hover:bg-slate-700 transition-all disabled:opacity-50 flex items-center justify-center gap-2 border border-white/5"
                                >
                                    {testStatus === 'testing' ? (
                                        <>
                                            <Loader2 className="w-5 h-5 animate-spin" />
                                            <span>Testing...</span>
                                        </>
                                    ) : (
                                        <span>Test Connection</span>
                                    )}
                                </button>
                            </div>
                            <div className="has-tooltip flex-1">
                                <span className="tooltip">Persists settings to the database immediately</span>
                                <button
                                    onClick={handleSaveConfig}
                                    className="w-full py-4 bg-indigo-600 rounded-2xl font-bold hover:bg-indigo-700 transition-all flex items-center justify-center gap-2 shadow-lg shadow-indigo-500/20"
                                >
                                    <Save className="w-5 h-5" />
                                    <span>Save Config</span>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>

                <div className="space-y-6">
                    <div className="glass-morphism rounded-3xl p-8 border border-white/5 space-y-6 text-white">
                        <h4 className="font-bold flex items-center gap-2 text-indigo-400">
                            <Activity className="w-5 h-5" />
                            Connection Status
                        </h4>

                        <div className="space-y-4">
                            {testStatus === 'idle' && !lastDuration && (
                                <div className="p-4 rounded-2xl bg-slate-900/50 border border-white/5 text-sm text-slate-500">
                                    Run a connection test to verify your configuration.
                                </div>
                            )}

                            {testStatus === 'testing' && (
                                <div className="p-4 rounded-2xl bg-indigo-500/5 border border-indigo-500/10 text-sm animate-pulse text-indigo-300">
                                    Probing endpoint...
                                </div>
                            )}

                            {testStatus === 'success' && (
                                <div className="p-6 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 space-y-2">
                                    <div className="flex items-center justify-between">
                                        <div className="flex items-center gap-2 text-emerald-500 font-bold">
                                            <CheckCircle2 className="w-5 h-5" />
                                            <span>Connected</span>
                                        </div>
                                        <span className="text-[10px] font-mono bg-emerald-500/20 px-2 py-0.5 rounded text-emerald-400">
                                            {lastDuration}
                                        </span>
                                    </div>
                                    <p className="text-xs text-emerald-500/70">
                                        Host is reachable and API key is valid.
                                    </p>
                                </div>
                            )}

                            {testStatus === 'error' && (
                                <div className="p-6 rounded-2xl bg-rose-500/10 border border-rose-500/20 space-y-2">
                                    <div className="flex items-center justify-between">
                                        <div className="flex items-center gap-2 text-rose-500 font-bold">
                                            <AlertCircle className="w-5 h-5" />
                                            <span>Failed</span>
                                        </div>
                                        <span className="text-[10px] font-mono bg-rose-500/20 px-2 py-0.5 rounded text-rose-400">
                                            {lastDuration}
                                        </span>
                                    </div>
                                    <p className="text-xs text-rose-500/70 break-words">
                                        {testMessage}
                                    </p>
                                </div>
                            )}
                        </div>

                        <div className="pt-4 border-t border-white/5 space-y-4">
                            <div className="flex items-center justify-between">
                                <span className="text-xs font-bold text-slate-500 uppercase tracking-widest">API Activity Log</span>
                                <button
                                    onClick={() => setActivityLog([])}
                                    className="text-[10px] text-slate-600 hover:text-indigo-400 transition-colors uppercase"
                                >
                                    Clear
                                </button>
                            </div>
                            <div className="bg-black/40 rounded-2xl p-4 h-48 overflow-y-auto font-mono text-[10px] space-y-1.5 scrollbar-hide">
                                {activityLog.length === 0 ? (
                                    <div className="text-slate-700 italic">No activity yet...</div>
                                ) : (
                                    activityLog.map((log, i) => (
                                        <div key={i} className={`flex gap-2 ${log.type === 'error' ? 'text-rose-400' : 'text-slate-400'}`}>
                                            <span className="text-slate-600 shrink-0">[{log.time}]</span>
                                            <span className="break-words">{log.msg}</span>
                                        </div>
                                    ))
                                )}
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Provider Balance Info */}
            {provider === 'openrouter' && (
                <div className="glass-morphism rounded-3xl border border-white/5 bg-slate-900/50 p-8 space-y-6 text-white">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <div className="p-3 bg-amber-500/10 rounded-2xl">
                                <Coins className="w-6 h-6 text-amber-500" />
                            </div>
                            <div>
                                <h3 className="text-xl font-bold">Provider Credits</h3>
                                <p className="text-xs text-slate-500">Live balance from your OpenRouter account</p>
                            </div>
                        </div>
                        <button
                            onClick={handleCheckBalance}
                            disabled={isBalanceLoading || (!apiKey.trim() && !hasSavedApiKey)}
                            className="p-3 hover:bg-white/5 rounded-xl transition-all disabled:opacity-20"
                        >
                            <RefreshCw className={`w-5 h-5 text-slate-400 ${isBalanceLoading ? 'animate-spin' : ''}`} />
                        </button>
                    </div>

                    {balanceInfo ? (
                        balanceInfo.status === 'success' ? (
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                <div className="bg-slate-950/50 border border-white/5 rounded-2xl p-4">
                                    <div className="text-[10px] font-black uppercase tracking-widest text-slate-500 mb-1">Total Credits</div>
                                    <div className="text-2xl font-bold text-slate-200">${balanceInfo.credits}</div>
                                </div>
                                <div className="bg-slate-950/50 border border-white/5 rounded-2xl p-4">
                                    <div className="text-[10px] font-black uppercase tracking-widest text-slate-500 mb-1">Usage</div>
                                    <div className="text-2xl font-bold text-rose-500">${balanceInfo.usage}</div>
                                </div>
                                <div className="bg-slate-950/50 border border-amber-500/20 rounded-2xl p-4 bg-amber-500/5">
                                    <div className="text-[10px] font-black uppercase tracking-widest text-amber-500/70 mb-1">Current Balance</div>
                                    <div className="text-2xl font-bold text-amber-500">${balanceInfo.balance}</div>
                                </div>
                            </div>
                        ) : (
                            <div className="p-4 bg-rose-500/10 border border-rose-500/20 rounded-2xl flex items-center gap-3 text-rose-500 text-xs">
                                <AlertCircle className="w-4 h-4" />
                                <span>{balanceInfo.message}</span>
                            </div>
                        )
                    ) : (
                        <div className="py-6 text-center border-2 border-dashed border-white/5 rounded-3xl">
                            <p className="text-xs text-slate-500 mb-2">Click the refresh icon to fetch your account balance</p>
                            <button
                                onClick={handleCheckBalance}
                                disabled={!apiKey.trim() && !hasSavedApiKey}
                                className="text-indigo-500 text-xs font-bold hover:underline disabled:opacity-30"
                            >
                                Check Entitlements
                            </button>
                        </div>
                    )}
                </div>
            )}

            {/* Technical Diagnostics Overlay */}
            <div className="glass-morphism rounded-3xl p-8 border border-white/5 space-y-6">
                <button
                    onClick={() => setShowDiagnostics(!showDiagnostics)}
                    className="w-full flex items-center justify-between group"
                >
                    <div className="flex items-center gap-3">
                        <div className="p-2 bg-rose-500/10 rounded-xl group-hover:bg-rose-500/20 transition-colors">
                            <Bug className="w-5 h-5 text-rose-500" />
                        </div>
                        <div className="text-left">
                            <h4 className="font-bold text-rose-400">Technical Diagnostics</h4>
                            <p className="text-[10px] text-slate-500">Advanced troubleshooting and network logs</p>
                        </div>
                    </div>
                    {showDiagnostics ? <ChevronDown className="w-5 h-5 text-slate-600" /> : <ChevronRight className="w-5 h-5 text-slate-600" />}
                </button>

                {showDiagnostics && (
                    <div className="space-y-6 animate-in fade-in slide-in-from-top-4 duration-300">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div className="space-y-4">
                                <div className="flex items-center justify-between">
                                    <label className="text-[10px] font-bold text-slate-500 uppercase tracking-widest flex items-center gap-2">
                                        <Terminal className="w-3 h-3" />
                                        Network Request Log
                                    </label>
                                    <button
                                        onClick={() => setNetworkLogs([])}
                                        className="text-[9px] text-rose-400/60 hover:text-rose-400 transition-colors"
                                    >
                                        CLEAR
                                    </button>
                                </div>
                                <div className="bg-black/60 rounded-2xl p-4 h-64 overflow-y-auto font-mono text-[9px] border border-white/5 space-y-2">
                                    {networkLogs.length === 0 ? (
                                        <div className="text-slate-700 italic">Listening for network traffic...</div>
                                    ) : (
                                        networkLogs.map((log, i) => (
                                            <div key={i} className={`p-2 rounded border border-white/5 ${log.error ? 'bg-rose-500/5 text-rose-400' : 'bg-slate-900/40 text-slate-400'}`}>
                                                <div className="flex items-center justify-between mb-1">
                                                    <span className="text-slate-600">[{log.time}]</span>
                                                    <span className={`px-1.5 py-0.5 rounded ${log.error ? 'bg-rose-500/20' : 'bg-indigo-500/20 text-indigo-400'}`}>
                                                        {log.method} {log.status || 'ERR'}
                                                    </span>
                                                </div>
                                                <div className="truncate mb-1">{log.url}</div>
                                                {log.error && <div className="text-rose-500 font-bold">Error: {log.error}</div>}
                                                {log.duration && <div className="text-[8px] text-slate-600">RTT: {log.duration}</div>}
                                            </div>
                                        ))
                                    )}
                                </div>
                            </div>

                            <div className="space-y-6">
                                <div className="space-y-4">
                                    <label className="text-[10px] font-bold text-slate-500 uppercase tracking-widest flex items-center gap-2">
                                        <RefreshCw className="w-3 h-3" />
                                        App Configuration State
                                    </label>
                                    <div className="bg-slate-900/40 rounded-2xl p-4 border border-white/5 space-y-3">
                                        <div className="flex justify-between text-[11px]">
                                            <span className="text-slate-500">Backend Endpoint</span>
                                            <span className="text-indigo-400 font-mono">{API_BASE}</span>
                                        </div>
                                        <div className="flex justify-between text-[11px]">
                                            <span className="text-slate-500">Frontend Origin</span>
                                            <span className="text-indigo-400 font-mono">{window.location.origin}</span>
                                        </div>
                                        <div className="flex justify-between text-[11px]">
                                            <span className="text-slate-500">Active Provider</span>
                                            <span className="text-slate-300 font-bold uppercase">{provider}</span>
                                        </div>
                                        <div className="flex justify-between text-[11px]">
                                            <span className="text-slate-500">Models Cached</span>
                                            <span className="text-slate-300">{models.length}</span>
                                        </div>
                                    </div>
                                </div>

                                <div className="space-y-3 pt-2">
                                    <button
                                        onClick={copyDebugInfo}
                                        className="w-full py-3 bg-slate-800 hover:bg-slate-700 rounded-xl text-xs font-bold flex items-center justify-center gap-2 transition-all border border-white/5"
                                    >
                                        <Copy className="w-3.5 h-3.5" />
                                        Copy Debug JSON to Clipboard
                                    </button>
                                    <div className="p-4 rounded-xl bg-indigo-500/5 border border-indigo-500/10 text-[10px] text-indigo-300 leading-relaxed">
                                        <strong>Debug Tip:</strong> If you see "Failed to fetch", open your browser console (F12) to check for deeper CORS or networking details.
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};
