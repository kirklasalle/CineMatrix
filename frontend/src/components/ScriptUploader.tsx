import React, { useState } from 'react';
import { Upload, FileText, CheckCircle, AlertCircle, Shield, BookOpen, Sparkles, ArrowRight, Layers, Cpu } from 'lucide-react';
import { API_BASE } from '../utils/api';
import { ExampleScriptsHub, ExampleScriptMeta } from './ExampleScriptsHub';

interface ScriptUploaderProps {
    onUploadSuccess: (id: string) => void;
    projectId: string;
}

const FEATURED_LEARNING_SCRIPTS = [
    {
        category: 'engines',
        filename: '10_story_doctor_15_beats.fountain',
        title: 'The Alchemist\'s Horizon',
        engine: 'Story Doctor (15 Beats)',
        format: 'Fountain',
        tag: 'Structural Masterclass',
    },
    {
        category: 'genres',
        filename: '16_sci_fi_cyberpunk_neo_noir.fountain',
        title: 'Nexus Zero: Synthetic Tears',
        engine: 'Style Vault Neo-Noir',
        format: 'Fountain',
        tag: 'Blade Runner Style',
    },
    {
        category: 'engines',
        filename: '11_table_read_ensemble_cast.fountain',
        title: 'Summit at Blackwood Manor',
        engine: 'Table Read Studio',
        format: 'Fountain',
        tag: '6-Voice Auditions',
    },
    {
        category: 'spectrum',
        filename: '25_micro_scene_1min.fountain',
        title: 'The Cold Call (1-Min Demo)',
        engine: '10-Sec Rapid Test',
        format: 'Fountain',
        tag: 'Instant Setup',
    },
];

export const ScriptUploader: React.FC<ScriptUploaderProps> = ({ onUploadSuccess, projectId }) => {
    const [file, setFile] = useState<File | null>(null);
    const [status, setStatus] = useState<'idle' | 'uploading' | 'success' | 'error'>('idle');
    const [showExamplesModal, setShowExamplesModal] = useState(false);
    const [loadingExample, setLoadingExample] = useState<string | null>(null);

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            setFile(e.target.files[0]);
        }
    };

    const handleUpload = async () => {
        if (!file) return;

        setStatus('uploading');
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch(`${API_BASE}/projects/${projectId}/scripts`, {
                method: 'POST',
                body: formData,
            });

            if (response.ok) {
                const data = await response.json();
                setStatus('success');
                onUploadSuccess(data.id);
            } else {
                setStatus('error');
            }
        } catch (error) {
            console.error('Upload failed:', error);
            setStatus('error');
        }
    };

    const handleLoadExample = async (category: string, filename: string) => {
        setLoadingExample(filename);
        try {
            const response = await fetch(`${API_BASE}/projects/${projectId}/load-example`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ category, filename }),
            });

            if (response.ok) {
                const data = await response.json();
                setStatus('success');
                onUploadSuccess(data.script_id || projectId);
            } else {
                setStatus('error');
            }
        } catch (err) {
            console.error('Failed to load example script:', err);
            setStatus('error');
        } finally {
            setLoadingExample(null);
            setShowExamplesModal(false);
        }
    };

    return (
        <div className="max-w-2xl mx-auto space-y-6">
            <div className="glass-morphism rounded-3xl p-8 border border-white/10">
                <div className="flex flex-col items-center gap-6 text-center">
                    <div className="w-16 h-16 rounded-2xl bg-indigo-500/20 border border-indigo-500/30 flex items-center justify-center">
                        <FileText className="w-8 h-8 text-indigo-400" />
                    </div>
                    <div>
                        <h3 className="text-2xl font-black text-white">Upload Your Script</h3>
                        <p className="text-sm text-slate-400 mt-1">
                            Supports Fountain, Final Draft (.fdx), PDF, Word (.docx), Comic (.cbz), ePub, or plain text
                        </p>
                    </div>

                    <label className="w-full h-36 border-2 border-dashed border-slate-700 hover:border-indigo-500/50 rounded-2xl flex items-center justify-center cursor-pointer transition-all group bg-slate-900/30 hover:bg-slate-900/50">
                        <input type="file" className="hidden" onChange={handleFileChange} />
                        {file ? (
                            <div className="flex items-center gap-2 text-indigo-300 font-bold">
                                <FileText className="w-5 h-5 text-indigo-400" />
                                <span>{file.name}</span>
                            </div>
                        ) : (
                            <div className="flex flex-col items-center gap-2">
                                <Upload className="w-6 h-6 text-slate-500 group-hover:text-indigo-400 transition-colors" />
                                <span className="text-sm text-slate-400 font-medium">Click to select script file or drag &amp; drop</span>
                                <span className="text-[11px] text-slate-600">Max size 20 MB</span>
                            </div>
                        )}
                    </label>

                    {file && status !== 'success' && (
                        <button
                            onClick={handleUpload}
                            disabled={status === 'uploading'}
                            className="w-full py-3.5 bg-indigo-600 rounded-xl font-bold hover:bg-indigo-700 transition-all flex items-center justify-center gap-2 shadow-lg shadow-indigo-600/20 text-white text-sm"
                        >
                            {status === 'uploading' ? 'Analyzing Script...' : 'Continue with Uploaded Script'}
                        </button>
                    )}

                    {/* ── Example Scripts Learning Section ────────────────── */}
                    <div className="w-full pt-6 border-t border-white/10 text-left space-y-4">
                        <div className="flex items-center justify-between">
                            <div className="flex items-center gap-2">
                                <Sparkles className="w-4 h-4 text-amber-400" />
                                <span className="text-xs font-black uppercase tracking-wider text-white">
                                    Or Start with an Example Script
                                </span>
                            </div>
                            <button
                                type="button"
                                onClick={() => setShowExamplesModal(true)}
                                className="text-xs font-bold text-indigo-400 hover:text-indigo-300 transition-colors flex items-center gap-1"
                            >
                                <span>Browse All 27 Scripts</span>
                                <ArrowRight className="w-3 h-3" />
                            </button>
                        </div>

                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                            {FEATURED_LEARNING_SCRIPTS.map((s) => (
                                <button
                                    key={s.filename}
                                    type="button"
                                    onClick={() => handleLoadExample(s.category, s.filename)}
                                    disabled={loadingExample === s.filename}
                                    className="p-3.5 rounded-2xl bg-slate-900/60 hover:bg-indigo-950/40 border border-white/5 hover:border-indigo-500/40 text-left transition-all group flex flex-col justify-between"
                                >
                                    <div>
                                        <div className="flex items-center justify-between text-[10px] font-bold text-slate-500 mb-1">
                                            <span className="text-indigo-400">{s.tag}</span>
                                            <span className="uppercase text-slate-400">{s.format}</span>
                                        </div>
                                        <h4 className="text-xs font-bold text-white group-hover:text-indigo-300 transition-colors line-clamp-1">
                                            {s.title}
                                        </h4>
                                    </div>
                                    <div className="flex items-center justify-between pt-2 mt-2 border-t border-white/5 text-[11px] text-slate-400">
                                        <span>{s.engine}</span>
                                        <span className="text-indigo-400 font-bold group-hover:translate-x-0.5 transition-transform">
                                            {loadingExample === s.filename ? 'Loading...' : 'Load →'}
                                        </span>
                                    </div>
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* ── Content Agreement Notice ────────────────────────── */}
                    <div className="w-full rounded-2xl border border-indigo-500/15 bg-indigo-500/5 p-4 text-left space-y-3">
                        <div className="flex items-center gap-2">
                            <Shield className="w-3.5 h-3.5 text-indigo-400 shrink-0" />
                            <span className="text-[10px] font-black uppercase tracking-widest text-indigo-400">
                                Content Agreement — Active &amp; Binding
                            </span>
                        </div>
                        <p className="text-[10px] text-slate-400 leading-relaxed">
                            By uploading, you grant Storyboard AI an irrevocable license to analyze your work
                            and learn from it — like a skilled reader who learns <em>craft and pattern</em>,
                            not verbatim content. <strong className="text-slate-300">You retain full copyright.</strong> Raw content
                            is analyzed then discarded. Only distilled cinematic insights are added to our
                            Knowledge Base. No personal data is stored.
                        </p>
                        <div className="grid grid-cols-2 gap-1.5">
                            {[
                                'You keep full copyright',
                                'Raw content is never stored',
                                'Only craft insights retained',
                                'No personal data stored',
                            ].map((point) => (
                                <div key={point} className="flex items-center gap-1.5 text-[9px] text-slate-500">
                                    <div className="w-1 h-1 rounded-full bg-indigo-500 shrink-0" />
                                    {point}
                                </div>
                            ))}
                        </div>
                        <div className="flex items-center gap-1.5 pt-1 border-t border-white/5">
                            <BookOpen className="w-3 h-3 text-slate-600 shrink-0" />
                            <span className="text-[9px] text-slate-600">
                                Governed by Kirk LaSalle's 10 Laws (Laws 6, 7 &amp; 8 — Privacy, Transparency &amp; Equity)
                            </span>
                        </div>
                    </div>

                    {status === 'success' && (
                        <div className="flex items-center gap-2 text-emerald-500 font-medium">
                            <CheckCircle className="w-5 h-5" />
                            <span>Script Loaded Successfully!</span>
                        </div>
                    )}

                    {status === 'error' && (
                        <div className="flex items-center gap-2 text-rose-500 font-medium">
                            <AlertCircle className="w-5 h-5" />
                            <span>Script processing failed. Please try again.</span>
                        </div>
                    )}
                </div>
            </div>

            {/* Full 27-Script Selection Modal */}
            {showExamplesModal && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-in fade-in duration-200">
                    <div className="glass-morphism rounded-3xl border border-indigo-500/30 bg-slate-900/95 max-w-5xl w-full max-h-[90vh] overflow-y-auto p-6 shadow-2xl">
                        <ExampleScriptsHub
                            isModal={true}
                            currentProjectId={projectId}
                            onClose={() => setShowExamplesModal(false)}
                            onSelectExample={(_ex, _mode) => {
                                setShowExamplesModal(false);
                                setStatus('success');
                                onUploadSuccess(projectId);
                            }}
                        />
                    </div>
                </div>
            )}
        </div>
    );
};
