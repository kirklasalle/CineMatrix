import React, { useEffect, useState } from 'react';
import { Layout, Image as ImageIcon, Wand2, Download, RefreshCw, Loader2, AlertCircle, Activity, CheckCircle2, XCircle, ArrowRight, Sparkles, Info, Zap, Shield, FileSpreadsheet, FileText, Archive, ChevronDown, Video, Play, Square, Film, X, Camera, Maximize2 } from 'lucide-react';
import { PresentationMode } from './PresentationMode';
import { API_BASE } from '../utils/api';

interface Attempt {
    model: string;
    status: 'success' | 'failed';
    reason?: string;
    note?: string;
}

interface ImageGenNotification {
    frameId: string;
    modelUsed: string;
    provider: string;
    attempts: Attempt[];
    visible: boolean;
}

interface ImageModelInfo {
    name: string;
    status: string;
    tier: string;
}

interface ImageStatus {
    ready: boolean;
    provider: string;
    text_model?: string;
    tier: string;
    message: string;
    models_available: ImageModelInfo[];
}

interface StoryboardGalleryProps {
    projectId: string;
    config?: any;
}

export const StoryboardGallery: React.FC<StoryboardGalleryProps> = ({ projectId, config }) => {
    const [frames, setFrames] = useState<any[]>([]);
    const [status, setStatus] = useState<'idle' | 'generating' | 'success' | 'error'>('idle');
    const [error, setError] = useState<string | null>(null);
    const [notification, setNotification] = useState<ImageGenNotification | null>(null);
    const [imageStatus, setImageStatus] = useState<ImageStatus | null>(null);
    const [showModelPanel, setShowModelPanel] = useState(false);
    const [streamProgress, setStreamProgress] = useState<{ current: number; total: number } | null>(null);
    const [streamGenre, setStreamGenre] = useState<string | null>(null);
    const [exportingType, setExportingType] = useState<string | null>(null);
    const [showExportMenu, setShowExportMenu] = useState(false);
    const [isBatchRenderingImages, setIsBatchRenderingImages] = useState(false);
    const [isBatchRenderingAnimatics, setIsBatchRenderingAnimatics] = useState(false);

    // Multimodal Video & Animatic State (Phase 4)
    const [animatingFrameId, setAnimatingFrameId] = useState<string | null>(null);
    const [frameMotionPresets, setFrameMotionPresets] = useState<Record<string, string>>({});
    const [activeVideoModal, setActiveVideoModal] = useState<{
        frameId: string;
        videoUrl: string;
        heading: string;
        shotType: string;
        motionPreset: string;
    } | null>(null);
    const [showPresentation, setShowPresentation] = useState<boolean>(false);
    const [activeLightboxImage, setActiveLightboxImage] = useState<{
        src: string;
        heading?: string;
        desc?: string;
        shot?: string;
    } | null>(null);

    // Fetch image status on mount
    useEffect(() => {
        fetchImageStatus();
    }, []);

    useEffect(() => {
        if (projectId) {
            loadExistingOrGenerate();
        }
    }, [projectId]);

    // Auto-dismiss notification after 12 seconds
    useEffect(() => {
        if (notification?.visible) {
            const timer = setTimeout(() => {
                setNotification(prev => prev ? { ...prev, visible: false } : null);
            }, 12000);
            return () => clearTimeout(timer);
        }
    }, [notification?.visible]);

    const fetchImageStatus = async () => {
        try {
            const resp = await fetch(`${API_BASE}/providers/image-status`);
            if (resp.ok) {
                const data = await resp.json();
                setImageStatus(data);
            }
        } catch (e) {
            // Backend not reachable, but Pollinations.ai is always available
            setImageStatus({
                ready: true,
                provider: 'Pollinations.ai',
                tier: 'free',
                message: 'Backend unreachable. Free Pollinations.ai fallback available.',
                models_available: [{ name: 'Pollinations.ai', status: 'ready', tier: 'free' }]
            });
        }
    };

    const loadExistingOrGenerate = async () => {
        setStatus('generating');
        try {
            const resp = await fetch(`${API_BASE}/projects/${projectId}`);
            if (resp.ok) {
                const data = await resp.json();
                if (data.frames && data.frames.length > 0) {
                    setFrames(data.frames);
                    setStatus('success');
                    fetchImageStatus();
                    return;
                }
            }
        } catch (e) {
            console.warn("Checking existing project frames, fallback to streaming generation", e);
        }
        handleGenerate();
    };

    const handleBatchGenerateImages = async () => {
        setIsBatchRenderingImages(true);
        try {
            const resp = await fetch(`${API_BASE}/projects/${projectId}/generate-all-images`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ force: true })
            });
            if (resp.ok) {
                const data = await resp.json();
                if (data.frames) {
                    setFrames(data.frames);
                }
            }
        } catch (e) {
            console.error("Batch image rendering failed:", e);
        } finally {
            setIsBatchRenderingImages(false);
        }
    };

    const handleBatchGenerateAnimatics = async () => {
        setIsBatchRenderingAnimatics(true);
        try {
            const resp = await fetch(`${API_BASE}/projects/${projectId}/generate-all-animatics`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            if (resp.ok) {
                const data = await resp.json();
                // Reload updated project frames
                const pResp = await fetch(`${API_BASE}/projects/${projectId}`);
                if (pResp.ok) {
                    const pData = await pResp.json();
                    if (pData.frames) setFrames(pData.frames);
                }
                if (data.master_reel_url) {
                    setActiveVideoModal({
                        frameId: 'master_reel',
                        videoUrl: `${API_BASE}${data.master_reel_url}`,
                        heading: 'Master Production Animatic Reel',
                        shotType: 'FULL REEL',
                        motionPreset: '24 FPS Cinematic Sequence'
                    });
                }
            }
        } catch (e) {
            console.error("Batch animatic generation failed:", e);
        } finally {
            setIsBatchRenderingAnimatics(false);
        }
    };

    const handleGenerate = async () => {
        setStatus('generating');
        setError(null);
        setFrames([]);
        setStreamProgress(null);
        setStreamGenre(null);

        try {
            const resp = await fetch(`${API_BASE}/projects/${projectId}/generate-stream`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(config || { type: 'openai', api_key: '' })
            });

            if (!resp.ok || !resp.body) {
                const data = await resp.json().catch(() => ({}));
                setStatus('error');
                setError(data.detail || data.error || 'Generation failed.');
                return;
            }

            const reader = resp.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split('\n');
                buffer = lines.pop() || '';

                for (const line of lines) {
                    if (!line.startsWith('data: ')) continue;
                    try {
                        const event = JSON.parse(line.slice(6));
                        if (event.type === 'start') {
                            setStreamGenre(event.genre || null);
                            setStreamProgress({ current: 0, total: event.total });
                        } else if (event.type === 'frame') {
                            setFrames(prev => [...prev, event.frame]);
                            setStreamProgress(event.progress);
                        } else if (event.type === 'complete') {
                            setStatus('success');
                            setStreamProgress(null);
                            fetchImageStatus();
                        } else if (event.type === 'error') {
                            setStatus('error');
                            setError(event.message || 'Generation error.');
                        }
                    } catch {
                        // malformed event line — skip
                    }
                }
            }

            if (status === 'generating') setStatus('success');
        } catch (e: any) {
            setStatus('error');
            setError(e.message === 'Failed to fetch'
                ? 'Backend server is unreachable. Please ensure the Storyboard backend is running on port 8000.'
                : e.message
            );
        }
    };

    const handleGenerateImage = async (frameId: string) => {
        setFrames(prev => prev.map(f => f.id === frameId ? { ...f, generating: true, imageError: null } : f));
        setNotification(null);
        try {
            const resp = await fetch(`${API_BASE}/frames/${frameId}/generate-image`, {
                method: 'POST'
            });
            const data = await resp.json();
            if (resp.ok) {
                setFrames(prev => prev.map(f => f.id === frameId ? { ...f, image_path: data.image_url, generating: false } : f));

                setNotification({
                    frameId,
                    modelUsed: data.model_used || 'unknown',
                    provider: data.provider || 'unknown',
                    attempts: data.attempts || [],
                    visible: true
                });
            } else {
                setFrames(prev => prev.map(f => f.id === frameId ? { ...f, generating: false, imageError: data.detail || 'Failed' } : f));
            }
        } catch (e) {
            console.error(e);
            setFrames(prev => prev.map(f => f.id === frameId ? { ...f, generating: false, imageError: 'Backend unreachable' } : f));
        }
    };

    const handleDownloadExport = async (endpoint: string, fallbackName: string, typeName: string) => {
        setExportingType(typeName);
        try {
            const resp = await fetch(`${API_BASE}/projects/${projectId}/export/${endpoint}`);
            if (!resp.ok) {
                const err = await resp.json().catch(() => ({}));
                alert(err.detail || `Failed to export ${typeName}`);
                return;
            }
            const blob = await resp.blob();
            const disposition = resp.headers.get('Content-Disposition');
            let filename = fallbackName;
            if (disposition && disposition.includes('filename=')) {
                const match = disposition.match(/filename="?([^"]+)"?/);
                if (match && match[1]) filename = match[1];
            }
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            a.remove();
            window.URL.revokeObjectURL(url);
        } catch (e: any) {
            console.error('Export failed', e);
            alert(`Export failed: ${e.message}`);
        } finally {
            setExportingType(null);
            setShowExportMenu(false);
        }
    };

    const handleGenerateAnimatic = async (frame: any) => {
        const motion = frameMotionPresets[frame.id] || frame.motion_preset || 'dolly_in';
        setAnimatingFrameId(frame.id);
        try {
            const resp = await fetch(`${API_BASE}/frames/${frame.id}/generate-animatic`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ motion_preset: motion, duration: 3.5 })
            });
            if (resp.ok) {
                const data = await resp.json();
                const fullVideoUrl = `${API_BASE}${data.video_url}`;
                setFrames(prev => prev.map(f => f.id === frame.id ? { ...f, video_path: fullVideoUrl, video_status: 'ready', motion_preset: motion } : f));
                setActiveVideoModal({
                    frameId: frame.id,
                    videoUrl: fullVideoUrl,
                    heading: frame.heading,
                    shotType: frame.shot_type || 'CINEMATIC SHOT',
                    motionPreset: motion
                });
            } else {
                const err = await resp.json().catch(() => ({}));
                alert(err.detail || 'Failed to generate animatic video');
            }
        } catch (e: any) {
            console.error('Animatic error', e);
            alert(`Animatic failed: ${e.message}`);
        } finally {
            setAnimatingFrameId(null);
        }
    };

    // ─── Telemetry Bar ──────────────────────────────────────────────
    const renderImageTelemetry = () => {
        if (!imageStatus) return null;

        const guaranteedModel = imageStatus.models_available.find(m => m.status === 'ready');
        const paidModels = imageStatus.models_available.filter(m => m.tier !== 'free');

        return (
            <div className="mb-8 rounded-2xl border border-white/5 bg-slate-900/60 backdrop-blur-lg overflow-hidden">
                {/* Top bar */}
                <div className="flex items-center justify-between px-5 py-3 border-b border-white/5">
                    <div className="flex items-center gap-3">
                        <div className={`w-2.5 h-2.5 rounded-full ${imageStatus.ready ? 'bg-emerald-400 shadow-lg shadow-emerald-500/40 animate-pulse' : 'bg-rose-400'}`} />
                        <span className="text-sm font-bold text-white">
                            Image Generation {imageStatus.ready ? 'Ready' : 'Unavailable'}
                        </span>
                        <span className="text-[10px] font-bold uppercase tracking-widest px-2 py-0.5 rounded-md bg-white/5 text-slate-400">
                            {imageStatus.provider}
                        </span>
                    </div>
                    <button
                        onClick={() => setShowModelPanel(!showModelPanel)}
                        className="text-xs font-bold text-slate-500 hover:text-white transition-colors flex items-center gap-1.5 px-3 py-1.5 rounded-lg hover:bg-white/5"
                    >
                        <Activity className="w-3 h-3" />
                        {showModelPanel ? 'Hide' : 'Show'} Model Chain
                    </button>
                </div>

                {/* Expandable model chain */}
                {showModelPanel && (
                    <div className="px-5 py-4 space-y-3 border-b border-white/5 animate-in slide-in-from-top-2 duration-300">
                        <p className="text-[10px] font-bold uppercase tracking-widest text-slate-600 mb-2">
                            Image Model Priority Chain
                        </p>
                        <div className="flex flex-wrap items-center gap-2">
                            {imageStatus.models_available.map((model, idx) => (
                                <React.Fragment key={idx}>
                                    <div className={`
                                        flex items-center gap-2 px-3 py-2 rounded-xl text-xs font-bold
                                        ${model.status === 'ready'
                                            ? 'bg-emerald-500/10 border border-emerald-500/20 text-emerald-300'
                                            : 'bg-white/5 border border-white/5 text-slate-400'
                                        }
                                    `}>
                                        {model.status === 'ready' ? (
                                            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                                        ) : (
                                            <Zap className="w-3.5 h-3.5 text-slate-500" />
                                        )}
                                        <span>{model.name}</span>
                                        <span className={`
                                            text-[9px] uppercase tracking-wider px-1.5 py-0.5 rounded-md
                                            ${model.tier === 'free' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-indigo-500/20 text-indigo-400'}
                                        `}>
                                            {model.tier}
                                        </span>
                                    </div>
                                    {idx < imageStatus.models_available.length - 1 && (
                                        <ArrowRight className="w-3 h-3 text-slate-700 flex-shrink-0" />
                                    )}
                                </React.Fragment>
                            ))}
                        </div>
                    </div>
                )}

                {/* Status summary */}
                <div className="flex items-center justify-between px-5 py-2.5">
                    <div className="flex items-center gap-3 text-xs text-slate-500">
                        <Shield className="w-3.5 h-3.5 text-emerald-500" />
                        <span>
                            {guaranteedModel
                                ? <><span className="text-emerald-400 font-bold">{guaranteedModel.name}</span> guaranteed fallback</>
                                : 'No guaranteed model'
                            }
                            {paidModels.length > 0 && (
                                <> · {paidModels.length} premium model{paidModels.length > 1 ? 's' : ''} in chain</>
                            )}
                        </span>
                    </div>
                    <span className="text-[10px] font-bold text-emerald-500 flex items-center gap-1">
                        <CheckCircle2 className="w-3 h-3" />
                        IMAGES WILL GENERATE
                    </span>
                </div>
            </div>
        );
    };

    // ─── Notification Toast ─────────────────────────────────────────
    const renderNotification = () => {
        if (!notification || !notification.visible) return null;

        const hasFailures = notification.attempts.some(a => a.status === 'failed');
        const isFallback = notification.modelUsed === 'Pollinations.ai';

        return (
            <div className="fixed bottom-6 right-6 z-50 max-w-md animate-in slide-in-from-bottom-4 fade-in duration-500">
                <div className={`
                    rounded-2xl border backdrop-blur-xl shadow-2xl overflow-hidden
                    ${isFallback
                        ? 'bg-amber-950/90 border-amber-500/30 shadow-amber-500/10'
                        : 'bg-emerald-950/90 border-emerald-500/30 shadow-emerald-500/10'
                    }
                `}>
                    <div className={`px-5 py-3 flex items-center justify-between border-b ${isFallback ? 'border-amber-500/20' : 'border-emerald-500/20'
                        }`}>
                        <div className="flex items-center gap-2.5">
                            {isFallback ? (
                                <div className="w-7 h-7 rounded-full bg-amber-500/20 flex items-center justify-center">
                                    <Info className="w-4 h-4 text-amber-400" />
                                </div>
                            ) : (
                                <div className="w-7 h-7 rounded-full bg-emerald-500/20 flex items-center justify-center">
                                    <Sparkles className="w-4 h-4 text-emerald-400" />
                                </div>
                            )}
                            <span className={`text-sm font-bold ${isFallback ? 'text-amber-200' : 'text-emerald-200'}`}>
                                {isFallback ? 'Model Fallback Active' : 'Image Generated'}
                            </span>
                        </div>
                        <button
                            onClick={() => setNotification(prev => prev ? { ...prev, visible: false } : null)}
                            className="text-slate-500 hover:text-white transition-colors text-xs font-bold px-2 py-1 rounded-lg hover:bg-white/5"
                        >
                            ✕
                        </button>
                    </div>

                    <div className="px-5 py-4 space-y-2.5">
                        <p className="text-[11px] font-bold uppercase tracking-widest text-slate-500 mb-3">
                            Model Resolution Chain
                        </p>
                        {notification.attempts.map((attempt, idx) => (
                            <div key={idx} className="flex items-center gap-3">
                                {attempt.status === 'success' ? (
                                    <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
                                ) : (
                                    <XCircle className="w-4 h-4 text-rose-400 flex-shrink-0" />
                                )}
                                <div className="flex-1 min-w-0">
                                    <span className={`text-sm font-semibold ${attempt.status === 'success' ? 'text-white' : 'text-slate-400 line-through'
                                        }`}>
                                        {attempt.model}
                                    </span>
                                    {attempt.reason && (
                                        <p className="text-[11px] text-rose-400/80 truncate mt-0.5">{attempt.reason}</p>
                                    )}
                                    {attempt.note && (
                                        <p className="text-[11px] text-emerald-400/80 mt-0.5">{attempt.note}</p>
                                    )}
                                </div>
                                {idx < notification.attempts.length - 1 && attempt.status === 'failed' && (
                                    <ArrowRight className="w-3 h-3 text-slate-600 flex-shrink-0" />
                                )}
                            </div>
                        ))}
                    </div>

                    <div className={`px-5 py-3 border-t ${isFallback ? 'border-amber-500/20 bg-amber-950/50' : 'border-emerald-500/20 bg-emerald-950/50'
                        }`}>
                        <p className="text-[11px] text-slate-400">
                            {isFallback ? (
                                <>Rendered via <span className="font-bold text-amber-300">Pollinations.ai</span> — free community generation. Enable a paid image model for higher quality.</>
                            ) : (
                                <>Rendered via <span className="font-bold text-emerald-300">{notification.provider}</span> using <span className="font-bold text-emerald-300">{notification.modelUsed}</span></>
                            )}
                        </p>
                    </div>
                </div>
            </div>
        );
    };

    // ─── Main Render ────────────────────────────────────────────────
    if (showPresentation) return <PresentationMode frames={frames} onClose={() => setShowPresentation(false)} />;

    return (
        <div className="space-y-8 animate-in fade-in duration-700">
            {/* Header */}
            <div className="flex flex-col md:flex-row items-center justify-between gap-6">
                <div>
                    <h2 className="text-4xl font-black tracking-tight">Storyboard Discovery</h2>
                    <p className="text-slate-400">Visual narrative moments identified from your script</p>
                </div>
                <div className="flex flex-wrap items-center gap-3">
                    <button
                        onClick={handleBatchGenerateImages}
                        disabled={status === 'generating' || isBatchRenderingImages || frames.length === 0}
                        className="bg-indigo-600/20 hover:bg-indigo-600/30 text-indigo-300 border border-indigo-500/30 px-4 py-2.5 rounded-2xl text-xs font-bold transition-all flex items-center gap-2 disabled:opacity-40 shadow-sm"
                    >
                        {isBatchRenderingImages ? (
                            <Loader2 className="w-3.5 h-3.5 animate-spin" />
                        ) : (
                            <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
                        )}
                        <span>{isBatchRenderingImages ? 'Rendering All Visuals...' : 'Render All Frames'}</span>
                    </button>

                    <button
                        onClick={handleBatchGenerateAnimatics}
                        disabled={status === 'generating' || isBatchRenderingAnimatics || frames.length === 0}
                        className="bg-purple-600/20 hover:bg-purple-600/30 text-purple-300 border border-purple-500/30 px-4 py-2.5 rounded-2xl text-xs font-bold transition-all flex items-center gap-2 disabled:opacity-40 shadow-sm"
                    >
                        {isBatchRenderingAnimatics ? (
                            <Loader2 className="w-3.5 h-3.5 animate-spin" />
                        ) : (
                            <Film className="w-3.5 h-3.5 text-purple-400" />
                        )}
                        <span>{isBatchRenderingAnimatics ? 'Compiling 24 FPS Reel...' : 'Animate All Frames'}</span>
                    </button>

                    <button
                        onClick={handleGenerate}
                        disabled={status === 'generating'}
                        className="bg-indigo-600 hover:bg-indigo-700 text-white px-5 py-2.5 rounded-2xl text-xs font-bold transition-all flex items-center gap-2 disabled:opacity-50"
                    >
                        {status === 'generating' ? (
                            <Loader2 className="w-4 h-4 animate-spin" />
                        ) : (
                            <RefreshCw className="w-4 h-4" />
                        )}
                        <span>{status === 'generating' ? 'Analyzing...' : 'Regenerate'}</span>
                    </button>

                    <button
                        onClick={() => setShowPresentation(true)}
                        disabled={frames.length === 0}
                        className="px-4 py-2.5 bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 text-white rounded-2xl text-xs font-bold transition-all flex items-center gap-2 shadow-lg shadow-indigo-600/20 disabled:opacity-40"
                    >
                        <Play className="w-3.5 h-3.5 fill-current" />
                        <span>Pitch Mode</span>
                    </button>

                    {/* Master Export Suite Dropdown */}
                    <div className="relative">
                        <button
                            onClick={() => setShowExportMenu(!showExportMenu)}
                            disabled={status === 'generating' || frames.length === 0}
                            className="bg-slate-900 border border-white/10 hover:border-indigo-500/50 text-white px-4 py-2.5 rounded-2xl text-xs font-bold transition-all flex items-center gap-2 disabled:opacity-40 shadow-lg shadow-black/30"
                        >
                            {exportingType ? (
                                <Loader2 className="w-3.5 h-3.5 animate-spin text-indigo-400" />
                            ) : (
                                <Download className="w-3.5 h-3.5 text-indigo-400" />
                            )}
                            <span>{exportingType ? `Exporting ${exportingType}...` : 'Export Master Deck'}</span>
                            <ChevronDown className={`w-3.5 h-3.5 text-slate-400 transition-transform ${showExportMenu ? 'rotate-180' : ''}`} />
                        </button>

                        {showExportMenu && (
                            <div className="absolute right-0 mt-2 w-72 bg-slate-900/95 backdrop-blur-xl border border-white/10 rounded-2xl shadow-2xl z-50 p-2 space-y-1 animate-in fade-in zoom-in-95 duration-200">
                                <button
                                    onClick={() => handleDownloadExport('storyboard.pdf', 'storyboard.pdf', 'PDF Presentation')}
                                    className="w-full px-3 py-2.5 rounded-xl text-left hover:bg-white/5 flex items-center gap-3 transition-colors group"
                                >
                                    <div className="w-8 h-8 rounded-lg bg-indigo-500/10 text-indigo-400 flex items-center justify-center group-hover:bg-indigo-500/20">
                                        <FileText className="w-4 h-4" />
                                    </div>
                                    <div>
                                        <p className="text-xs font-bold text-white">Executive PDF Storyboard</p>
                                        <p className="text-[10px] text-slate-400">16:9 Presentation deck with camera specs</p>
                                    </div>
                                </button>

                                <button
                                    onClick={() => handleDownloadExport('shot-list.csv', 'shot-list.csv', 'Shot List CSV')}
                                    className="w-full px-3 py-2.5 rounded-xl text-left hover:bg-white/5 flex items-center gap-3 transition-colors group"
                                >
                                    <div className="w-8 h-8 rounded-lg bg-emerald-500/10 text-emerald-400 flex items-center justify-center group-hover:bg-emerald-500/20">
                                        <FileSpreadsheet className="w-4 h-4" />
                                    </div>
                                    <div>
                                        <p className="text-xs font-bold text-white">Production Shot List (.CSV)</p>
                                        <p className="text-[10px] text-slate-400">For Directors, DPs, and 1st ADs</p>
                                    </div>
                                </button>

                                <button
                                    onClick={() => handleDownloadExport('images.zip', 'storyboard-images.zip', 'Images ZIP')}
                                    className="w-full px-3 py-2.5 rounded-xl text-left hover:bg-white/5 flex items-center gap-3 transition-colors group"
                                >
                                    <div className="w-8 h-8 rounded-lg bg-amber-500/10 text-amber-400 flex items-center justify-center group-hover:bg-amber-500/20">
                                        <Archive className="w-4 h-4" />
                                    </div>
                                    <div>
                                        <p className="text-xs font-bold text-white">Rendered Frames (.ZIP)</p>
                                        <p className="text-[10px] text-slate-400">Full resolution images + CSV index</p>
                                    </div>
                                </button>

                                <button
                                    onClick={() => handleDownloadExport('script.fountain', 'script.fountain', 'Fountain Script')}
                                    className="w-full px-3 py-2.5 rounded-xl text-left hover:bg-white/5 flex items-center gap-3 transition-colors group"
                                >
                                    <div className="w-8 h-8 rounded-lg bg-rose-500/10 text-rose-400 flex items-center justify-center group-hover:bg-rose-500/20">
                                        <FileText className="w-4 h-4" />
                                    </div>
                                    <div>
                                        <p className="text-xs font-bold text-white">Fountain Screenplay (.fountain)</p>
                                        <p className="text-[10px] text-slate-400">Round-trip to Final Draft &amp; Highland</p>
                                    </div>
                                </button>

                                <button
                                    onClick={() => handleDownloadExport('animatic-reel.mp4', 'animatic-reel.mp4', 'Master Video Reel')}
                                    className="w-full px-3 py-2.5 rounded-xl text-left hover:bg-white/5 flex items-center gap-3 transition-colors group border-t border-white/5 pt-2"
                                >
                                    <div className="w-8 h-8 rounded-lg bg-purple-500/10 text-purple-400 flex items-center justify-center group-hover:bg-purple-500/20">
                                        <Video className="w-4 h-4" />
                                    </div>
                                    <div>
                                        <p className="text-xs font-bold text-white">Master Animatic Reel (.MP4)</p>
                                        <p className="text-[10px] text-slate-400">Stitched cinematic video reel with title cards</p>
                                    </div>
                                </button>
                            </div>
                        )}
                    </div>
                </div>
            </div>

            {/* Image Generation Telemetry Bar */}
            {status === 'success' && renderImageTelemetry()}

            {/* Loading State — with live progress */}
            {status === 'generating' && (
                <div className="py-20 text-center space-y-6">
                    <div className="relative inline-block">
                        <div className="w-24 h-24 rounded-full border-4 border-indigo-500/20 border-t-indigo-500 animate-spin"></div>
                        <Wand2 className="w-8 h-8 text-indigo-500 absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2" />
                    </div>
                    <div className="space-y-3">
                        {streamProgress ? (
                            <>
                                <h3 className="text-xl font-bold">
                                    Analyzing Scene {streamProgress.current} of {streamProgress.total}
                                </h3>
                                {/* Progress bar */}
                                <div className="max-w-xs mx-auto bg-slate-800 rounded-full h-2 overflow-hidden">
                                    <div
                                        className="bg-indigo-500 h-2 rounded-full transition-all duration-500"
                                        style={{ width: `${(streamProgress.current / streamProgress.total) * 100}%` }}
                                    />
                                </div>
                                <p className="text-slate-500 text-xs font-mono">
                                    {Math.round((streamProgress.current / streamProgress.total) * 100)}%
                                    {streamGenre && ` · ${streamGenre.toUpperCase()}`}
                                </p>
                                {frames.length > 0 && (
                                    <p className="text-indigo-400 text-xs font-bold">
                                        {frames.length} frame{frames.length !== 1 ? 's' : ''} ready ↓
                                    </p>
                                )}
                            </>
                        ) : (
                            <>
                                <h3 className="text-xl font-bold">Orchestrating AI Discovery</h3>
                                <p className="text-slate-500 max-w-sm mx-auto">
                                    Detecting genre, loading cinematic knowledge base...
                                </p>
                            </>
                        )}
                    </div>
                </div>
            )}

            {/* Error State */}
            {status === 'error' && (
                <div className="py-20 text-center space-y-6 max-w-2xl mx-auto">
                    <div className={`w-20 h-20 rounded-full ${error?.includes('Credits') ? 'bg-amber-500/20' : 'bg-rose-500/20'} flex items-center justify-center mx-auto animate-bounce`}>
                        <AlertCircle className={`w-10 h-10 ${error?.includes('Credits') ? 'text-amber-500' : 'text-rose-500'}`} />
                    </div>
                    <div className="space-y-3">
                        <h3 className="text-2xl font-black tracking-tight">
                            {error?.includes('Credits') ? 'Account Refill Required' : 'Analysis Interrupted'}
                        </h3>
                        <div className="glass-morphism p-6 rounded-2xl border border-white/5 bg-slate-900/50">
                            <p className="text-slate-300 leading-relaxed font-medium">{error}</p>
                        </div>
                    </div>
                    <button
                        onClick={handleGenerate}
                        className="bg-indigo-600 hover:bg-indigo-700 text-white px-8 py-3 rounded-2xl font-bold transition-all shadow-xl shadow-indigo-500/20"
                    >
                        Retry Analysis
                    </button>
                </div>
            )}

            {/* Frame Cards Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                {frames.map((frame, idx) => (
                    <div
                        key={idx}
                        className="glass-morphism rounded-3xl border border-white/5 hover:border-indigo-500/40 transition-all hover:translate-y-[-2px] flex flex-col relative"
                    >
                        {/* ── Image Area (top) ── */}
                        <div className="aspect-video bg-slate-900 rounded-t-3xl relative flex items-center justify-center overflow-hidden group/img">
                            {frame.image_path ? (
                                <img
                                    src={frame.image_path}
                                    alt={frame.description}
                                    className="w-full h-full object-cover transition-transform duration-500 group-hover/img:scale-105 cursor-pointer"
                                    onClick={() => setActiveLightboxImage({ src: frame.image_path!, heading: frame.heading, desc: frame.description, shot: frame.shot_type })}
                                    onError={(e) => {
                                        const cleanDesc = encodeURIComponent((frame.description || "cinematic scene").slice(0, 100));
                                        (e.currentTarget as HTMLImageElement).src = `https://image.pollinations.ai/prompt/cinematic%20storyboard%20scene%20${frame.scene_number}%20${cleanDesc}?width=1024&height=576&nologo=true&seed=${frame.scene_number * 77 + 9}`;
                                    }}
                                    loading="lazy"
                                />
                            ) : (
                                <>
                                    <div className="absolute inset-0 bg-gradient-to-b from-transparent to-slate-950/80"></div>
                                    <ImageIcon className="w-12 h-12 text-slate-800 group-hover/img:scale-110 transition-transform" />
                                </>
                            )}

                            {frame.generating && (
                                <div className="absolute inset-0 bg-slate-950/70 backdrop-blur-sm flex items-center justify-center z-20">
                                    <div className="flex flex-col items-center gap-3">
                                        <Loader2 className="w-8 h-8 text-indigo-500 animate-spin" />
                                        <span className="text-[10px] font-bold uppercase tracking-widest text-indigo-400">Generating visual...</span>
                                    </div>
                                </div>
                            )}

                            {/* Scene badge */}
                            <div className="absolute top-3.5 left-3.5 z-20">
                                <span className="bg-indigo-600/90 text-white text-[10px] font-black uppercase tracking-widest px-2.5 py-1 rounded-lg backdrop-blur-sm shadow-md">
                                    Scene {frame.scene_number}
                                </span>
                            </div>

                            {/* Intensity badge */}
                            <div className="absolute top-3.5 right-3.5 z-20">
                                <div className="bg-slate-950/80 backdrop-blur-md border border-white/10 text-white text-[10px] font-bold px-2.5 py-1 rounded-lg flex items-center gap-1.5 shadow-md">
                                    <Activity className="w-3 h-3 text-indigo-400" />
                                    <span>{Math.round(frame.intensity_score * 10)}%</span>
                                </div>
                            </div>

                            {/* Click to zoom indicator on image hover only */}
                            {frame.image_path && (
                                <div
                                    onClick={() => setActiveLightboxImage({ src: frame.image_path!, heading: frame.heading, desc: frame.description, shot: frame.shot_type })}
                                    className="absolute inset-0 bg-slate-950/40 opacity-0 group-hover/img:opacity-100 transition-opacity flex items-center justify-center cursor-pointer z-10"
                                >
                                    <div className="bg-slate-900/90 backdrop-blur-md border border-white/20 text-white text-xs font-bold px-3 py-1.5 rounded-xl flex items-center gap-1.5 shadow-xl">
                                        <Maximize2 className="w-3.5 h-3.5 text-indigo-400" />
                                        <span>Click to View Full Size</span>
                                    </div>
                                </div>
                            )}
                        </div>

                        {/* ── Content Area (below image) ── */}
                        <div className="p-5 flex flex-col flex-1 gap-4">
                            {/* Heading & Intensity Type */}
                            <div className="flex items-center justify-between gap-2">
                                <span className={`text-[9px] font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-full ${
                                    frame.intensity_type === 'Action Peak' ? 'bg-orange-500/20 text-orange-400 border border-orange-500/30' :
                                    frame.intensity_type === 'Emotional Peak' ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30' :
                                    'bg-indigo-500/15 text-indigo-300 border border-indigo-500/20'
                                }`}>
                                    {frame.intensity_type || 'Scene'} Moment
                                </span>

                                {frame.heading && (
                                    <span className="text-[10px] font-bold text-slate-400 truncate max-w-[180px]">
                                        {frame.heading}
                                    </span>
                                )}
                            </div>

                            {/* Description */}
                            <p className="text-xs text-slate-300 leading-relaxed line-clamp-3">
                                {frame.description}
                            </p>

                            {/* ── Cinematography Specs Grid (ALWAYS CLEAR & VISIBLE, NEVER COVERED) ── */}
                            <div className="bg-slate-950/60 border border-white/5 rounded-2xl p-3.5 space-y-2.5">
                                <div className="flex items-center justify-between text-[9px] font-black uppercase tracking-widest text-indigo-400 border-b border-white/5 pb-1.5">
                                    <div className="flex items-center gap-1.5">
                                        <Camera className="w-3.5 h-3.5" />
                                        <span>Camera &amp; Lighting Spec</span>
                                    </div>
                                    {frame.lens && (
                                        <span className="text-slate-400 font-mono font-normal">{frame.lens}</span>
                                    )}
                                </div>

                                <div className="grid grid-cols-2 gap-2 text-[11px]">
                                    <div>
                                        <p className="text-[9px] font-bold text-slate-500 uppercase tracking-wider">Shot Type</p>
                                        <p className="font-semibold text-slate-200 truncate">{frame.shot_type || 'Medium Shot'}</p>
                                    </div>
                                    <div>
                                        <p className="text-[9px] font-bold text-slate-500 uppercase tracking-wider">Camera Motion</p>
                                        <p className="font-semibold text-slate-200 truncate">{frame.camera_movement || 'Static'}</p>
                                    </div>
                                    {frame.lighting && (
                                        <div className="col-span-2">
                                            <p className="text-[9px] font-bold text-slate-500 uppercase tracking-wider">Lighting</p>
                                            <p className="font-semibold text-slate-300 truncate">{frame.lighting}</p>
                                        </div>
                                    )}
                                </div>

                                {/* Director's Note */}
                                {frame.moment_summary && (
                                    <div className="pt-2 border-t border-white/5">
                                        <p className="text-[9px] font-bold text-slate-500 uppercase tracking-wider mb-0.5">Director's Note</p>
                                        <p className="text-[10px] text-slate-400 italic leading-relaxed">
                                            &ldquo;{frame.moment_summary}&rdquo;
                                        </p>
                                    </div>
                                )}
                            </div>

                            {/* Error display */}
                            {frame.imageError && (
                                <div className="text-xs text-rose-400 bg-rose-500/10 border border-rose-500/20 rounded-xl px-3 py-2 flex items-center gap-2">
                                    <AlertCircle className="w-3.5 h-3.5 flex-shrink-0" />
                                    <span className="line-clamp-2">{frame.imageError}</span>
                                </div>
                            )}

                            {/* Action Buttons: Visual Gen & Video Animatic */}
                            <div className="space-y-2 mt-auto pt-2">
                                <div className="relative has-tooltip">
                                    <button
                                        onClick={() => handleGenerateImage(frame.id)}
                                        disabled={frame.generating}
                                        className={`
                                            w-full py-2.5 rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-2 disabled:opacity-50
                                            ${frame.image_path
                                                ? 'bg-white/5 hover:bg-white/10 text-slate-300 hover:text-white border border-white/10'
                                                : 'bg-indigo-600 hover:bg-indigo-700 text-white shadow-lg shadow-indigo-600/20'
                                            }
                                        `}
                                    >
                                        {frame.generating ? (
                                            <Loader2 className="w-3.5 h-3.5 animate-spin" />
                                        ) : (
                                            <ImageIcon className="w-3.5 h-3.5" />
                                        )}
                                        <span>{frame.image_path ? 'Regenerate Frame' : 'Generate Frame'}</span>
                                    </button>
                                    <div className="tooltip tooltip-above">
                                        {frame.image_path
                                            ? 'Re-render this visual frame using active AI provider style settings.'
                                            : 'Synthesize high-fidelity AI storyboard image for this scene.'}
                                    </div>
                                </div>

                                {/* Motion Animatic Action Bar */}
                                <div className="flex items-center gap-1.5">
                                    <div className="relative has-tooltip">
                                        <select
                                            value={frameMotionPresets[frame.id] || frame.motion_preset || 'dolly_in'}
                                            onChange={(e) => setFrameMotionPresets({ ...frameMotionPresets, [frame.id]: e.target.value })}
                                            className="bg-slate-950/80 border border-white/10 rounded-xl px-2 py-2 text-[10px] font-bold text-slate-300 focus:outline-none focus:border-indigo-500"
                                        >
                                            <option value="dolly_in">Dolly In (Push)</option>
                                            <option value="dolly_out">Dolly Out (Pull)</option>
                                            <option value="pan_left">Pan Left</option>
                                            <option value="pan_right">Pan Right</option>
                                            <option value="handheld">Handheld Tension</option>
                                            <option value="slow_motion">Slow-Mo Drift</option>
                                        </select>
                                        <div className="tooltip tooltip-above">
                                            Select camera motion preset for animatic generation.
                                        </div>
                                    </div>

                                    <div className="flex-1 relative has-tooltip">
                                        <button
                                            onClick={() => {
                                                if (frame.video_path && !animatingFrameId) {
                                                    setActiveVideoModal({
                                                        frameId: frame.id,
                                                        videoUrl: frame.video_path.startsWith('http') ? frame.video_path : `${API_BASE}${frame.video_path}`,
                                                        heading: frame.heading,
                                                        shotType: frame.shot_type || 'CINEMATIC SHOT',
                                                        motionPreset: frameMotionPresets[frame.id] || frame.motion_preset || 'dolly_in'
                                                    });
                                                } else {
                                                    handleGenerateAnimatic(frame);
                                                }
                                            }}
                                            disabled={animatingFrameId === frame.id}
                                            className={`w-full py-2 rounded-xl text-[10px] font-bold transition-all flex items-center justify-center gap-1.5 border ${frame.video_path
                                                ? 'bg-purple-600/20 hover:bg-purple-600/30 text-purple-300 border-purple-500/30'
                                                : 'bg-indigo-600/20 hover:bg-indigo-600/30 text-indigo-300 border-indigo-500/20'
                                                }`}
                                        >
                                            {animatingFrameId === frame.id ? (
                                                <Loader2 className="w-3 h-3 animate-spin" />
                                            ) : frame.video_path ? (
                                                <Play className="w-3 h-3 fill-current" />
                                            ) : (
                                                <Video className="w-3 h-3" />
                                            )}
                                            <span>{animatingFrameId === frame.id ? 'Synthesizing...' : frame.video_path ? 'Play Animatic' : 'Animate Frame'}</span>
                                        </button>
                                        <div className="tooltip tooltip-above">
                                            {frame.video_path
                                                ? 'Play 24 FPS sub-pixel Ken Burns motion animatic.'
                                                : 'Generate sub-pixel camera motion video clip from this frame.'}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                ))}
            </div>

            {/* Modal Video Player (Phase 4 Animatic Suite) */}
            {activeVideoModal && (
                <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-xl z-50 flex items-center justify-center p-4 animate-in fade-in duration-200">
                    <div className="bg-slate-900 border border-white/10 rounded-3xl max-w-4xl w-full overflow-hidden shadow-2xl space-y-4 p-6 relative">
                        <div className="flex items-center justify-between">
                            <div className="flex items-center gap-2">
                                <div className="p-2 rounded-xl bg-purple-500/10 text-purple-400">
                                    <Video className="w-5 h-5" />
                                </div>
                                <div>
                                    <h3 className="font-bold text-white text-base">{activeVideoModal.heading || 'Cinematic Animatic Motion'}</h3>
                                    <p className="text-xs text-slate-400 uppercase tracking-widest">{activeVideoModal.shotType} &middot; Preset: {activeVideoModal.motionPreset.replace('_', ' ')}</p>
                                </div>
                            </div>
                            <button
                                onClick={() => setActiveVideoModal(null)}
                                className="p-2 text-slate-400 hover:text-white rounded-xl hover:bg-white/5 transition-colors"
                            >
                                <X className="w-5 h-5" />
                            </button>
                        </div>

                        {/* Video Player */}
                        <div className="aspect-video bg-black rounded-2xl overflow-hidden relative shadow-inner">
                            <video
                                src={activeVideoModal.videoUrl}
                                controls
                                autoPlay
                                loop
                                className="w-full h-full object-contain"
                            />
                        </div>

                        <div className="flex items-center justify-between pt-2">
                            <span className="text-[10px] text-slate-500">16:9 Sub-Pixel Camera Interpolation &middot; 24 FPS HD MP4</span>
                            <a
                                href={activeVideoModal.videoUrl}
                                download="scene-animatic.mp4"
                                className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-bold transition-all flex items-center gap-1.5"
                            >
                                <Download className="w-3.5 h-3.5" />
                                <span>Download Video Clip</span>
                            </a>
                        </div>
                    </div>
                </div>
            )}

            {/* Fullscreen Lightbox Image Modal */}
            {activeLightboxImage && (
                <div 
                    onClick={() => setActiveLightboxImage(null)}
                    className="fixed inset-0 bg-slate-950/90 backdrop-blur-2xl z-50 flex items-center justify-center p-4 md:p-8 animate-in fade-in duration-200"
                >
                    <div 
                        onClick={(e) => e.stopPropagation()}
                        className="bg-slate-900 border border-white/15 rounded-3xl max-w-5xl w-full overflow-hidden shadow-2xl flex flex-col space-y-4 p-6 relative"
                    >
                        <div className="flex items-center justify-between">
                            <div>
                                <span className="text-[10px] font-black uppercase tracking-widest text-indigo-400">
                                    {activeLightboxImage.shot || 'Storyboard Frame'}
                                </span>
                                <h3 className="font-bold text-white text-lg">{activeLightboxImage.heading || 'Scene Visual'}</h3>
                            </div>
                            <button
                                onClick={() => setActiveLightboxImage(null)}
                                className="p-2 text-slate-400 hover:text-white rounded-xl hover:bg-white/5 transition-colors"
                            >
                                <X className="w-5 h-5" />
                            </button>
                        </div>

                        <div className="aspect-video bg-black rounded-2xl overflow-hidden relative shadow-inner flex items-center justify-center">
                            <img
                                src={activeLightboxImage.src}
                                alt={activeLightboxImage.desc || 'Frame image'}
                                className="w-full h-full object-contain"
                            />
                        </div>

                        {activeLightboxImage.desc && (
                            <p className="text-xs text-slate-300 leading-relaxed">
                                {activeLightboxImage.desc}
                            </p>
                        )}
                    </div>
                </div>
            )}

            {/* Notification Toast */}
            {renderNotification()}
            {/* Director Presentation Mode Fullscreen Keynote */}
            {showPresentation && (
                <PresentationMode
                    frames={frames}
                    onClose={() => setShowPresentation(false)}
                />
            )}
        </div>
    );
};
