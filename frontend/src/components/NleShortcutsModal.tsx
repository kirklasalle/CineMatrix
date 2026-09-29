import React from 'react';
import { Clapperboard, X, Command, Film, Sparkles, Sliders, Play, SkipBack, SkipForward, Pause, BookOpen, Mic, Users, Settings } from 'lucide-react';

interface NleShortcutsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const NleShortcutsModal: React.FC<NleShortcutsModalProps> = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4 selection:bg-indigo-500/30 animate-in fade-in duration-200">
      <div 
        className="glass-morphism rounded-3xl border border-indigo-500/30 bg-slate-900/95 max-w-2xl w-full p-6 sm:p-8 shadow-2xl shadow-indigo-950/50 space-y-6 animate-in zoom-in-95 duration-200"
        role="dialog"
        aria-modal="true"
      >
        {/* Header */}
        <div className="flex items-center justify-between border-b border-white/10 pb-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-indigo-600/20 border border-indigo-500/40 flex items-center justify-center text-indigo-400">
              <Clapperboard className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-xl font-black text-white">NLE Keyboard Controls</h2>
                <span className="text-[10px] uppercase tracking-wider font-extrabold px-2 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                  Avid / Premiere / Resolve
                </span>
              </div>
              <p className="text-xs text-slate-400">
                Non-linear editing keyboard navigation &amp; 9-studio hotkeys
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="w-8 h-8 rounded-xl bg-white/5 hover:bg-white/10 text-slate-400 hover:text-white flex items-center justify-center transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Content Columns */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-sm">
          {/* Studio Switcher (1-9) */}
          <div className="space-y-3">
            <div className="flex items-center gap-2 text-xs font-black uppercase tracking-widest text-indigo-400">
              <Command className="w-3.5 h-3.5" />
              <span>Studio Quick-Switch</span>
            </div>
            <div className="space-y-1.5 bg-slate-950/60 rounded-2xl p-3.5 border border-white/5">
              {[
                { key: '1', name: 'Projects Hub', desc: 'Home & recent scripts', icon: Film },
                { key: '2', name: 'Script Ingestion', desc: 'Upload .fdx, .fountain, etc.', icon: Clapperboard },
                { key: '3', name: 'Storyboard Gallery', desc: 'Shot list & animatics', icon: Sparkles },
                { key: '4', name: 'Cast & Archetypes', desc: 'Character consistency vault', icon: Users },
                { key: '5', name: 'Table Read Studio', desc: 'Multi-voice auditioning', icon: Mic },
                { key: '6', name: 'Story Doctor', desc: 'Blake Snyder 15-beat review', icon: BookOpen },
                { key: '7', name: 'Graphic Novel', desc: '300 DPI CMYK print export', icon: Sparkles },
                { key: '8', name: 'Examples Library', desc: '27 pre-analyzed master scripts', icon: Film },
                { key: '9', name: 'Config & Models', desc: 'Local SLM & API providers', icon: Settings },
              ].map(item => (
                <div key={item.key} className="flex items-center justify-between text-xs py-1">
                  <div className="flex items-center gap-2 text-slate-300 font-medium">
                    <span className="text-slate-500"><item.icon className="w-3.5 h-3.5" /></span>
                    <span>{item.name}</span>
                  </div>
                  <kbd className="px-2 py-0.5 rounded bg-slate-800 border border-slate-700 font-mono text-[11px] font-bold text-indigo-300">
                    {item.key}
                  </kbd>
                </div>
              ))}
            </div>
          </div>

          {/* J-K-L Playback & Presentation */}
          <div className="space-y-6">
            {/* Playback Controls */}
            <div className="space-y-3">
              <div className="flex items-center gap-2 text-xs font-black uppercase tracking-widest text-emerald-400">
                <Play className="w-3.5 h-3.5" />
                <span>J-K-L Scrubbing &amp; Audition</span>
              </div>
              <div className="space-y-1.5 bg-slate-950/60 rounded-2xl p-3.5 border border-white/5">
                <div className="flex items-center justify-between text-xs py-1">
                  <span className="text-slate-300 font-medium">Play / Pause Audition</span>
                  <kbd className="px-2.5 py-0.5 rounded bg-slate-800 border border-slate-700 font-mono text-[11px] font-bold text-emerald-300">
                    Space
                  </kbd>
                </div>
                <div className="flex items-center justify-between text-xs py-1">
                  <span className="text-slate-300 font-medium">Rewind / Step Back</span>
                  <div className="flex gap-1">
                    <kbd className="px-2 py-0.5 rounded bg-slate-800 border border-slate-700 font-mono text-[11px] font-bold text-emerald-300">J</kbd>
                    <kbd className="px-2 py-0.5 rounded bg-slate-800 border border-slate-700 font-mono text-[11px] font-bold text-emerald-300">←</kbd>
                  </div>
                </div>
                <div className="flex items-center justify-between text-xs py-1">
                  <span className="text-slate-300 font-medium">Pause Playback</span>
                  <kbd className="px-2 py-0.5 rounded bg-slate-800 border border-slate-700 font-mono text-[11px] font-bold text-emerald-300">
                    K
                  </kbd>
                </div>
                <div className="flex items-center justify-between text-xs py-1">
                  <span className="text-slate-300 font-medium">Forward / Step Next</span>
                  <div className="flex gap-1">
                    <kbd className="px-2 py-0.5 rounded bg-slate-800 border border-slate-700 font-mono text-[11px] font-bold text-emerald-300">L</kbd>
                    <kbd className="px-2 py-0.5 rounded bg-slate-800 border border-slate-700 font-mono text-[11px] font-bold text-emerald-300">→</kbd>
                  </div>
                </div>
              </div>
            </div>

            {/* Presentation & Help */}
            <div className="space-y-3">
              <div className="flex items-center gap-2 text-xs font-black uppercase tracking-widest text-amber-400">
                <Sliders className="w-3.5 h-3.5" />
                <span>Presentation Mode &amp; Help</span>
              </div>
              <div className="space-y-1.5 bg-slate-950/60 rounded-2xl p-3.5 border border-white/5">
                <div className="flex items-center justify-between text-xs py-1">
                  <span className="text-slate-300 font-medium">Toggle Fullscreen Mode</span>
                  <kbd className="px-2 py-0.5 rounded bg-slate-800 border border-slate-700 font-mono text-[11px] font-bold text-amber-300">
                    F
                  </kbd>
                </div>
                <div className="flex items-center justify-between text-xs py-1">
                  <span className="text-slate-300 font-medium">Toggle Director Notes</span>
                  <kbd className="px-2 py-0.5 rounded bg-slate-800 border border-slate-700 font-mono text-[11px] font-bold text-amber-300">
                    N
                  </kbd>
                </div>
                <div className="flex items-center justify-between text-xs py-1">
                  <span className="text-slate-300 font-medium">Open Shortcuts Reference</span>
                  <kbd className="px-2 py-0.5 rounded bg-slate-800 border border-slate-700 font-mono text-[11px] font-bold text-amber-300">
                    ?
                  </kbd>
                </div>
                <div className="flex items-center justify-between text-xs py-1">
                  <span className="text-slate-300 font-medium">Exit Presentation / Close Modal</span>
                  <kbd className="px-2 py-0.5 rounded bg-slate-800 border border-slate-700 font-mono text-[11px] font-bold text-amber-300">
                    Esc
                  </kbd>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Footer Note */}
        <div className="pt-2 border-t border-white/5 flex items-center justify-between text-[11px] text-slate-400">
          <span>Shortcuts are automatically paused while typing in script editors or prompts.</span>
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold transition-all shadow-md shadow-indigo-600/30"
          >
            Got It (Esc)
          </button>
        </div>
      </div>
    </div>
  );
};
