import React, { useEffect, useState, useRef } from 'react';
import { Mic, Play, Square, Volume2, SkipForward, SkipBack, Loader2, Sparkles, Users, Clapperboard, Check } from 'lucide-react';
import { API_BASE } from '../utils/api';

interface Cue {
    character: string;
    type: 'dialogue' | 'action';
    text: string;
    voice_id: string;
    start_time: number;
    end_time: number;
    duration: number;
}

interface SceneReadthrough {
    project_id: string;
    scene_number: number;
    heading: string;
    cues: Cue[];
    total_duration: number;
}

const VOICE_BADGES: Record<string, string> = {
    alloy: 'bg-slate-500/20 text-slate-300 border-slate-500/30',
    echo: 'bg-blue-500/20 text-blue-300 border-blue-500/30',
    fable: 'bg-amber-500/20 text-amber-300 border-amber-500/30',
    onyx: 'bg-purple-500/20 text-purple-300 border-purple-500/30',
    nova: 'bg-rose-500/20 text-rose-300 border-rose-500/30',
    shimmer: 'bg-cyan-500/20 text-cyan-300 border-cyan-500/30',
};

interface TableReadStudioProps {
    projectId: string | null;
}

export const TableReadStudio: React.FC<TableReadStudioProps> = ({ projectId }) => {
    const [sceneNumber, setSceneNumber] = useState<number>(1);
    const [readthrough, setReadthrough] = useState<SceneReadthrough | null>(null);
    const [loading, setLoading] = useState(false);
    const [isPlaying, setIsPlaying] = useState(false);
    const [currentTime, setCurrentTime] = useState(0.0);
    const [activeCueIndex, setActiveCueIndex] = useState<number | null>(null);
    const [auditioningIndex, setAuditioningIndex] = useState<number | null>(null);

    const timerRef = useRef<any>(null);
    const cueRefs = useRef<(HTMLDivElement | null)[]>([]);

    useEffect(() => {
        if (!projectId) return;

        const fetchScene = async () => {
            setLoading(true);
            try {
                const resp = await fetch(`${API_BASE}/projects/${projectId}/readthrough/scene/${sceneNumber}`);
                if (resp.ok) {
                    const data = await resp.json();
                    setReadthrough(data);
                    setCurrentTime(0.0);
                    setActiveCueIndex(0);
                }
            } catch (e) {
                console.error('Table read fetch error', e);
            } finally {
                setLoading(false);
            }
        };

        fetchScene();
    }, [projectId, sceneNumber]);

    // Timer playback loop
    useEffect(() => {
        if (isPlaying && readthrough) {
            timerRef.current = setInterval(() => {
                setCurrentTime(prev => {
                    const nextTime = prev + 0.1;
                    if (nextTime >= readthrough.total_duration) {
                        setIsPlaying(false);
                        return 0.0;
                    }

                    // Determine active cue
                    const idx = readthrough.cues.findIndex(
                        c => nextTime >= c.start_time && nextTime <= c.end_time
                    );
                    if (idx !== -1 && idx !== activeCueIndex) {
                        setActiveCueIndex(idx);
                        cueRefs.current[idx]?.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    }

                    return nextTime;
                });
            }, 100);
        } else {
            if (timerRef.current) clearInterval(timerRef.current);
        }

        return () => {
            if (timerRef.current) clearInterval(timerRef.current);
        };
    }, [isPlaying, readthrough, activeCueIndex]);

    const handlePlayPause = () => {
        setIsPlaying(!isPlaying);
    };

    const handleAuditionLine = async (cue: Cue, idx: number) => {
        setAuditioningIndex(idx);
        try {
            const resp = await fetch(`${API_BASE}/characters/audition`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    voice_id: cue.voice_id || 'alloy',
                    character_name: cue.character,
                    text: cue.text,
                }),
            });

            const data = await resp.json();
            if (data.status === 'success' && data.audio_base64) {
                const audio = new Audio(`data:audio/mp3;base64,${data.audio_base64}`);
                await audio.play();
            }
        } catch (e) {
            console.error('Audition failed', e);
        } finally {
            setAuditioningIndex(null);
        }
    };

    if (!projectId) {
        return (
            <div className="text-center py-24 space-y-4">
                <Mic className="w-16 h-16 text-slate-700 mx-auto" />
                <h3 className="text-xl font-bold text-white">No Project Selected</h3>
                <p className="text-sm text-slate-500 max-w-md mx-auto">
                    Please select a project from the Projects Hub to launch the Virtual Table Read Studio.
                </p>
            </div>
        );
    }

    return (
        <div className="space-y-6 max-w-5xl mx-auto animate-in fade-in duration-500">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-violet-500/20 bg-violet-500/10 text-violet-300 text-xs font-bold uppercase tracking-widest mb-1">
                        <Sparkles className="w-3.5 h-3.5" />
                        <span>Synchronized Multi-Voice Studio</span>
                    </div>
                    <h2 className="text-4xl font-black tracking-tight text-white">Virtual Table Read</h2>
                    <p className="text-slate-400 text-sm">Automated teleprompter reading with OpenAI TTS voice profiles</p>
                </div>

                {/* Scene Selector */}
                <div className="flex items-center gap-2 bg-slate-900/60 border border-white/10 p-1.5 rounded-2xl">
                    <button
                        onClick={() => setSceneNumber(Math.max(1, sceneNumber - 1))}
                        disabled={sceneNumber <= 1}
                        className="p-2 text-slate-400 hover:text-white disabled:opacity-30 rounded-xl hover:bg-white/5"
                    >
                        <SkipBack className="w-4 h-4" />
                    </button>
                    <span className="text-xs font-bold text-white px-2">Scene {sceneNumber}</span>
                    <button
                        onClick={() => setSceneNumber(sceneNumber + 1)}
                        className="p-2 text-slate-400 hover:text-white rounded-xl hover:bg-white/5"
                    >
                        <SkipForward className="w-4 h-4" />
                    </button>
                </div>
            </div>

            {/* Master Playback Console */}
            {readthrough && (
                <div className="glass-morphism rounded-3xl border border-white/10 p-6 bg-slate-900/60 space-y-4 shadow-2xl">
                    <div className="flex items-center justify-between">
                        <div>
                            <span className="text-[10px] font-black uppercase tracking-widest text-violet-400">Scene Teleprompter</span>
                            <h3 className="text-lg font-bold text-white mt-0.5">{readthrough.heading}</h3>
                        </div>

                        {/* Play/Pause Main Button */}
                        <button
                            onClick={handlePlayPause}
                            className={`px-6 py-3 rounded-2xl font-bold text-xs transition-all flex items-center gap-2 shadow-lg ${isPlaying
                                ? 'bg-rose-600 hover:bg-rose-700 text-white shadow-rose-600/30'
                                : 'bg-indigo-600 hover:bg-indigo-700 text-white shadow-indigo-600/30 scale-105'
                                }`}
                        >
                            {isPlaying ? <Square className="w-4 h-4 fill-current" /> : <Play className="w-4 h-4 fill-current" />}
                            <span>{isPlaying ? 'Pause Read' : 'Start Table Read'}</span>
                        </button>
                    </div>

                    {/* Progress Bar & Timeline Scrubber */}
                    <div className="space-y-1.5 pt-2">
                        <div className="w-full bg-slate-950/80 rounded-full h-2 overflow-hidden border border-white/5">
                            <div
                                className="bg-gradient-to-r from-indigo-500 to-violet-500 h-full rounded-full transition-all duration-100"
                                style={{
                                    width: `${readthrough.total_duration > 0 ? (currentTime / readthrough.total_duration) * 100 : 0}%`
                                }}
                            />
                        </div>
                        <div className="flex items-center justify-between text-[10px] font-mono text-slate-500">
                            <span>{currentTime.toFixed(1)}s</span>
                            <span>{readthrough.total_duration.toFixed(1)}s Total</span>
                        </div>
                    </div>
                </div>
            )}

            {/* Teleprompter Cues View */}
            {loading ? (
                <div className="py-24 text-center space-y-3">
                    <Loader2 className="w-8 h-8 text-indigo-500 animate-spin mx-auto" />
                    <p className="text-sm text-slate-400">Loading scene dialogue cues &amp; voice profiles...</p>
                </div>
            ) : readthrough && (
                <div className="glass-morphism rounded-3xl border border-white/5 p-8 bg-slate-900/30 space-y-6 max-h-[550px] overflow-y-auto">
                    {readthrough.cues.map((cue, idx) => {
                        const isActive = activeCueIndex === idx;

                        return (
                            <div
                                key={idx}
                                ref={(el) => (cueRefs.current[idx] = el)}
                                className={`p-5 rounded-2xl transition-all duration-300 flex items-start justify-between gap-4 ${isActive
                                    ? 'bg-indigo-600/20 border border-indigo-500/60 shadow-xl shadow-indigo-500/10 translate-x-2'
                                    : 'bg-slate-950/30 border border-white/5 opacity-70 hover:opacity-100'
                                    }`}
                            >
                                <div className="space-y-2 flex-1">
                                    <div className="flex items-center gap-2">
                                        <span className={`text-xs font-black uppercase tracking-wider ${cue.type === 'dialogue' ? 'text-indigo-300' : 'text-slate-500'}`}>
                                            {cue.character}
                                        </span>
                                        <span className={`text-[9px] font-bold uppercase tracking-widest px-2 py-0.5 rounded-full border ${VOICE_BADGES[cue.voice_id] || VOICE_BADGES.alloy}`}>
                                            {cue.voice_id}
                                        </span>
                                        <span className="text-[10px] font-mono text-slate-600">
                                            {cue.start_time}s - {cue.end_time}s
                                        </span>
                                    </div>

                                    <p className={`text-sm leading-relaxed ${cue.type === 'dialogue' ? 'text-white font-serif' : 'text-slate-400 italic'}`}>
                                        {cue.text}
                                    </p>
                                </div>

                                <button
                                    onClick={() => handleAuditionLine(cue, idx)}
                                    disabled={auditioningIndex === idx}
                                    title="Audition line voice"
                                    className="p-2.5 rounded-xl bg-white/5 hover:bg-white/10 text-slate-300 hover:text-white transition-colors"
                                >
                                    {auditioningIndex === idx ? (
                                        <Loader2 className="w-4 h-4 animate-spin text-indigo-400" />
                                    ) : (
                                        <Volume2 className="w-4 h-4" />
                                    )}
                                </button>
                            </div>
                        );
                    })}
                </div>
            )}
        </div>
    );
};
