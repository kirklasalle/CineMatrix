import React, { useEffect, useState } from 'react';
import { Maximize2, Minimize2, ChevronLeft, ChevronRight, X, Volume2, Film, Sparkles, Play } from 'lucide-react';
import { API_BASE } from '../utils/api';

interface Frame {
    id: string;
    scene_number: number;
    heading: string;
    description: string;
    intensity_score: number;
    intensity_type: string;
    moment_summary: string;
    image_path?: string;
    camera_shot_type?: string;
    audio_mood?: string;
}

interface PresentationModeProps {
    frames: Frame[];
    initialIndex?: number;
    onClose: () => void;
}

export const PresentationMode: React.FC<PresentationModeProps> = ({
    frames,
    initialIndex = 0,
    onClose,
}) => {
    const [currentIndex, setCurrentIndex] = useState<number>(initialIndex);
    const [isFullscreen, setIsFullscreen] = useState<boolean>(false);
    const [showNotes, setShowNotes] = useState<boolean>(true);

    const currentFrame = frames[currentIndex];

    // Keyboard controls
    useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            if (e.key === 'ArrowRight' || e.key === ' ') {
                e.preventDefault();
                setCurrentIndex(prev => Math.min(frames.length - 1, prev + 1));
            } else if (e.key === 'ArrowLeft') {
                e.preventDefault();
                setCurrentIndex(prev => Math.max(0, prev - 1));
            } else if (e.key === 'Escape') {
                onClose();
            } else if (e.key.toLowerCase() === 'f') {
                toggleFullscreen();
            } else if (e.key.toLowerCase() === 'n') {
                setShowNotes(prev => !prev);
            }
        };

        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [frames.length, onClose]);

    const toggleFullscreen = () => {
        if (!document.fullscreenElement) {
            document.documentElement.requestFullscreen().catch(() => {});
            setIsFullscreen(true);
        } else {
            document.exitFullscreen().catch(() => {});
            setIsFullscreen(false);
        }
    };

    if (!currentFrame) return null;

    return (
        <div className="fixed inset-0 z-50 bg-black text-white flex flex-col justify-between select-none animate-in fade-in duration-300">
            {/* Top Control Bar */}
            <div className="flex items-center justify-between p-6 bg-gradient-to-b from-black/80 to-transparent z-10">
                <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-xl bg-indigo-600/30 border border-indigo-500/40 flex items-center justify-center">
                        <Film className="w-4 h-4 text-indigo-400" />
                    </div>
                    <div>
                        <span className="text-[10px] font-black uppercase tracking-widest text-indigo-400">Director Presentation Mode</span>
                        <h2 className="text-sm font-bold text-slate-200">
                            Scene {currentFrame.scene_number} of {frames.length} &middot; {currentFrame.heading}
                        </h2>
                    </div>
                </div>

                <div className="flex items-center gap-2">
                    <button
                        onClick={() => setShowNotes(!showNotes)}
                        className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all border ${showNotes ? 'bg-white/15 border-white/20 text-white' : 'bg-transparent border-white/5 text-slate-400'}`}
                    >
                        Notes (N)
                    </button>

                    <button
                        onClick={toggleFullscreen}
                        className="p-2 text-slate-400 hover:text-white rounded-xl hover:bg-white/10 transition-colors"
                        title="Toggle Fullscreen (F)"
                    >
                        {isFullscreen ? <Minimize2 className="w-5 h-5" /> : <Maximize2 className="w-5 h-5" />}
                    </button>

                    <button
                        onClick={onClose}
                        className="p-2 text-slate-400 hover:text-white rounded-xl hover:bg-rose-500/20 transition-colors"
                        title="Exit (Esc)"
                    >
                        <X className="w-5 h-5 text-rose-400" />
                    </button>
                </div>
            </div>

            {/* Central Stage Canvas */}
            <div className="flex-1 relative flex items-center justify-center p-8">
                {/* Previous Button */}
                <button
                    onClick={() => setCurrentIndex(Math.max(0, currentIndex - 1))}
                    disabled={currentIndex === 0}
                    className="absolute left-6 z-20 p-4 rounded-full bg-black/60 hover:bg-indigo-600/80 border border-white/10 text-white disabled:opacity-20 transition-all hover:scale-110"
                >
                    <ChevronLeft className="w-6 h-6" />
                </button>

                {/* Main Frame Viewport */}
                <div className="max-h-[75vh] max-w-[85vw] aspect-video rounded-3xl overflow-hidden shadow-2xl border border-white/10 bg-slate-950 flex items-center justify-center relative group">
                    {currentFrame.image_path ? (
                        <img
                            src={currentFrame.image_path.startsWith('data:') || currentFrame.image_path.startsWith('http')
                                ? currentFrame.image_path
                                : `${API_BASE}${currentFrame.image_path}`}
                            alt={currentFrame.heading}
                            className="w-full h-full object-cover"
                        />
                    ) : (
                        <div className="p-12 text-center space-y-4">
                            <Sparkles className="w-16 h-16 text-indigo-400/40 mx-auto" />
                            <p className="text-xl font-serif text-slate-300 italic max-w-lg">
                                &ldquo;{currentFrame.description}&rdquo;
                            </p>
                        </div>
                    )}

                    {/* Lower-Third Cinematic Slate Overlay */}
                    {showNotes && (
                        <div className="absolute bottom-0 inset-x-0 bg-gradient-to-t from-black via-black/80 to-transparent p-6 space-y-2">
                            <div className="flex items-center justify-between">
                                <div className="flex items-center gap-2">
                                    <span className="text-[10px] font-black uppercase tracking-widest bg-indigo-600 text-white px-2.5 py-0.5 rounded-full">
                                        SCENE {currentFrame.scene_number}
                                    </span>
                                    <span className="text-xs font-bold text-white font-mono">
                                        {currentFrame.camera_shot_type || 'Widescreen Master'}
                                    </span>
                                </div>
                                <span className="text-xs font-bold text-indigo-400">
                                    {Math.round((currentFrame.intensity_score || 5) * 10)}% Dramatic Intensity
                                </span>
                            </div>

                            <p className="text-xs text-slate-300 font-serif line-clamp-2 max-w-3xl leading-relaxed">
                                {currentFrame.description}
                            </p>
                        </div>
                    )}
                </div>

                {/* Next Button */}
                <button
                    onClick={() => setCurrentIndex(Math.min(frames.length - 1, currentIndex + 1))}
                    disabled={currentIndex >= frames.length - 1}
                    className="absolute right-6 z-20 p-4 rounded-full bg-black/60 hover:bg-indigo-600/80 border border-white/10 text-white disabled:opacity-20 transition-all hover:scale-110"
                >
                    <ChevronRight className="w-6 h-6" />
                </button>
            </div>

            {/* Bottom Scene Thumbnail Scrubber */}
            <div className="p-4 bg-black/80 backdrop-blur-md border-t border-white/5 flex items-center gap-3 overflow-x-auto scrollbar-none z-10">
                {frames.map((f, idx) => (
                    <button
                        key={f.id || idx}
                        onClick={() => setCurrentIndex(idx)}
                        className={`flex-shrink-0 w-24 h-14 rounded-xl overflow-hidden border-2 transition-all relative ${currentIndex === idx
                            ? 'border-indigo-500 scale-105 shadow-lg shadow-indigo-500/20'
                            : 'border-white/10 opacity-50 hover:opacity-100'
                            }`}
                    >
                        {f.image_path ? (
                            <img
                                src={f.image_path.startsWith('data:') || f.image_path.startsWith('http')
                                    ? f.image_path
                                    : `${API_BASE}${f.image_path}`}
                                alt={`Scene ${f.scene_number}`}
                                className="w-full h-full object-cover"
                            />
                        ) : (
                            <div className="w-full h-full bg-slate-900 flex items-center justify-center text-[10px] font-bold text-slate-500">
                                S{f.scene_number}
                            </div>
                        )}
                        <span className="absolute bottom-1 right-1 px-1 rounded bg-black/80 text-[8px] font-bold text-white">
                            {f.scene_number}
                        </span>
                    </button>
                ))}
            </div>
        </div>
    );
};
