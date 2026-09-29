import { useState, useEffect } from 'react'
import { Layout, Clapperboard, Settings, Database, Wand2, Plus, Bug, Copy, Users, Film, Trash2, Calendar, FileText, Download, Sparkles, Layers, ArrowRight, BookOpen, Activity, Mic, Power, CheckCircle, RefreshCw, Keyboard } from 'lucide-react'
import { ScriptUploader } from './components/ScriptUploader'
import { Configuration } from './components/Configuration'
import { StoryboardGallery } from './components/StoryboardGallery'
import { CharacterLibraryView } from './components/CharacterLibraryView'
import { StoryDoctorView } from './components/StoryDoctorView'
import { TableReadStudio } from './components/TableReadStudio'
import { GraphicNovelStudio } from './components/GraphicNovelStudio'
import { ExampleScriptsHub, ExampleScriptMeta } from './components/ExampleScriptsHub'
import { ShutdownModal } from './components/ShutdownModal'
import { NleShortcutsModal } from './components/NleShortcutsModal'
import { useNleKeyboardShortcuts, StudioView } from './hooks/useNleKeyboardShortcuts'
import { API_BASE } from './utils/api'

interface SavedProject {
    id: string;
    name: string;
    description: string;
    created_at: string;
    scene_count: number;
    frame_count: number;
    character_count: number;
    script_filename?: string;
    script_format?: string;
}

function App() {
    const [view, setView] = useState<'home' | 'config' | 'upload' | 'gallery' | 'characters' | 'story_doctor' | 'table_read' | 'graphic_novel' | 'examples'>('home');
    const [projectId, setProjectId] = useState<string | null>(null);
    const [config, setConfig] = useState<any>(null);
    const [projects, setProjects] = useState<SavedProject[]>([]);
    const [loadingProjects, setLoadingProjects] = useState(false);
    const [kbStats, setKbStats] = useState<any>(null);

    // Shutdown State
    const [showShutdownModal, setShowShutdownModal] = useState(false);
    const [isShutDown, setIsShutDown] = useState(false);

    // NLE Shortcuts Modal State
    const [showNleShortcutsModal, setShowNleShortcutsModal] = useState(false);

    // Bind NLE Studio Switcher & Playback Hotkeys (1-9, J-K-L, ?, F, Space)
    useNleKeyboardShortcuts({
        currentView: view as StudioView,
        onNavigate: (targetView) => {
            if (['gallery', 'characters', 'story_doctor', 'table_read', 'graphic_novel'].includes(targetView) && !projectId && projects.length > 0) {
                setProjectId(projects[0].id);
            }
            setView(targetView);
        },
        onToggleShortcutsModal: () => setShowNleShortcutsModal(prev => !prev),
    });

    // Fetch active provider config and project list
    useEffect(() => {
        loadConfig();
        loadProjects();
        loadKbStats();
    }, []);

    // Refresh projects whenever navigating home
    useEffect(() => {
        if (view === 'home') {
            loadProjects();
        }
    }, [view]);

    const loadConfig = async () => {
        try {
            const resp = await fetch(`${API_BASE}/providers/config`);
            if (resp.ok) {
                const data = await resp.json();
                if (data) setConfig(data);
            }
        } catch (e) {
            console.error('Failed to load initial config', e);
        }
    };

    const loadProjects = async () => {
        setLoadingProjects(true);
        try {
            const resp = await fetch(`${API_BASE}/projects`);
            if (resp.ok) {
                const data = await resp.json();
                setProjects(Array.isArray(data) ? data : []);
            }
        } catch (e) {
            console.error('Failed to load projects', e);
        } finally {
            setLoadingProjects(false);
        }
    };

    const loadKbStats = async () => {
        try {
            const resp = await fetch(`${API_BASE}/knowledge/stats`);
            if (resp.ok) {
                setKbStats(await resp.json());
            }
        } catch (e) {
            console.error('Failed to load KB stats', e);
        }
    };

    const handleCreateProject = async () => {
        try {
            const resp = await fetch(`${API_BASE}/projects`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name: 'New Storyboard Project', description: 'AI Screenplay Analysis' })
            });
            const data = await resp.json();
            setProjectId(data.id);
            setView('upload');
        } catch (e) {
            console.error(e);
            setProjectId('demo-id-' + Math.random().toString(36).substr(2, 9));
            setView('upload');
        }
    };

    const handleSelectProject = (id: string, targetView: 'gallery' | 'characters' | 'story_doctor' | 'table_read' | 'graphic_novel' = 'gallery') => {
        setProjectId(id);
        setView(targetView);
    };

    const handleDeleteProject = async (id: string, e: React.MouseEvent) => {
        e.stopPropagation();
        if (!window.confirm('Are you sure you want to delete this project and all its storyboard frames?')) {
            return;
        }
        try {
            const resp = await fetch(`${API_BASE}/projects/${id}`, { method: 'DELETE' });
            if (resp.ok) {
                setProjects(prev => prev.filter(p => p.id !== id));
                if (projectId === id) {
                    setProjectId(null);
                }
            }
        } catch (err) {
            console.error('Failed to delete project', err);
        }
    };

    const handleExportDirectPdf = async (id: string, projectName: string, e: React.MouseEvent) => {
        e.stopPropagation();
        try {
            const resp = await fetch(`${API_BASE}/projects/${id}/export/storyboard.pdf`);
            if (!resp.ok) {
                alert('No storyboard frames generated yet for this project.');
                return;
            }
            const blob = await resp.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `storyboard-${projectName.toLowerCase().replace(/\s+/g, '-')}.pdf`;
            document.body.appendChild(a);
            a.click();
            a.remove();
            window.URL.revokeObjectURL(url);
        } catch (err) {
            console.error('Direct PDF export error', err);
        }
    };

    const handleUploadSuccess = (id: string) => {
        setView('gallery');
        loadProjects();
    };

    const handleExampleSelected = (example: ExampleScriptMeta, mode: 'launch' | 'load') => {
        if (mode === 'launch') {
            setProjectId(example.id);
        }
        setView('gallery');
        loadProjects();
    };

    const handleConfigSave = (newConfig: any) => {
        setConfig(newConfig);
    };

    // Global Debug State
    const [showDebugPanel, setShowDebugPanel] = useState(false);
    const [globalErrors, setGlobalErrors] = useState<string[]>([]);

    useEffect(() => {
        const errorHandler = (e: ErrorEvent) => {
            setGlobalErrors(prev => [...prev, `${new Date().toLocaleTimeString()}: ${e.message}`].slice(-20));
        };
        window.addEventListener('error', errorHandler);
        return () => window.removeEventListener('error', errorHandler);
    }, []);

    const copyDebugInfo = () => {
        const info = {
            timestamp: new Date().toISOString(),
            userAgent: navigator.userAgent,
            currentView: view,
            projectId,
            config,
            backendUrl: 'http://127.0.0.1:8000',
            errors: globalErrors,
            localStorage: Object.keys(localStorage)
        };
        navigator.clipboard.writeText(JSON.stringify(info, null, 2));
        alert('Debug info copied to clipboard!');
    };

    // Calculate aggregated stats
    const totalFrames = projects.reduce((acc, p) => acc + (p.frame_count || 0), 0);
    const totalScenes = projects.reduce((acc, p) => acc + (p.scene_count || 0), 0);

    // If server is shut down, render safe exit screen
    if (isShutDown) {
        return (
            <div className="min-h-screen bg-slate-950 text-slate-50 flex items-center justify-center p-6 selection:bg-rose-500/30">
                <div className="glass-morphism rounded-3xl border border-rose-500/30 bg-slate-900/90 max-w-lg w-full p-8 text-center space-y-6 shadow-2xl shadow-rose-950/50 animate-in zoom-in-95 duration-300">
                    <div className="w-20 h-20 rounded-3xl bg-rose-500/10 border border-rose-500/30 flex items-center justify-center text-rose-400 mx-auto shadow-inner">
                        <Power className="w-10 h-10" />
                    </div>

                    <div className="space-y-2">
                        <h1 className="text-3xl font-black text-white">CineMatrix Shut Down</h1>
                        <p className="text-sm text-slate-400 leading-relaxed">
                            The server process and database connections have terminated cleanly.
                        </p>
                    </div>

                    <div className="p-4 rounded-2xl bg-slate-950/70 border border-white/5 text-left text-xs text-slate-400 space-y-2">
                        <div className="flex items-center gap-2 text-emerald-400 font-bold">
                            <CheckCircle className="w-4 h-4 shrink-0" />
                            <span>All your project data &amp; storyboards are safe</span>
                        </div>
                        <p className="text-slate-500 pl-6">
                            To start the application again, double-click <code className="text-indigo-300">start_storyboard.bat</code> in the project directory.
                        </p>
                    </div>

                    <p className="text-xs text-slate-500 font-medium">
                        You can now safely close this browser window.
                    </p>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-slate-950 text-slate-50 flex flex-col selection:bg-indigo-500/30">
            {/* Top Navigation */}
            <header className="border-b border-white/5 bg-slate-900/50 backdrop-blur-xl sticky top-0 z-50">
                <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between gap-4">
                    <button onClick={() => setView('home')} className="flex items-center gap-2.5 hover:opacity-80 transition-opacity shrink-0">
                        <div className="w-9 h-9 rounded-xl bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center">
                            <Clapperboard className="w-5 h-5 text-indigo-400" />
                        </div>
                        <div className="text-left hidden sm:block">
                            <span className="text-lg font-black tracking-tight block leading-tight">CineMatrix</span>
                            <span className="text-[9px] uppercase tracking-widest text-indigo-400 font-bold block">Oscar Prestige</span>
                        </div>
                    </button>

                    <nav className="flex items-center gap-2 md:gap-4 overflow-x-auto scrollbar-none py-1">
                        <button
                            onClick={() => setView('home')}
                            className={`text-xs md:text-sm font-bold transition-colors flex items-center gap-1.5 whitespace-nowrap ${view === 'home' || view === 'gallery' || view === 'upload' ? 'text-white bg-white/5 px-3 py-1.5 rounded-xl border border-white/10' : 'text-slate-400 hover:text-white px-2.5 py-1.5'}`}
                        >
                            <Layers className="w-4 h-4 text-indigo-400" />
                            <span>Projects ({projects.length})</span>
                        </button>

                        <button
                            onClick={() => setView('examples')}
                            className={`text-xs md:text-sm font-bold transition-colors flex items-center gap-1.5 whitespace-nowrap ${view === 'examples' ? 'text-white bg-white/5 px-3 py-1.5 rounded-xl border border-white/10' : 'text-slate-400 hover:text-white px-2.5 py-1.5'}`}
                        >
                            <Sparkles className="w-4 h-4 text-amber-400" />
                            <span>Examples (27)</span>
                        </button>

                        <button
                            onClick={() => setView('characters')}
                            className={`text-xs md:text-sm font-bold transition-colors flex items-center gap-1.5 whitespace-nowrap ${view === 'characters' ? 'text-white bg-white/5 px-3 py-1.5 rounded-xl border border-white/10' : 'text-slate-400 hover:text-white px-2.5 py-1.5'}`}
                        >
                            <Users className="w-4 h-4 text-violet-400" />
                            <span>Cast</span>
                        </button>

                        <button
                            onClick={() => setView('table_read')}
                            className={`text-xs md:text-sm font-bold transition-colors flex items-center gap-1.5 whitespace-nowrap ${view === 'table_read' ? 'text-white bg-white/5 px-3 py-1.5 rounded-xl border border-white/10' : 'text-slate-400 hover:text-white px-2.5 py-1.5'}`}
                        >
                            <Mic className="w-4 h-4 text-cyan-400" />
                            <span>Table Read</span>
                        </button>

                        <button
                            onClick={() => setView('story_doctor')}
                            className={`text-xs md:text-sm font-bold transition-colors flex items-center gap-1.5 whitespace-nowrap ${view === 'story_doctor' ? 'text-white bg-white/5 px-3 py-1.5 rounded-xl border border-white/10' : 'text-slate-400 hover:text-white px-2.5 py-1.5'}`}
                        >
                            <BookOpen className="w-4 h-4 text-amber-400" />
                            <span>Story Doctor</span>
                        </button>

                        <button
                            onClick={() => setView('graphic_novel')}
                            className={`text-xs md:text-sm font-bold transition-colors flex items-center gap-1.5 whitespace-nowrap ${view === 'graphic_novel' ? 'text-white bg-white/5 px-3 py-1.5 rounded-xl border border-white/10' : 'text-slate-400 hover:text-white px-2.5 py-1.5'}`}
                        >
                            <Sparkles className="w-4 h-4 text-rose-400" />
                            <span>Graphic Novel</span>
                        </button>

                        <button
                            onClick={() => setView('config')}
                            className={`text-xs md:text-sm font-bold transition-colors flex items-center gap-1.5 whitespace-nowrap ${view === 'config' ? 'text-white bg-white/5 px-3 py-1.5 rounded-xl border border-white/10' : 'text-slate-400 hover:text-white px-2.5 py-1.5'}`}
                        >
                            <Settings className="w-4 h-4 text-slate-400" />
                            <span>Config</span>
                        </button>
                    </nav>

                    {/* Header Action: NLE Shortcuts Reference */}
                    <button
                        onClick={() => setShowNleShortcutsModal(true)}
                        title="Open NLE Keyboard Shortcuts & Studio Hotkeys (?)"
                        className="flex items-center gap-1.5 text-xs font-bold text-indigo-300 hover:text-white hover:bg-indigo-500/20 px-2.5 py-1.5 rounded-xl border border-indigo-500/20 transition-all shrink-0 ml-1"
                    >
                        <Keyboard className="w-4 h-4 text-indigo-400" />
                        <span className="hidden md:inline">Shortcuts</span>
                        <kbd className="hidden lg:inline px-1.5 py-0.5 rounded bg-indigo-950/70 border border-indigo-500/30 text-[10px] text-indigo-300 font-mono">?</kbd>
                    </button>

                    {/* Header Action: Graceful Shutdown */}
                    <button
                        onClick={() => setShowShutdownModal(true)}
                        title="Shut down Storyboard AI application & backend server"
                        className="flex items-center gap-1.5 text-xs font-bold text-rose-400 hover:text-rose-300 hover:bg-rose-500/10 px-3 py-1.5 rounded-xl border border-rose-500/20 transition-all shrink-0 ml-1"
                    >
                        <Power className="w-4 h-4" />
                        <span className="hidden sm:inline">Shutdown</span>
                    </button>
                </div>
            </header>

            {/* Main Application Container */}
            <main className="flex-1 max-w-7xl mx-auto px-4 py-8 w-full">
                {view === 'home' && (
                    <div className="space-y-10 animate-in fade-in duration-500">
                        {/* Hero Section */}
                        <div className="text-center space-y-4 py-6">
                            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-indigo-500/20 bg-indigo-500/10 text-indigo-300 text-xs font-bold uppercase tracking-widest mb-2">
                                <Sparkles className="w-3.5 h-3.5" />
                                <span>Cinematic Storyboard &amp; Shot Direction</span>
                            </div>
                            <h1 className="text-5xl md:text-6xl font-black tracking-tight bg-gradient-to-b from-white via-slate-100 to-slate-500 bg-clip-text text-transparent">
                                Directed by Intelligence.
                            </h1>
                            <p className="text-slate-400 text-lg max-w-2xl mx-auto leading-relaxed">
                                Transform screenplays and stage plays into high-impact storyboard presentation decks, camera shot lists, and consistent character profiles.
                            </p>
                        </div>

                        {/* Top Telemetry & Stats Counters */}
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                            <div className="glass-morphism rounded-2xl p-4 border border-white/5 bg-slate-900/40">
                                <p className="text-[10px] font-black uppercase tracking-widest text-slate-500">Saved Projects</p>
                                <p className="text-2xl font-black text-white mt-1">{projects.length}</p>
                            </div>
                            <div className="glass-morphism rounded-2xl p-4 border border-white/5 bg-slate-900/40">
                                <p className="text-[10px] font-black uppercase tracking-widest text-indigo-400">Frames Rendered</p>
                                <p className="text-2xl font-black text-indigo-300 mt-1">{totalFrames}</p>
                            </div>
                            <div className="glass-morphism rounded-2xl p-4 border border-white/5 bg-slate-900/40">
                                <p className="text-[10px] font-black uppercase tracking-widest text-amber-400">Total Scenes Parsed</p>
                                <p className="text-2xl font-black text-amber-300 mt-1">{totalScenes}</p>
                            </div>
                            <div className="glass-morphism rounded-2xl p-4 border border-white/5 bg-slate-900/40">
                                <p className="text-[10px] font-black uppercase tracking-widest text-emerald-400">Sample Library</p>
                                <p className="text-2xl font-black text-emerald-300 mt-1">27 Scripts</p>
                            </div>
                        </div>

                        {/* ── Sample Scripts Quick Learning Banner ────────── */}
                        <div className="glass-morphism rounded-3xl p-6 md:p-8 border border-indigo-500/20 bg-gradient-to-r from-indigo-950/40 via-slate-900/60 to-purple-950/40 flex flex-col md:flex-row items-center justify-between gap-6">
                            <div className="space-y-2 text-center md:text-left">
                                <div className="inline-flex items-center gap-1.5 text-xs font-bold text-amber-400 uppercase tracking-widest">
                                    <Sparkles className="w-3.5 h-3.5" />
                                    <span>New User or Need an Example?</span>
                                </div>
                                <h3 className="text-xl md:text-2xl font-black text-white">
                                    Explore the 27 World-Class Sample Scripts
                                </h3>
                                <p className="text-xs md:text-sm text-slate-400 max-w-xl leading-relaxed">
                                    Don't have a screenplay on hand? Choose from our curated catalog across 15-Beat Story Doctor, Table Read casting, 6 Motion Animatics, Graphic Novels, and 9 Cinematic Art Styles.
                                </p>
                            </div>

                            <button
                                onClick={() => setView('examples')}
                                className="px-6 py-3.5 bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-sm rounded-2xl transition-all shadow-xl shadow-indigo-600/30 flex items-center gap-2 whitespace-nowrap group shrink-0"
                            >
                                <span>Browse Sample Library</span>
                                <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                            </button>
                        </div>

                        {/* Projects Grid */}
                        <div className="space-y-6">
                            <div className="flex items-center justify-between">
                                <div>
                                    <h2 className="text-2xl font-black tracking-tight text-white">Project Deck Hub</h2>
                                    <p className="text-xs text-slate-400">Select a project to view storyboard frames, characters, or export presentations</p>
                                </div>

                                <button
                                    onClick={handleCreateProject}
                                    className="bg-indigo-600 hover:bg-indigo-700 text-white px-5 py-2.5 rounded-2xl font-bold transition-all shadow-xl shadow-indigo-500/20 flex items-center gap-2 text-sm"
                                >
                                    <Plus className="w-4 h-4" />
                                    <span>New Storyboard</span>
                                </button>
                            </div>

                            {projects.length === 0 && !loadingProjects ? (
                                <div className="text-center py-20 rounded-3xl border border-dashed border-white/10 bg-slate-900/20 space-y-4">
                                    <Film className="w-12 h-12 text-slate-700 mx-auto" />
                                    <div className="space-y-1">
                                        <h3 className="text-lg font-bold text-white">No Storyboard Projects Yet</h3>
                                        <p className="text-sm text-slate-500 max-w-sm mx-auto">
                                            Upload a screenplay or pick any of our 27 sample scripts to begin immediate multi-modal analysis.
                                        </p>
                                    </div>
                                    <div className="flex items-center justify-center gap-3 pt-2">
                                        <button
                                            onClick={() => setView('examples')}
                                            className="bg-amber-600 hover:bg-amber-700 text-white px-6 py-3 rounded-2xl font-bold transition-all inline-flex items-center gap-2 shadow-lg shadow-amber-600/20"
                                        >
                                            <Sparkles className="w-4 h-4" />
                                            <span>Pick a Sample Script</span>
                                        </button>
                                        <button
                                            onClick={handleCreateProject}
                                            className="bg-slate-800 hover:bg-slate-700 text-slate-200 px-6 py-3 rounded-2xl font-bold transition-all inline-flex items-center gap-2 border border-white/10"
                                        >
                                            <Plus className="w-4 h-4" />
                                            <span>Upload Your Own</span>
                                        </button>
                                    </div>
                                </div>
                            ) : (
                                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                                    {/* Create New Card */}
                                    <div
                                        onClick={handleCreateProject}
                                        className="rounded-3xl border-2 border-dashed border-white/10 hover:border-indigo-500/50 bg-slate-900/20 hover:bg-slate-900/40 p-6 flex flex-col items-center justify-center text-center cursor-pointer transition-all group min-h-[220px]"
                                    >
                                        <div className="w-12 h-12 rounded-2xl bg-indigo-600/10 text-indigo-400 flex items-center justify-center group-hover:scale-110 transition-transform mb-3">
                                            <Plus className="w-6 h-6" />
                                        </div>
                                        <h3 className="text-base font-bold text-white">Start New Project</h3>
                                        <p className="text-xs text-slate-500 mt-1">Upload script or pick from example library</p>
                                    </div>

                                    {/* Existing Projects */}
                                    {projects.map((proj) => (
                                        <div
                                            key={proj.id}
                                            onClick={() => handleSelectProject(proj.id, 'gallery')}
                                            className="glass-morphism rounded-3xl border border-white/5 hover:border-indigo-500/40 bg-slate-900/50 p-6 flex flex-col justify-between cursor-pointer transition-all hover:translate-y-[-2px] group"
                                        >
                                            <div className="space-y-3">
                                                <div className="flex items-start justify-between gap-2">
                                                    <div className="flex items-center gap-2">
                                                        <span className="w-2.5 h-2.5 rounded-full bg-indigo-500"></span>
                                                        <span className="text-[10px] font-black uppercase tracking-widest px-2 py-0.5 rounded-md bg-white/5 text-slate-400">
                                                            {proj.script_format ? proj.script_format.toUpperCase() : 'SCREENPLAY'}
                                                        </span>
                                                    </div>
                                                    <button
                                                        onClick={(e) => handleDeleteProject(proj.id, e)}
                                                        title="Delete Project"
                                                        className="text-slate-600 hover:text-rose-400 p-1.5 rounded-lg hover:bg-rose-500/10 transition-colors"
                                                    >
                                                        <Trash2 className="w-4 h-4" />
                                                    </button>
                                                </div>

                                                <div>
                                                    <h3 className="text-lg font-bold text-white group-hover:text-indigo-300 transition-colors line-clamp-1">
                                                        {proj.name}
                                                    </h3>
                                                    <p className="text-xs text-slate-400 mt-1 line-clamp-2">
                                                        {proj.description || 'AI analyzed screenplay'}
                                                    </p>
                                                </div>

                                                {proj.script_filename && (
                                                    <div className="flex items-center gap-1.5 text-[11px] text-slate-500 font-mono">
                                                        <FileText className="w-3.5 h-3.5 text-slate-600" />
                                                        <span className="truncate">{proj.script_filename}</span>
                                                    </div>
                                                )}
                                            </div>

                                            <div className="pt-4 mt-4 border-t border-white/5 space-y-3">
                                                {/* Metrics */}
                                                <div className="grid grid-cols-3 gap-2 text-center">
                                                    <div className="bg-slate-950/40 rounded-xl p-2">
                                                        <p className="text-[9px] font-bold text-slate-500 uppercase tracking-wider">Frames</p>
                                                        <p className="text-sm font-black text-indigo-400">{proj.frame_count || 0}</p>
                                                    </div>
                                                    <div className="bg-slate-950/40 rounded-xl p-2">
                                                        <p className="text-[9px] font-bold text-slate-500 uppercase tracking-wider">Scenes</p>
                                                        <p className="text-sm font-black text-slate-300">{proj.scene_count || 0}</p>
                                                    </div>
                                                    <div className="bg-slate-950/40 rounded-xl p-2">
                                                        <p className="text-[9px] font-bold text-slate-500 uppercase tracking-wider">Cast</p>
                                                        <p className="text-sm font-black text-violet-400">{proj.character_count || 0}</p>
                                                    </div>
                                                </div>

                                                {/* Action Bar */}
                                                <div className="flex items-center gap-2 pt-1">
                                                    <button
                                                        onClick={() => handleSelectProject(proj.id, 'gallery')}
                                                        className="flex-1 bg-indigo-600/20 hover:bg-indigo-600/30 text-indigo-300 py-2 rounded-xl text-xs font-bold transition-colors flex items-center justify-center gap-1.5 border border-indigo-500/20"
                                                    >
                                                        <span>View Gallery</span>
                                                        <ArrowRight className="w-3 h-3" />
                                                    </button>
                                                    {proj.frame_count > 0 && (
                                                        <button
                                                            onClick={(e) => handleExportDirectPdf(proj.id, proj.name, e)}
                                                            title="Direct Download PDF Storyboard"
                                                            className="p-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl transition-colors border border-white/5"
                                                        >
                                                            <Download className="w-4 h-4" />
                                                        </button>
                                                    )}
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    </div>
                )}

                {view === 'examples' && (
                    <ExampleScriptsHub
                        onSelectExample={handleExampleSelected}
                        currentProjectId={projectId}
                    />
                )}

                {view === 'upload' && projectId && (
                    <ScriptUploader projectId={projectId} onUploadSuccess={handleUploadSuccess} />
                )}

                {view === 'config' && (
                    <Configuration onSave={handleConfigSave} />
                )}

                {view === 'gallery' && projectId && (
                    <StoryboardGallery projectId={projectId} config={config} />
                )}

                {view === 'characters' && (
                    <CharacterLibraryView projectId={projectId} />
                )}

                {view === 'story_doctor' && (
                    <StoryDoctorView projectId={projectId} />
                )}

                {view === 'table_read' && (
                    <TableReadStudio projectId={projectId} />
                )}

                {view === 'graphic_novel' && (
                    <GraphicNovelStudio projectId={projectId} />
                )}
            </main>

            {/* Footer with Covenant & 10 Laws Attribution */}
            <footer className="border-t border-white/5 py-8 mt-auto">
                <div className="max-w-7xl mx-auto px-4 space-y-4">
                    <div className="text-center py-2 border-b border-white/5">
                        <blockquote className="text-slate-500 text-xs italic">
                            &ldquo;Every element is used because the story demands it &mdash; not as a syntax exercise.&rdquo;
                        </blockquote>
                        <cite className="text-[9px] font-bold uppercase tracking-widest text-indigo-500/60 mt-1 block not-italic">
                            — ACS4.6 &nbsp;&middot;&nbsp; Anthropic Claude Sonnet 4.6
                        </cite>
                    </div>
                    <div className="flex flex-col md:flex-row items-center justify-between gap-4 text-xs text-slate-600">
                        <div className="flex items-center gap-2">
                            <Clapperboard className="w-4 h-4 text-indigo-500" />
                            <span className="font-bold text-slate-400">Storyboard AI</span>
                            <span>&middot; Oscar / Level 3 Presentation Suite</span>
                        </div>
                        <div>
                            Governed by Kirk LaSalle&rsquo;s Permanent Active Directives (The 10 Laws)
                        </div>
                        <div>
                            &copy; {new Date().getFullYear()} Storyboard AI
                        </div>
                    </div>
                </div>
            </footer>

            {/* Shutdown Confirmation Modal */}
            <ShutdownModal
                isOpen={showShutdownModal}
                onClose={() => setShowShutdownModal(false)}
                onShutdownComplete={() => {
                    setShowShutdownModal(false);
                    setIsShutDown(true);
                }}
            />

            {/* NLE Keyboard Shortcuts Reference Modal */}
            <NleShortcutsModal
                isOpen={showNleShortcutsModal}
                onClose={() => setShowNleShortcutsModal(false)}
            />

            {/* Floating Debug Button */}
            <button
                onClick={copyDebugInfo}
                title="Copy Debug Info"
                className="fixed bottom-6 right-6 p-3.5 bg-rose-600 hover:bg-rose-700 rounded-full shadow-2xl transition-all z-50 flex items-center gap-2 group"
            >
                <Bug className="w-5 h-5 text-white" />
                <span className="hidden group-hover:inline text-white text-xs font-bold">Copy Debug</span>
            </button>

            {/* Error Toast */}
            {globalErrors.length > 0 && (
                <div className="fixed bottom-24 right-6 bg-rose-500/90 text-white p-4 rounded-xl shadow-lg max-w-sm text-sm z-50">
                    <div className="font-bold mb-2">Recent Errors</div>
                    <div className="space-y-1 max-h-32 overflow-y-auto text-xs">
                        {globalErrors.slice(-5).map((err, i) => (
                            <div key={i} className="opacity-80">{err}</div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    )
}

export default App
