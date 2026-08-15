import React, { useState, useEffect } from 'react';
import { Sparkles, BookOpen, Film, Layers, Play, Eye, FileText, Search, Clock, Cpu, Check, ArrowRight, X, RefreshCw } from 'lucide-react';
import { API_BASE } from '../utils/api';

export interface ExampleScriptMeta {
    id: string;
    category: 'formats' | 'engines' | 'genres' | 'spectrum';
    filename: string;
    title: string;
    format: string;
    genre: string;
    style: string;
    target_engine: string;
    duration: string;
    scene_count: number;
    description: string;
    tags: string[];
}

interface ExampleScriptsHubProps {
    onSelectExample?: (example: ExampleScriptMeta, mode: 'launch' | 'load') => void;
    currentProjectId?: string | null;
    isModal?: boolean;
    onClose?: () => void;
}

export const ExampleScriptsHub: React.FC<ExampleScriptsHubProps> = ({
    onSelectExample,
    currentProjectId,
    isModal = false,
    onClose,
}) => {
    const [examples, setExamples] = useState<ExampleScriptMeta[]>([]);
    const [loading, setLoading] = useState(true);
    const [selectedCategory, setSelectedCategory] = useState<string>('all');
    const [searchQuery, setSearchQuery] = useState('');
    const [previewScript, setPreviewScript] = useState<ExampleScriptMeta | null>(null);
    const [previewContent, setPreviewContent] = useState<string>('');
    const [previewLoading, setPreviewLoading] = useState(false);
    const [launchingId, setLaunchingId] = useState<string | null>(null);

    useEffect(() => {
        fetchExamples();
    }, []);

    const fetchExamples = async () => {
        setLoading(true);
        try {
            const resp = await fetch(`${API_BASE}/examples`);
            if (resp.ok) {
                const data = await resp.json();
                setExamples(data);
            }
        } catch (e) {
            console.error('Failed to fetch example scripts', e);
        } finally {
            setLoading(false);
        }
    };

    const handleOpenPreview = async (example: ExampleScriptMeta, e: React.MouseEvent) => {
        e.stopPropagation();
        setPreviewScript(example);
        setPreviewLoading(true);
        try {
            const resp = await fetch(`${API_BASE}/examples/${example.category}/${example.filename}`);
            if (resp.ok) {
                const data = await resp.json();
                setPreviewContent(data.content || 'No text preview available.');
            } else {
                setPreviewContent('Failed to load script preview.');
            }
        } catch (err) {
            setPreviewContent('Error connecting to backend.');
        } finally {
            setPreviewLoading(false);
        }
    };

    const handleLaunch = async (example: ExampleScriptMeta) => {
        setLaunchingId(example.id);
        try {
            if (currentProjectId) {
                // Load into existing project
                const resp = await fetch(`${API_BASE}/projects/${currentProjectId}/load-example`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ category: example.category, filename: example.filename }),
                });
                if (resp.ok) {
                    if (onSelectExample) onSelectExample(example, 'load');
                }
            } else {
                // 1-Click Create new project with example
                const resp = await fetch(`${API_BASE}/projects/create-with-example`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ category: example.category, filename: example.filename }),
                });
                if (resp.ok) {
                    const data = await resp.json();
                    if (onSelectExample) onSelectExample({ ...example, id: data.project_id }, 'launch');
                }
            }
        } catch (err) {
            console.error('Failed to launch example project', err);
        } finally {
            setLaunchingId(null);
            if (previewScript) setPreviewScript(null);
        }
    };

    const filteredExamples = examples.filter((ex) => {
        const matchesCat = selectedCategory === 'all' || ex.category === selectedCategory;
        const q = searchQuery.toLowerCase();
        const matchesQuery =
            !searchQuery ||
            ex.title.toLowerCase().includes(q) ||
            ex.genre.toLowerCase().includes(q) ||
            ex.format.toLowerCase().includes(q) ||
            ex.target_engine.toLowerCase().includes(q) ||
            ex.description.toLowerCase().includes(q) ||
            ex.tags.some((t) => t.toLowerCase().includes(q));
        return matchesCat && matchesQuery;
    });

    const categoryTabs = [
        { id: 'all', label: 'All Scripts', count: examples.length },
        { id: 'engines', label: 'AI Engines', count: examples.filter((e) => e.category === 'engines').length },
        { id: 'genres', label: 'Cinematic Genres', count: examples.filter((e) => e.category === 'genres').length },
        { id: 'formats', label: 'File Formats', count: examples.filter((e) => e.category === 'formats').length },
        { id: 'spectrum', label: 'Duration Tiers', count: examples.filter((e) => e.category === 'spectrum').length },
    ];

    const getFormatBadgeColor = (fmt: string) => {
        switch (fmt.toLowerCase()) {
            case 'fountain':
                return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20';
            case 'fdx':
                return 'bg-amber-500/10 text-amber-400 border-amber-500/20';
            case 'docx':
                return 'bg-blue-500/10 text-blue-400 border-blue-500/20';
            case 'pdf':
                return 'bg-rose-500/10 text-rose-400 border-rose-500/20';
            case 'cbz':
                return 'bg-purple-500/10 text-purple-400 border-purple-500/20';
            case 'epub':
                return 'bg-cyan-500/10 text-cyan-400 border-cyan-500/20';
            default:
                return 'bg-slate-500/10 text-slate-300 border-slate-500/20';
        }
    };

    return (
        <div className={`space-y-6 ${isModal ? 'p-2' : 'w-full'}`}>
            {/* Header / Intro */}
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-indigo-500/20 bg-indigo-500/10 text-indigo-300 text-xs font-bold uppercase tracking-widest mb-1.5">
                        <BookOpen className="w-3.5 h-3.5" />
                        <span>Interactive Learning &amp; Demo Suite</span>
                    </div>
                    <h2 className="text-2xl md:text-3xl font-black tracking-tight text-white">
                        Sample Scripts Library
                    </h2>
                    <p className="text-xs md:text-sm text-slate-400">
                        {currentProjectId
                            ? 'Select any world-class sample script below to load into this project.'
                            : 'Choose any authentic example script below to jump straight in and learn all features.'}
                    </p>
                </div>

                {isModal && onClose && (
                    <button
                        onClick={onClose}
                        className="p-2 text-slate-400 hover:text-white rounded-xl hover:bg-white/5 transition-colors self-start md:self-auto"
                    >
                        <X className="w-5 h-5" />
                    </button>
                )}
            </div>

            {/* Category Filter Tabs & Search */}
            <div className="flex flex-col md:flex-row items-center justify-between gap-4 border-b border-white/5 pb-4">
                <div className="flex items-center gap-2 overflow-x-auto w-full md:w-auto pb-2 md:pb-0 scrollbar-none">
                    {categoryTabs.map((tab) => (
                        <button
                            key={tab.id}
                            onClick={() => setSelectedCategory(tab.id)}
                            className={`px-3.5 py-2 rounded-xl text-xs font-bold whitespace-nowrap transition-all flex items-center gap-1.5 ${
                                selectedCategory === tab.id
                                    ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/30'
                                    : 'bg-slate-900/60 text-slate-400 hover:text-white hover:bg-slate-800/80 border border-white/5'
                            }`}
                        >
                            <span>{tab.label}</span>
                            <span
                                className={`text-[10px] px-1.5 py-0.2 rounded-full ${
                                    selectedCategory === tab.id
                                        ? 'bg-white/20 text-white'
                                        : 'bg-white/5 text-slate-400'
                                }`}
                            >
                                {tab.count}
                            </span>
                        </button>
                    ))}
                </div>

                {/* Search Bar */}
                <div className="relative w-full md:w-72">
                    <Search className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
                    <input
                        type="text"
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        placeholder="Search 27 sample scripts..."
                        className="w-full bg-slate-900/80 border border-white/10 rounded-xl pl-9 pr-4 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500/50 transition-colors"
                    />
                    {searchQuery && (
                        <button
                            onClick={() => setSearchQuery('')}
                            className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-500 hover:text-white"
                        >
                            <X className="w-3.5 h-3.5" />
                        </button>
                    )}
                </div>
            </div>

            {/* Grid of Example Cards */}
            {loading ? (
                <div className="text-center py-20">
                    <RefreshCw className="w-8 h-8 text-indigo-400 animate-spin mx-auto mb-3" />
                    <p className="text-sm text-slate-400">Loading sample scripts catalog...</p>
                </div>
            ) : filteredExamples.length === 0 ? (
                <div className="text-center py-16 rounded-2xl border border-dashed border-white/10 bg-slate-900/20">
                    <FileText className="w-10 h-10 text-slate-600 mx-auto mb-2" />
                    <p className="text-sm text-slate-400">No sample scripts found matching "{searchQuery}".</p>
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
                    {filteredExamples.map((ex) => (
                        <div
                            key={ex.id}
                            className="glass-morphism rounded-2xl border border-white/5 hover:border-indigo-500/40 bg-slate-900/40 hover:bg-slate-900/70 p-5 flex flex-col justify-between transition-all hover:translate-y-[-2px] group"
                        >
                            <div className="space-y-3">
                                {/* Badges */}
                                <div className="flex items-center justify-between gap-2 flex-wrap">
                                    <div className="flex items-center gap-1.5">
                                        <span
                                            className={`text-[9px] font-black uppercase tracking-wider px-2 py-0.5 rounded-md border ${getFormatBadgeColor(
                                                ex.format
                                            )}`}
                                        >
                                            {ex.format.toUpperCase()}
                                        </span>
                                        <span className="text-[9px] font-bold text-slate-400 uppercase tracking-wider px-2 py-0.5 rounded-md bg-white/5 border border-white/5">
                                            {ex.genre}
                                        </span>
                                    </div>

                                    <div className="flex items-center gap-1 text-[10px] text-slate-400 font-mono">
                                        <Clock className="w-3 h-3 text-slate-500" />
                                        <span>{ex.duration}</span>
                                    </div>
                                </div>

                                {/* Title & Engine */}
                                <div>
                                    <h3 className="text-base font-black text-white group-hover:text-indigo-300 transition-colors line-clamp-1">
                                        {ex.title}
                                    </h3>
                                    <div className="flex items-center gap-1.5 text-xs text-indigo-400 font-semibold mt-0.5">
                                        <Cpu className="w-3.5 h-3.5 shrink-0" />
                                        <span className="truncate">{ex.target_engine}</span>
                                    </div>
                                </div>

                                {/* Description */}
                                <p className="text-xs text-slate-400 leading-relaxed line-clamp-2">
                                    {ex.description}
                                </p>

                                {/* Tags */}
                                <div className="flex items-center gap-1 flex-wrap pt-1">
                                    {ex.tags.slice(0, 3).map((tag) => (
                                        <span
                                            key={tag}
                                            className="text-[9px] font-medium text-slate-500 bg-slate-950/60 px-2 py-0.5 rounded-md"
                                        >
                                            #{tag}
                                        </span>
                                    ))}
                                    {ex.scene_count > 0 && (
                                        <span className="text-[9px] font-bold text-amber-400/80 bg-amber-500/10 px-2 py-0.5 rounded-md ml-auto">
                                            {ex.scene_count} {ex.scene_count === 1 ? 'scene' : 'scenes'}
                                        </span>
                                    )}
                                </div>
                            </div>

                            {/* Action Buttons */}
                            <div className="flex items-center gap-2 pt-4 mt-4 border-t border-white/5">
                                <button
                                    onClick={(e) => handleOpenPreview(ex, e)}
                                    title="Read & preview script text"
                                    className="p-2.5 rounded-xl bg-slate-800/80 hover:bg-slate-700 text-slate-300 hover:text-white transition-colors border border-white/5 flex items-center justify-center gap-1 text-xs font-bold"
                                >
                                    <Eye className="w-3.5 h-3.5" />
                                    <span className="hidden sm:inline">Preview</span>
                                </button>

                                <button
                                    onClick={() => handleLaunch(ex)}
                                    disabled={launchingId === ex.id}
                                    className="flex-1 py-2.5 px-3 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-xs transition-all shadow-md shadow-indigo-600/20 flex items-center justify-center gap-1.5 group-hover:scale-[1.01]"
                                >
                                    {launchingId === ex.id ? (
                                        <>
                                            <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                                            <span>Loading...</span>
                                        </>
                                    ) : (
                                        <>
                                            <span>{currentProjectId ? 'Load into Project' : 'Launch Project'}</span>
                                            <ArrowRight className="w-3.5 h-3.5" />
                                        </>
                                    )}
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            )}

            {/* Script Text Preview Modal */}
            {previewScript && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-in fade-in duration-200">
                    <div className="glass-morphism rounded-3xl border border-indigo-500/30 bg-slate-900/95 max-w-3xl w-full max-h-[85vh] flex flex-col shadow-2xl shadow-indigo-950/50">
                        {/* Modal Header */}
                        <div className="p-6 border-b border-white/10 flex items-center justify-between gap-4">
                            <div className="space-y-1">
                                <div className="flex items-center gap-2">
                                    <span
                                        className={`text-[9px] font-black uppercase tracking-wider px-2 py-0.5 rounded-md border ${getFormatBadgeColor(
                                            previewScript.format
                                        )}`}
                                    >
                                        {previewScript.format.toUpperCase()}
                                    </span>
                                    <span className="text-xs text-slate-400 font-bold">{previewScript.genre}</span>
                                </div>
                                <h3 className="text-xl font-black text-white">{previewScript.title}</h3>
                            </div>

                            <button
                                onClick={() => setPreviewScript(null)}
                                className="p-2 text-slate-400 hover:text-white rounded-xl hover:bg-white/5 transition-colors"
                            >
                                <X className="w-5 h-5" />
                            </button>
                        </div>

                        {/* Modal Body: Script Reader */}
                        <div className="p-6 overflow-y-auto flex-1 font-mono text-xs text-slate-300 leading-relaxed bg-slate-950/70 select-text whitespace-pre-wrap">
                            {previewLoading ? (
                                <div className="text-center py-16">
                                    <RefreshCw className="w-6 h-6 text-indigo-400 animate-spin mx-auto mb-2" />
                                    <p className="text-xs text-slate-400">Loading script content...</p>
                                </div>
                            ) : (
                                previewContent
                            )}
                        </div>

                        {/* Modal Footer */}
                        <div className="p-5 border-t border-white/10 flex items-center justify-between gap-4 bg-slate-900/80">
                            <div className="text-xs text-slate-400 flex items-center gap-2">
                                <Cpu className="w-4 h-4 text-indigo-400" />
                                <span>Engine: <strong className="text-slate-200">{previewScript.target_engine}</strong></span>
                            </div>

                            <div className="flex items-center gap-3">
                                <button
                                    onClick={() => setPreviewScript(null)}
                                    className="px-4 py-2.5 rounded-xl border border-white/10 text-slate-300 hover:bg-white/5 text-xs font-bold transition-colors"
                                >
                                    Close
                                </button>

                                <button
                                    onClick={() => handleLaunch(previewScript)}
                                    disabled={launchingId === previewScript.id}
                                    className="px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold transition-all shadow-lg shadow-indigo-600/30 flex items-center gap-2"
                                >
                                    {launchingId === previewScript.id ? (
                                        <>
                                            <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                                            <span>Loading...</span>
                                        </>
                                    ) : (
                                        <>
                                            <span>{currentProjectId ? 'Load into Project' : 'Launch with this Script'}</span>
                                            <ArrowRight className="w-3.5 h-3.5" />
                                        </>
                                    )}
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};
