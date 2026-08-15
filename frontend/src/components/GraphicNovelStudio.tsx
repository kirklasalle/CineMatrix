import React, { useEffect, useState } from 'react';
import { BookOpen, Sparkles, Download, Layers, Layout, ChevronLeft, ChevronRight, Loader2, MessageSquare, Image, Award } from 'lucide-react';
import { API_BASE } from '../utils/api';

interface Panel {
    panel_index: number;
    scene_number: number;
    heading: string;
    description: string;
    moment_summary: string;
    image_path?: string;
    dialogue_balloons: string[];
    caption?: string;
}

interface Page {
    page_number: number;
    layout: string;
    layout_name: string;
    panels: Panel[];
}

interface LayoutOption {
    id: string;
    name: string;
    panels_per_page: number;
    description: string;
}

interface GraphicNovelStudioProps {
    projectId: string | null;
}

export const GraphicNovelStudio: React.FC<GraphicNovelStudioProps> = ({ projectId }) => {
    const [layouts, setLayouts] = useState<LayoutOption[]>([]);
    const [selectedLayout, setSelectedLayout] = useState<string>('4_quadrant');
    const [pages, setPages] = useState<Page[]>([]);
    const [currentPageIndex, setCurrentPageIndex] = useState<number>(0);
    const [loading, setLoading] = useState(true);
    const [exporting, setExporting] = useState(false);

    useEffect(() => {
        const fetchLayouts = async () => {
            try {
                const resp = await fetch(`${API_BASE}/graphic-novel/layouts`);
                if (resp.ok) {
                    const data = await resp.json();
                    setLayouts(data.layouts || []);
                }
            } catch (e) {
                console.error('Layouts fetch error', e);
            }
        };
        fetchLayouts();
    }, []);

    useEffect(() => {
        if (!projectId) {
            setLoading(false);
            return;
        }

        const fetchPages = async () => {
            setLoading(true);
            try {
                const resp = await fetch(`${API_BASE}/projects/${projectId}/graphic-novel/pages?layout=${selectedLayout}`);
                if (resp.ok) {
                    const data = await resp.json();
                    setPages(data.pages || []);
                    setCurrentPageIndex(0);
                }
            } catch (e) {
                console.error('Pages fetch error', e);
            } finally {
                setLoading(false);
            }
        };

        fetchPages();
    }, [projectId, selectedLayout]);

    const handleExportPrintPDF = () => {
        if (!projectId) return;
        window.open(`${API_BASE}/projects/${projectId}/export/graphic-novel-print.pdf?layout=${selectedLayout}`, '_blank');
    };

    const handleExportCBZ = () => {
        if (!projectId) return;
        window.open(`${API_BASE}/projects/${projectId}/export/storyboard.cbz`, '_blank');
    };

    if (!projectId) {
        return (
            <div className="text-center py-24 space-y-4">
                <BookOpen className="w-16 h-16 text-slate-700 mx-auto" />
                <h3 className="text-xl font-bold text-white">No Project Selected</h3>
                <p className="text-sm text-slate-500 max-w-md mx-auto">
                    Please select a project from the Projects Hub to open the Graphic Novel Creation Studio.
                </p>
            </div>
        );
    }

    const currentPage = pages[currentPageIndex];

    return (
        <div className="space-y-6 max-w-7xl mx-auto animate-in fade-in duration-500">
            {/* Header & Controls */}
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-rose-500/20 bg-rose-500/10 text-rose-300 text-xs font-bold uppercase tracking-widest mb-1">
                        <Sparkles className="w-3.5 h-3.5" />
                        <span>Dynamic Comic &amp; Graphic Novel Studio</span>
                    </div>
                    <h2 className="text-4xl font-black tracking-tight text-white">Graphic Novel Studio</h2>
                    <p className="text-slate-400 text-sm">Multi-panel layout generator, speech balloons, and 300 DPI CMYK Print PDF</p>
                </div>

                {/* Direct Exporters */}
                <div className="flex items-center gap-2.5">
                    <button
                        onClick={handleExportCBZ}
                        className="px-4 py-2.5 bg-slate-900/80 hover:bg-slate-800 border border-white/10 text-slate-200 hover:text-white rounded-2xl text-xs font-bold transition-all flex items-center gap-2"
                    >
                        <Download className="w-3.5 h-3.5 text-indigo-400" />
                        <span>Export .CBZ Comic</span>
                    </button>

                    <button
                        onClick={handleExportPrintPDF}
                        className="px-5 py-2.5 bg-rose-600 hover:bg-rose-700 text-white rounded-2xl text-xs font-bold transition-all flex items-center gap-2 shadow-lg shadow-rose-600/20"
                    >
                        <Download className="w-3.5 h-3.5" />
                        <span>300 DPI Print PDF</span>
                    </button>
                </div>
            </div>

            {/* Layout Preset Selector Bar */}
            <div className="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-none">
                {layouts.map((l) => (
                    <button
                        key={l.id}
                        onClick={() => setSelectedLayout(l.id)}
                        className={`px-4 py-2 rounded-xl text-xs font-bold whitespace-nowrap transition-all border ${selectedLayout === l.id
                            ? 'bg-rose-600/20 border-rose-500 text-rose-300 shadow-md shadow-rose-500/10'
                            : 'bg-slate-900/40 border-white/5 text-slate-400 hover:text-white hover:border-white/20'
                            }`}
                    >
                        {l.name}
                    </button>
                ))}
            </div>

            {/* Main Comic Page Canvas */}
            {loading ? (
                <div className="py-24 text-center space-y-3">
                    <Loader2 className="w-8 h-8 text-rose-500 animate-spin mx-auto" />
                    <p className="text-sm text-slate-400">Paginating scenes &amp; calculating speech balloon geometry...</p>
                </div>
            ) : pages.length === 0 ? (
                <div className="text-center py-20 bg-slate-900/30 rounded-3xl border border-white/5">
                    <p className="text-slate-400">No pages generated. Please analyze screenplay scenes first.</p>
                </div>
            ) : (
                <div className="space-y-4">
                    {/* Page Navigator */}
                    <div className="flex items-center justify-between bg-slate-900/60 border border-white/10 px-6 py-3 rounded-2xl">
                        <span className="text-xs font-bold text-slate-400">
                            Page <span className="text-white font-mono text-sm">{currentPageIndex + 1}</span> of {pages.length} &middot; {currentPage.layout_name}
                        </span>

                        <div className="flex items-center gap-2">
                            <button
                                onClick={() => setCurrentPageIndex(Math.max(0, currentPageIndex - 1))}
                                disabled={currentPageIndex === 0}
                                className="p-2 text-slate-400 hover:text-white disabled:opacity-30 rounded-xl hover:bg-white/5"
                            >
                                <ChevronLeft className="w-4 h-4" />
                            </button>
                            <button
                                onClick={() => setCurrentPageIndex(Math.min(pages.length - 1, currentPageIndex + 1))}
                                disabled={currentPageIndex >= pages.length - 1}
                                className="p-2 text-slate-400 hover:text-white disabled:opacity-30 rounded-xl hover:bg-white/5"
                            >
                                <ChevronRight className="w-4 h-4" />
                            </button>
                        </div>
                    </div>

                    {/* Comic Book Page Surface */}
                    <div className="bg-white text-slate-950 rounded-3xl p-8 shadow-2xl border-4 border-slate-900 min-h-[700px] flex flex-col justify-between">
                        {/* Comic Page Title Slate */}
                        <div className="flex items-center justify-between border-b-2 border-slate-900 pb-3 mb-6">
                            <span className="text-xs font-black uppercase tracking-widest text-slate-900">
                                GRAPHIC NOVEL ADAPTATION &middot; PAGE {currentPage.page_number}
                            </span>
                            <span className="text-[10px] font-mono text-slate-500 uppercase tracking-wider">
                                300 DPI MASTER PRINT EDITION
                            </span>
                        </div>

                        {/* Panels Grid */}
                        <div className={`grid gap-4 flex-1 ${currentPage.panels.length === 1 ? 'grid-cols-1' :
                            currentPage.panels.length === 2 ? 'grid-cols-1 md:grid-cols-2' :
                                currentPage.panels.length === 3 ? 'grid-cols-1 md:grid-cols-3' :
                                    currentPage.panels.length <= 4 ? 'grid-cols-1 md:grid-cols-2' :
                                        'grid-cols-1 md:grid-cols-3'
                            }`}>
                            {currentPage.panels.map((panel, pIdx) => (
                                <div
                                    key={pIdx}
                                    className="border-2 border-slate-900 rounded-2xl p-5 bg-slate-50 flex flex-col justify-between relative overflow-hidden group shadow-sm hover:shadow-md transition-shadow"
                                >
                                    {/* Panel Header */}
                                    <div className="space-y-1">
                                        <div className="flex items-center justify-between">
                                            <span className="text-[10px] font-black uppercase tracking-widest bg-slate-900 text-white px-2 py-0.5 rounded">
                                                PANEL {panel.panel_index}
                                            </span>
                                            <span className="text-[10px] font-bold text-slate-500">
                                                Scene {panel.scene_number}
                                            </span>
                                        </div>
                                        <h4 className="font-black text-xs text-slate-900 truncate">{panel.heading}</h4>
                                    </div>

                                    {/* Panel Moment Excerpt */}
                                    <p className="text-xs text-slate-700 my-4 line-clamp-3 leading-relaxed font-serif">
                                        {panel.description}
                                    </p>

                                    {/* Speech Balloon Overlay */}
                                    {panel.dialogue_balloons.length > 0 && (
                                        <div className="bg-white border-2 border-slate-900 rounded-2xl p-3 shadow-md relative">
                                            <p className="text-xs font-bold text-slate-900 italic">
                                                &ldquo;{panel.dialogue_balloons[0]}&rdquo;
                                            </p>
                                            <div className="absolute -bottom-2 left-6 w-3 h-3 bg-white border-b-2 border-r-2 border-slate-900 transform rotate-45"></div>
                                        </div>
                                    )}
                                </div>
                            ))}
                        </div>

                        {/* Page Footer */}
                        <div className="text-center pt-6 border-t border-slate-200 mt-6">
                            <span className="text-[10px] font-mono text-slate-400 uppercase tracking-widest">
                                &mdash; Page {currentPage.page_number} &mdash;
                            </span>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};
