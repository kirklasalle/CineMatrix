import React, { useEffect, useState, useRef } from 'react';
import { Users, Mic, Eye, Film, BookOpen, ChevronDown, ChevronUp, Play, Square, Volume2, Loader2, Sparkles, Check, Edit3, Save } from 'lucide-react';
import { API_BASE } from '../utils/api';

interface Character {
    id: string;
    name: string;
    role: string;
    description: string;
    age_range: string;
    wardrobe: string;
    visual_prompt: string;
    voice_id: string;
    voice_description: string;
    is_lead: boolean;
    scene_count: number;
    line_count: number;
}

interface Archetype {
    id: string;
    name: string;
    narrative_role: string;
    jungian_archetype: string;
    genre_type: string;
    visual_prompt: string;
    voice_id: string;
    voice_description: string;
    visual_style_notes: string;
    wardrobe_signature: string;
    usage_count: number;
}

interface LibraryStats {
    total_archetypes: number;
    by_role: Record<string, number>;
    by_genre_type: Record<string, number>;
    taxonomy: {
        narrative_roles: number;
        jungian_archetypes: number;
        production_tiers: number;
        genre_types: number;
        possible_combinations: number;
    };
    most_used: { name: string; usage: number }[];
}

const VOICE_COLORS: Record<string, string> = {
    alloy: 'bg-slate-500/20 text-slate-300 border-slate-500/30',
    echo: 'bg-blue-500/20 text-blue-300 border-blue-500/30',
    fable: 'bg-amber-500/20 text-amber-300 border-amber-500/30',
    onyx: 'bg-purple-500/20 text-purple-300 border-purple-500/30',
    nova: 'bg-rose-500/20 text-rose-300 border-rose-500/30',
    shimmer: 'bg-cyan-500/20 text-cyan-300 border-cyan-500/30',
};

const VOICE_DESCRIPTIONS: Record<string, string> = {
    alloy: 'Neutral, balanced narrator & protagonist voice',
    echo: 'Crisp, intellectual male lead voice',
    fable: 'Warm, expressive, nuanced dramatic voice',
    onyx: 'Deep, authoritative, gravelly baritone voice',
    nova: 'Warm, dynamic female lead voice',
    shimmer: 'Bright, youthful, energetic female voice',
};

const ROLE_COLORS: Record<string, string> = {
    protagonist: 'text-indigo-400',
    antagonist: 'text-rose-400',
    deuteragonist: 'text-violet-400',
    mentor: 'text-amber-400',
    love_interest: 'text-pink-400',
};

const SAMPLE_LINES = [
    'Every element is used because the story demands it.',
    'Look at me. Tell me what you saw in that alley.',
    'We only get one chance to make this right.',
    'The shadows don’t lie in this city. People do.',
];

interface CharacterLibraryViewProps {
    projectId: string | null;
}

export const CharacterLibraryView: React.FC<CharacterLibraryViewProps> = ({ projectId }) => {
    const [projectChars, setProjectChars] = useState<Character[]>([]);
    const [archetypes, setArchetypes] = useState<Archetype[]>([]);
    const [stats, setStats] = useState<LibraryStats | null>(null);
    const [activeTab, setActiveTab] = useState<'project' | 'library' | 'stats'>('project');
    const [expandedChar, setExpandedChar] = useState<string | null>(null);
    const [loading, setLoading] = useState(true);

    // Audio Playback & Audition State
    const [auditioningKey, setAuditioningKey] = useState<string | null>(null);
    const [playingKey, setPlayingKey] = useState<string | null>(null);
    const [customAuditionText, setCustomAuditionText] = useState<Record<string, string>>({});
    const [savedNotice, setSavedNotice] = useState<string | null>(null);
    const currentAudioRef = useRef<HTMLAudioElement | null>(null);

    useEffect(() => {
        const load = async () => {
            setLoading(true);
            try {
                const [arcResp, statsResp] = await Promise.all([
                    fetch(`${API_BASE}/characters/library?limit=50`),
                    fetch(`${API_BASE}/characters/library/stats`),
                ]);
                if (arcResp.ok) setArchetypes(await arcResp.json());
                if (statsResp.ok) setStats(await statsResp.json());

                if (projectId) {
                    const cResp = await fetch(`${API_BASE}/projects/${projectId}/characters`);
                    if (cResp.ok) setProjectChars(await cResp.json());
                }
            } catch (e) {
                console.error(e);
            } finally {
                setLoading(false);
            }
        };
        load();
    }, [projectId]);

    const stopAudio = () => {
        if (currentAudioRef.current) {
            currentAudioRef.current.pause();
            currentAudioRef.current.currentTime = 0;
            currentAudioRef.current = null;
        }
        setPlayingKey(null);
    };

    const handleAudition = async (key: string, voiceId: string, charName: string, customText?: string) => {
        if (playingKey === key) {
            stopAudio();
            return;
        }

        stopAudio();
        setAuditioningKey(key);

        const textToSpeak = customText || customAuditionText[key] || `${charName || 'Character'}: Every element is used because the story demands it.`;

        try {
            const resp = await fetch(`${API_BASE}/characters/audition`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    voice_id: voiceId,
                    character_name: charName,
                    text: textToSpeak,
                }),
            });

            const data = await resp.json();
            if (data.status === 'success' && data.audio_base64) {
                const audioUrl = `data:audio/mp3;base64,${data.audio_base64}`;
                const audio = new Audio(audioUrl);
                currentAudioRef.current = audio;
                setPlayingKey(key);

                audio.onended = () => {
                    setPlayingKey(null);
                    currentAudioRef.current = null;
                };
                audio.onerror = () => {
                    setPlayingKey(null);
                    currentAudioRef.current = null;
                };

                await audio.play();
            } else {
                alert(data.message || 'Voice audition failed. Please ensure an OpenAI API key is configured in Configuration.');
            }
        } catch (err: any) {
            console.error('Audition error', err);
            alert(`Voice audition failed: ${err.message}`);
        } finally {
            setAuditioningKey(null);
        }
    };

    const handleUpdateVoice = async (charId: string, newVoiceId: string) => {
        if (!projectId) return;

        // Optimistic UI update
        setProjectChars(prev => prev.map(c => c.id === charId ? { ...c, voice_id: newVoiceId } : c));

        try {
            const resp = await fetch(`${API_BASE}/projects/${projectId}/characters/${charId}`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ voice_id: newVoiceId }),
            });
            if (resp.ok) {
                setSavedNotice(`Voice updated to ${newVoiceId}`);
                setTimeout(() => setSavedNotice(null), 3000);
            }
        } catch (e) {
            console.error('Failed to update character voice', e);
        }
    };

    const VoiceBadge = ({ voiceId }: { voiceId: string }) => (
        <span className={`text-[9px] font-bold uppercase tracking-widest px-2.5 py-0.5 rounded-full border ${VOICE_COLORS[voiceId] || VOICE_COLORS.alloy}`}>
            {voiceId}
        </span>
    );

    const renderProjectChars = () => (
        <div className="space-y-4">
            {!projectId && (
                <div className="text-center py-16 text-slate-600">
                    <Users className="w-12 h-12 mx-auto mb-4 opacity-30" />
                    <p className="font-medium">Create and analyze a project to see its character profiles.</p>
                </div>
            )}
            {projectId && projectChars.length === 0 && !loading && (
                <div className="text-center py-16 text-slate-600">
                    <Users className="w-12 h-12 mx-auto mb-4 opacity-30" />
                    <p className="font-medium">No characters extracted yet.</p>
                    <p className="text-sm mt-1">Run analysis on a script to populate character profiles.</p>
                </div>
            )}

            {savedNotice && (
                <div className="p-3 bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 text-xs rounded-xl flex items-center gap-2">
                    <Check className="w-4 h-4 text-emerald-400" />
                    <span>{savedNotice}</span>
                </div>
            )}

            {projectChars.map(c => {
                const isPlaying = playingKey === c.id;
                const isAuditioning = auditioningKey === c.id;

                return (
                    <div key={c.id} className="glass-morphism rounded-2xl border border-white/5 overflow-hidden transition-all">
                        <div className="p-5 flex items-center justify-between hover:bg-white/2 transition-colors">
                            <div
                                className="flex items-center gap-4 flex-1 cursor-pointer"
                                onClick={() => setExpandedChar(expandedChar === c.id ? null : c.id)}
                            >
                                <div className="w-10 h-10 rounded-xl bg-indigo-500/10 flex items-center justify-center">
                                    <span className="text-indigo-400 font-black text-sm">{c.name[0]}</span>
                                </div>
                                <div>
                                    <div className="flex items-center gap-2">
                                        <span className="font-bold text-white text-base">{c.name}</span>
                                        {c.is_lead && (
                                            <span className="text-[9px] font-black uppercase tracking-widest px-1.5 py-0.5 rounded bg-indigo-500/20 text-indigo-400">LEAD</span>
                                        )}
                                        <VoiceBadge voiceId={c.voice_id || 'alloy'} />
                                    </div>
                                    <div className="flex items-center gap-3 mt-0.5">
                                        <span className={`text-[10px] font-bold uppercase tracking-wider ${ROLE_COLORS[c.role] || 'text-slate-500'}`}>
                                            {c.role?.replace('_', ' ')}
                                        </span>
                                        {c.age_range && <span className="text-[10px] text-slate-500">{c.age_range}</span>}
                                        <span className="text-[10px] text-slate-500">{c.scene_count} scene{c.scene_count !== 1 ? 's' : ''}</span>
                                    </div>
                                </div>
                            </div>

                            {/* Audio Audition Quick Action */}
                            <div className="flex items-center gap-3">
                                <button
                                    onClick={() => handleAudition(c.id, c.voice_id || 'alloy', c.name)}
                                    disabled={isAuditioning}
                                    title="Audition voice sample"
                                    className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 border ${isPlaying
                                        ? 'bg-rose-500/20 text-rose-300 border-rose-500/30 shadow-lg shadow-rose-500/20'
                                        : 'bg-indigo-600/20 hover:bg-indigo-600/30 text-indigo-300 border-indigo-500/20'
                                        }`}
                                >
                                    {isAuditioning ? (
                                        <Loader2 className="w-3.5 h-3.5 animate-spin" />
                                    ) : isPlaying ? (
                                        <Square className="w-3.5 h-3.5 fill-current" />
                                    ) : (
                                        <Play className="w-3.5 h-3.5 fill-current" />
                                    )}
                                    <span>{isPlaying ? 'Stop' : 'Audition'}</span>
                                </button>

                                <button
                                    onClick={() => setExpandedChar(expandedChar === c.id ? null : c.id)}
                                    className="p-2 text-slate-500 hover:text-white"
                                >
                                    {expandedChar === c.id ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                                </button>
                            </div>
                        </div>

                        {expandedChar === c.id && (
                            <div className="px-5 pb-5 space-y-4 border-t border-white/5 pt-4 animate-in slide-in-from-top-2 duration-200">
                                {/* Visual Profile */}
                                {c.description && (
                                    <div>
                                        <p className="text-[9px] font-bold uppercase tracking-widest text-slate-500 mb-1 flex items-center gap-1.5">
                                            <Eye className="w-3 h-3 text-indigo-400" /> Visual Profile
                                        </p>
                                        <p className="text-xs text-slate-300 leading-relaxed">{c.description}</p>
                                    </div>
                                )}

                                {/* Wardrobe */}
                                {c.wardrobe && (
                                    <div>
                                        <p className="text-[9px] font-bold uppercase tracking-widest text-slate-500 mb-1">Wardrobe Signature</p>
                                        <p className="text-xs text-slate-400">{c.wardrobe}</p>
                                    </div>
                                )}

                                {/* Visual Consistency Prompt */}
                                {c.visual_prompt && (
                                    <div>
                                        <p className="text-[9px] font-bold uppercase tracking-widest text-slate-500 mb-1 flex items-center gap-1.5">
                                            <Film className="w-3 h-3 text-indigo-400" /> Injected Image Consistency Prompt
                                        </p>
                                        <p className="text-[10px] text-indigo-300 font-mono bg-indigo-500/5 border border-indigo-500/10 rounded-lg px-3 py-2">
                                            {c.visual_prompt}
                                        </p>
                                    </div>
                                )}

                                {/* Voice Casting & Interactive Audition Suite */}
                                <div className="p-4 bg-slate-900/60 rounded-xl border border-white/5 space-y-3">
                                    <div className="flex items-center justify-between">
                                        <p className="text-[9px] font-bold uppercase tracking-widest text-violet-400 flex items-center gap-1.5">
                                            <Mic className="w-3 h-3" /> Voice Casting &amp; Table Read Reassignment
                                        </p>
                                        <span className="text-[9px] text-slate-500">OpenAI TTS-1 Engine</span>
                                    </div>

                                    {/* Voice Selector Pills */}
                                    <div className="flex flex-wrap gap-2">
                                        {(['alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer'] as const).map(v => (
                                            <button
                                                key={v}
                                                onClick={() => handleUpdateVoice(c.id, v)}
                                                className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all border flex items-center gap-1.5 ${c.voice_id === v
                                                    ? 'bg-indigo-600 text-white border-indigo-500 shadow-md shadow-indigo-500/30'
                                                    : 'bg-slate-800 text-slate-400 border-white/5 hover:border-white/20'
                                                    }`}
                                            >
                                                <span>{v}</span>
                                                {c.voice_id === v && <Check className="w-3 h-3" />}
                                            </button>
                                        ))}
                                    </div>
                                    <p className="text-[10px] text-slate-400 italic">
                                        {VOICE_DESCRIPTIONS[c.voice_id || 'alloy']}
                                    </p>

                                    {/* Custom Line Audition Input */}
                                    <div className="pt-2 border-t border-white/5 flex gap-2">
                                        <input
                                            type="text"
                                            value={customAuditionText[c.id] || ''}
                                            onChange={(e) => setCustomAuditionText({ ...customAuditionText, [c.id]: e.target.value })}
                                            placeholder={`Test dialogue for ${c.name}...`}
                                            className="flex-1 bg-slate-950/60 border border-white/10 rounded-xl px-3 py-2 text-xs text-white placeholder-slate-600 focus:outline-none focus:border-indigo-500"
                                        />
                                        <button
                                            onClick={() => handleAudition(c.id, c.voice_id || 'alloy', c.name, customAuditionText[c.id])}
                                            disabled={isAuditioning}
                                            className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-bold transition-all flex items-center gap-1.5"
                                        >
                                            {isAuditioning ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Volume2 className="w-3.5 h-3.5" />}
                                            <span>Audition Line</span>
                                        </button>
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>
                );
            })}
        </div>
    );

    const renderLibrary = () => (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {archetypes.map(a => {
                const isPlaying = playingKey === a.id;
                const isAuditioning = auditioningKey === a.id;

                return (
                    <div key={a.id} className="glass-morphism rounded-2xl border border-white/5 p-5 space-y-3 flex flex-col justify-between">
                        <div className="space-y-2">
                            <div className="flex items-start justify-between gap-2">
                                <div>
                                    <p className="font-bold text-sm text-white">{a.name}</p>
                                    <div className="flex items-center gap-2 mt-1 flex-wrap">
                                        <span className={`text-[9px] font-bold uppercase tracking-widest ${ROLE_COLORS[a.narrative_role] || 'text-slate-500'}`}>
                                            {a.narrative_role?.replace('_', ' ')}
                                        </span>
                                        {a.genre_type && (
                                            <span className="text-[9px] text-slate-500 uppercase tracking-wider">
                                                {a.genre_type?.replace('_', ' ')}
                                            </span>
                                        )}
                                        <VoiceBadge voiceId={a.voice_id || 'alloy'} />
                                    </div>
                                </div>
                                {a.usage_count > 0 && (
                                    <span className="text-[9px] text-slate-600 shrink-0">×{a.usage_count}</span>
                                )}
                            </div>

                            {a.visual_prompt && (
                                <p className="text-[10px] text-slate-400 leading-relaxed italic">"{a.visual_prompt}"</p>
                            )}
                            {a.wardrobe_signature && (
                                <p className="text-[9px] text-slate-500">{a.wardrobe_signature}</p>
                            )}
                        </div>

                        {/* Quick Listen Button */}
                        <div className="pt-2 border-t border-white/5 flex items-center justify-between">
                            <span className="text-[9px] text-slate-500">{VOICE_DESCRIPTIONS[a.voice_id || 'alloy']?.split(',')[0]}</span>
                            <button
                                onClick={() => handleAudition(a.id, a.voice_id || 'alloy', a.name)}
                                disabled={isAuditioning}
                                className={`px-2.5 py-1 rounded-lg text-[10px] font-bold transition-all flex items-center gap-1 border ${isPlaying
                                    ? 'bg-rose-500/20 text-rose-300 border-rose-500/30'
                                    : 'bg-white/5 hover:bg-white/10 text-slate-300 border-white/10'
                                    }`}
                            >
                                {isAuditioning ? <Loader2 className="w-3 h-3 animate-spin" /> : isPlaying ? <Square className="w-3 h-3 fill-current" /> : <Play className="w-3 h-3 fill-current" />}
                                <span>{isPlaying ? 'Stop' : 'Listen Voice'}</span>
                            </button>
                        </div>
                    </div>
                );
            })}
        </div>
    );

    const renderStats = () => (
        <div className="space-y-6">
            {stats && (
                <>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        {[
                            { label: 'Total Archetypes', value: stats.total_archetypes },
                            { label: 'Narrative Roles', value: stats.taxonomy?.narrative_roles },
                            { label: 'Jungian Types', value: stats.taxonomy?.jungian_archetypes },
                            { label: 'Type Combinations', value: stats.taxonomy?.possible_combinations?.toLocaleString() },
                        ].map(item => (
                            <div key={item.label} className="glass-morphism rounded-2xl border border-white/5 p-5 text-center">
                                <p className="text-2xl font-black text-indigo-400">{item.value}</p>
                                <p className="text-[10px] text-slate-500 uppercase tracking-widest mt-1">{item.label}</p>
                            </div>
                        ))}
                    </div>
                    <div className="glass-morphism rounded-2xl border border-white/5 p-5">
                        <p className="text-[9px] font-bold uppercase tracking-widest text-slate-600 mb-4">Most Used Archetypes</p>
                        <div className="space-y-2">
                            {stats.most_used?.map(m => (
                                <div key={m.name} className="flex items-center justify-between">
                                    <span className="text-xs text-slate-300">{m.name}</span>
                                    <span className="text-xs text-slate-600">×{m.usage}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                </>
            )}
        </div>
    );

    return (
        <div className="max-w-4xl mx-auto space-y-6 animate-in fade-in duration-500">
            <div className="flex items-center gap-3">
                <div className="p-3 bg-indigo-500/10 rounded-2xl border border-indigo-500/20">
                    <Users className="w-8 h-8 text-indigo-400" />
                </div>
                <div>
                    <h3 className="text-3xl font-black tracking-tight text-white">Character Casting &amp; Archetype Library</h3>
                    <p className="text-slate-400 text-sm">Visual consistency profiles, TTS voice auditions, and 14,000+ archetype taxonomy</p>
                </div>
            </div>

            <div className="flex items-center gap-1 bg-slate-900/50 rounded-xl p-1 border border-white/5 w-fit">
                {([['project', 'Project Cast'], ['library', 'Archetype Library'], ['stats', 'Library Taxonomy']] as const).map(([tab, label]) => (
                    <button
                        key={tab}
                        onClick={() => setActiveTab(tab)}
                        className={`px-4 py-2 rounded-lg text-xs font-bold transition-all ${activeTab === tab ? 'bg-indigo-600 text-white shadow-md shadow-indigo-500/30' : 'text-slate-400 hover:text-white'}`}
                    >
                        {label}
                    </button>
                ))}
            </div>

            {loading ? (
                <div className="text-center py-16 text-slate-600 flex items-center justify-center gap-2">
                    <Loader2 className="w-5 h-5 animate-spin text-indigo-500" />
                    <span>Loading character data...</span>
                </div>
            ) : (
                <>
                    {activeTab === 'project' && renderProjectChars()}
                    {activeTab === 'library' && renderLibrary()}
                    {activeTab === 'stats' && renderStats()}
                </>
            )}
        </div>
    );
};
