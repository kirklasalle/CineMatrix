import React, { useEffect, useState } from 'react';
import { Sparkles, Activity, FileText, Send, Loader2, BookOpen, Layers, CheckCircle2, ArrowRight, Shield, MessageSquare, Award } from 'lucide-react';
import { API_BASE } from '../utils/api';

interface Beat {
    id: string;
    name: string;
    act: string;
    target_pct: number;
    description: string;
    matched_scene_number: number;
    scene_heading: string;
    scene_excerpt: string;
    intensity_score: number;
    intensity_type: string;
    moment_summary: string;
    image_path?: string;
}

interface ArcPoint {
    scene_number: number;
    heading: string;
    progress_pct: number;
    tension_score: number;
    phase: string;
}

interface Coverage {
    title: string;
    scene_count: number;
    estimated_page_count: number;
    lead_characters: string[];
    cast_size: number;
    average_intensity: number;
    pacing_grade: string;
    act_distribution: {
        act_1: number;
        act_2a: number;
        act_2b: number;
        act_3: number;
    };
    strengths: string[];
    recommendations: string[];
}

interface StoryDoctorViewProps {
    projectId: string | null;
}

export const StoryDoctorView: React.FC<StoryDoctorViewProps> = ({ projectId }) => {
    const [beats, setBeats] = useState<Beat[]>([]);
    const [arc, setArc] = useState<ArcPoint[]>([]);
    const [coverage, setCoverage] = useState<Coverage | null>(null);
    const [loading, setLoading] = useState(true);
    const [selectedBeat, setSelectedBeat] = useState<Beat | null>(null);

    // Chat state
    const [chatMessages, setChatMessages] = useState<{ role: 'user' | 'assistant'; text: string }[]>([
        { role: 'assistant', text: "I'm your Oscar-grade Script Doctor. Ask me to punch up dialogue, evaluate character arcs, or pitch third-act twists." }
    ]);
    const [inputMessage, setInputMessage] = useState('');
    const [sendingChat, setSendingChat] = useState(false);

    useEffect(() => {
        if (!projectId) {
            setLoading(false);
            return;
        }

        const loadAnalysis = async () => {
            setLoading(true);
            try {
                const [beatResp, arcResp, covResp] = await Promise.all([
                    fetch(`${API_BASE}/projects/${projectId}/analysis/beat-sheet`),
                    fetch(`${API_BASE}/projects/${projectId}/analysis/narrative-arc`),
                    fetch(`${API_BASE}/projects/${projectId}/analysis/coverage`),
                ]);

                if (beatResp.ok) {
                    const data = await beatResp.json();
                    setBeats(data.beats || []);
                    if (data.beats && data.beats.length > 0) {
                        setSelectedBeat(data.beats[0]);
                    }
                }
                if (arcResp.ok) {
                    const data = await arcResp.json();
                    setArc(data.arc || []);
                }
                if (covResp.ok) {
                    setCoverage(await covResp.json());
                }
            } catch (e) {
                console.error('Story doctor load error', e);
            } finally {
                setLoading(false);
            }
        };

        loadAnalysis();
    }, [projectId]);

    const handleSendMessage = async () => {
        if (!inputMessage.trim() || !projectId) return;

        const userText = inputMessage;
        setChatMessages(prev => [...prev, { role: 'user', text: userText }]);
        setInputMessage('');
        setSendingChat(true);

        try {
            const resp = await fetch(`${API_BASE}/projects/${projectId}/analysis/story-doctor/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: userText }),
            });

            if (resp.ok) {
                const data = await resp.json();
                setChatMessages(prev => [...prev, { role: 'assistant', text: data.reply }]);
            } else {
                setChatMessages(prev => [...prev, { role: 'assistant', text: "Story Doctor engine is analyzing other scenes. Please try again." }]);
            }
        } catch (e: any) {
            setChatMessages(prev => [...prev, { role: 'assistant', text: `Consultation error: ${e.message}` }]);
        } finally {
            setSendingChat(false);
        }
    };

    if (!projectId) {
        return (
            <div className="text-center py-24 space-y-4">
                <BookOpen className="w-16 h-16 text-slate-700 mx-auto" />
                <h3 className="text-xl font-bold text-white">No Project Selected</h3>
                <p className="text-sm text-slate-500 max-w-md mx-auto">
                    Please select a project from the Projects Hub to review its Blake Snyder beat sheet and narrative tension curve.
                </p>
            </div>
        );
    }

    if (loading) {
        return (
            <div className="py-24 text-center space-y-3">
                <Loader2 className="w-8 h-8 text-indigo-500 animate-spin mx-auto" />
                <p className="text-sm text-slate-400">Analyzing screenplay structure &amp; 15-beat milestones...</p>
            </div>
        );
    }

    return (
        <div className="space-y-8 animate-in fade-in duration-500 max-w-7xl mx-auto">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-indigo-500/20 bg-indigo-500/10 text-indigo-300 text-xs font-bold uppercase tracking-widest mb-1">
                        <Sparkles className="w-3.5 h-3.5" />
                        <span>Blake Snyder 15-Beat Structural Intelligence</span>
                    </div>
                    <h2 className="text-4xl font-black tracking-tight text-white">Story Doctor &amp; Beat Sheet</h2>
                    <p className="text-slate-400 text-sm">Pacing analysis, narrative tension graphing, and interactive dramaturgy</p>
                </div>

                {coverage && (
                    <div className="flex items-center gap-3 bg-slate-900/60 border border-white/10 px-4 py-2.5 rounded-2xl">
                        <Award className="w-6 h-6 text-amber-400" />
                        <div>
                            <p className="text-[9px] uppercase tracking-widest font-black text-slate-400">Pacing Grade</p>
                            <p className="text-sm font-black text-white">{coverage.pacing_grade}</p>
                        </div>
                    </div>
                )}
            </div>

            {/* Narrative Tension Graph */}
            {arc.length > 0 && (
                <div className="glass-morphism rounded-3xl border border-white/5 p-6 bg-slate-900/40 space-y-4">
                    <div className="flex items-center justify-between">
                        <div>
                            <h3 className="text-base font-bold text-white flex items-center gap-2">
                                <Activity className="w-4 h-4 text-indigo-400" />
                                Narrative Tension &amp; Intensity Arc
                            </h3>
                            <p className="text-xs text-slate-500">Continuous dramatic volatility across scenes</p>
                        </div>
                        <div className="flex items-center gap-4 text-[10px] font-bold text-slate-400">
                            <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-indigo-500"></span> Act I (0-25%)</span>
                            <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-violet-500"></span> Act IIA (25-50%)</span>
                            <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-amber-500"></span> Act IIB (50-75%)</span>
                            <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-rose-500"></span> Act III (75-100%)</span>
                        </div>
                    </div>

                    {/* SVG Tension Arc Graph */}
                    <div className="h-44 w-full relative pt-2">
                        <svg className="w-full h-full overflow-visible" viewBox={`0 0 ${Math.max(100, arc.length * 50)} 100`} preserveAspectRatio="none">
                            {/* Gridlines */}
                            <line x1="0" y1="20" x2={arc.length * 50} y2="20" stroke="#334155" strokeDasharray="2,4" strokeWidth="0.5" />
                            <line x1="0" y1="50" x2={arc.length * 50} y2="50" stroke="#334155" strokeDasharray="2,4" strokeWidth="0.5" />
                            <line x1="0" y1="80" x2={arc.length * 50} y2="80" stroke="#334155" strokeDasharray="2,4" strokeWidth="0.5" />

                            {/* Curve Line */}
                            <polyline
                                fill="none"
                                stroke="url(#arcGradient)"
                                strokeWidth="3"
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                points={arc.map((p, i) => `${i * 50 + 25},${100 - (p.tension_score * 9)}`).join(' ')}
                            />

                            {/* Points */}
                            {arc.map((p, i) => (
                                <circle
                                    key={i}
                                    cx={i * 50 + 25}
                                    cy={100 - (p.tension_score * 9)}
                                    r="4"
                                    className="fill-indigo-400 stroke-slate-900 stroke-2 hover:r-6 transition-all cursor-pointer"
                                />
                            ))}

                            <defs>
                                <linearGradient id="arcGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                                    <stop offset="0%" stopColor="#6366f1" />
                                    <stop offset="35%" stopColor="#8b5cf6" />
                                    <stop offset="70%" stopColor="#f59e0b" />
                                    <stop offset="100%" stopColor="#f43f5e" />
                                </linearGradient>
                            </defs>
                        </svg>
                    </div>
                </div>
            )}

            {/* Main Content Layout: Beats Grid + Story Doctor Chat */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* 15 Beats List (2 columns wide) */}
                <div className="lg:col-span-2 space-y-4">
                    <h3 className="text-xl font-bold text-white">15 Screenplay Milestones</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                        {beats.map((beat) => (
                            <div
                                key={beat.id}
                                onClick={() => setSelectedBeat(beat)}
                                className={`p-4 rounded-2xl border transition-all cursor-pointer flex flex-col justify-between ${selectedBeat?.id === beat.id
                                    ? 'bg-indigo-600/15 border-indigo-500/60 shadow-lg shadow-indigo-500/10'
                                    : 'bg-slate-900/40 border-white/5 hover:border-white/20'
                                    }`}
                            >
                                <div className="space-y-1.5">
                                    <div className="flex items-center justify-between">
                                        <span className="text-[9px] font-black uppercase tracking-widest text-indigo-400">
                                            {beat.act} &middot; {beat.target_pct}%
                                        </span>
                                        <span className="text-[10px] font-mono px-2 py-0.5 rounded-md bg-white/5 text-slate-300">
                                            Scene {beat.matched_scene_number}
                                        </span>
                                    </div>
                                    <h4 className="font-bold text-white text-sm">{beat.name}</h4>
                                    <p className="text-xs text-slate-400 line-clamp-2">{beat.description}</p>
                                </div>

                                <div className="pt-2 mt-2 border-t border-white/5 flex items-center justify-between text-[10px] text-slate-500">
                                    <span className="truncate max-w-[160px]">{beat.scene_heading}</span>
                                    <span className="font-bold text-indigo-400">{Math.round(beat.intensity_score * 10)}% Int</span>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Story Doctor Interactive Chat Panel */}
                <div className="space-y-4 flex flex-col h-full">
                    <h3 className="text-xl font-bold text-white flex items-center gap-2">
                        <MessageSquare className="w-5 h-5 text-indigo-400" />
                        Story Doctor Studio
                    </h3>

                    <div className="glass-morphism rounded-3xl border border-white/10 bg-slate-900/50 flex-1 flex flex-col overflow-hidden min-h-[500px]">
                        {/* Selected Beat Snapshot */}
                        {selectedBeat && (
                            <div className="p-4 bg-slate-950/60 border-b border-white/5 space-y-1">
                                <div className="flex items-center justify-between">
                                    <span className="text-[9px] font-black uppercase tracking-widest text-indigo-400">Active Beat Focus</span>
                                    <span className="text-[9px] text-slate-500">Scene {selectedBeat.matched_scene_number}</span>
                                </div>
                                <p className="text-xs font-bold text-white">{selectedBeat.name}</p>
                                <p className="text-[11px] text-slate-400 italic line-clamp-1">{selectedBeat.scene_heading}</p>
                            </div>
                        )}

                        {/* Chat Message List */}
                        <div className="flex-1 p-4 space-y-3 overflow-y-auto max-h-[380px]">
                            {chatMessages.map((msg, idx) => (
                                <div
                                    key={idx}
                                    className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}
                                >
                                    <div
                                        className={`max-w-[85%] rounded-2xl p-3 text-xs leading-relaxed ${msg.role === 'user'
                                            ? 'bg-indigo-600 text-white font-medium rounded-br-none'
                                            : 'bg-slate-800 text-slate-200 rounded-bl-none border border-white/5'
                                            }`}
                                    >
                                        {msg.text}
                                    </div>
                                    <span className="text-[9px] text-slate-600 mt-1 px-1">
                                        {msg.role === 'user' ? 'Writer' : 'Oscar Story Doctor'}
                                    </span>
                                </div>
                            ))}
                            {sendingChat && (
                                <div className="flex items-center gap-2 text-xs text-indigo-400 bg-indigo-500/10 p-2.5 rounded-xl border border-indigo-500/20 w-fit">
                                    <Loader2 className="w-3.5 h-3.5 animate-spin" />
                                    <span>Script Doctor consulting dramatic principles...</span>
                                </div>
                            )}
                        </div>

                        {/* Chat Input Bar */}
                        <div className="p-3 border-t border-white/5 bg-slate-950/60 flex gap-2">
                            <input
                                type="text"
                                value={inputMessage}
                                onChange={(e) => setInputMessage(e.target.value)}
                                onKeyDown={(e) => e.key === 'Enter' && handleSendMessage()}
                                placeholder="Ask about pacing, dialogue punch-ups, twists..."
                                className="flex-1 bg-slate-900 border border-white/10 rounded-xl px-3 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
                            />
                            <button
                                onClick={handleSendMessage}
                                disabled={sendingChat || !inputMessage.trim()}
                                className="p-2 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-40 text-white rounded-xl transition-all"
                            >
                                <Send className="w-4 h-4" />
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};
