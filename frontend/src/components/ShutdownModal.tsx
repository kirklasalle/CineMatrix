import React, { useState } from 'react';
import { Power, AlertTriangle, CheckCircle, RefreshCw, X } from 'lucide-react';
import { API_BASE } from '../utils/api';

interface ShutdownModalProps {
    isOpen: boolean;
    onClose: () => void;
    onShutdownComplete: () => void;
}

export const ShutdownModal: React.FC<ShutdownModalProps> = ({
    isOpen,
    onClose,
    onShutdownComplete,
}) => {
    const [isShuttingDown, setIsShuttingDown] = useState(false);
    const [error, setError] = useState<string | null>(null);

    if (!isOpen) return null;

    const handleConfirmShutdown = async () => {
        setIsShuttingDown(true);
        setError(null);
        try {
            const resp = await fetch(`${API_BASE}/system/shutdown`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
            });
            if (resp.ok) {
                onShutdownComplete();
            } else {
                setError('Failed to initiate shutdown from server.');
                setIsShuttingDown(false);
            }
        } catch (e: any) {
            // Even if network drops because server stopped, treat as shutdown complete
            onShutdownComplete();
        }
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-in fade-in duration-200">
            <div className="glass-morphism rounded-3xl border border-rose-500/30 bg-slate-900/90 max-w-md w-full p-6 shadow-2xl shadow-rose-950/40 relative">
                <button
                    onClick={onClose}
                    disabled={isShuttingDown}
                    className="absolute top-4 right-4 p-2 text-slate-400 hover:text-white rounded-xl hover:bg-white/5 transition-colors"
                >
                    <X className="w-4 h-4" />
                </button>

                <div className="flex flex-col items-center text-center space-y-4">
                    <div className="w-14 h-14 rounded-2xl bg-rose-500/10 border border-rose-500/30 flex items-center justify-center text-rose-400">
                        <Power className="w-7 h-7" />
                    </div>

                    <div>
                        <h3 className="text-xl font-black text-white">Shut Down CineMatrix Studio?</h3>
                        <p className="text-sm text-slate-400 mt-1">
                            This will safely terminate the backend server process and close open database connections.
                        </p>
                    </div>

                    {error && (
                        <div className="w-full p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-2">
                            <AlertTriangle className="w-4 h-4 shrink-0" />
                            <span>{error}</span>
                        </div>
                    )}

                    <div className="w-full p-3 rounded-2xl bg-slate-950/60 border border-white/5 text-left text-xs text-slate-400 space-y-1.5">
                        <div className="flex items-center gap-2 text-slate-300 font-bold">
                            <CheckCircle className="w-3.5 h-3.5 text-emerald-400" />
                            <span>All projects &amp; frames are saved in SQLite</span>
                        </div>
                        <p className="text-[11px] text-slate-500 pl-5.5">
                            You can safely restart anytime by running <code className="text-indigo-300">start_cinematrix.bat</code>.
                        </p>
                    </div>

                    <div className="flex items-center gap-3 w-full pt-2">
                        <button
                            type="button"
                            onClick={onClose}
                            disabled={isShuttingDown}
                            className="flex-1 py-3 px-4 rounded-xl border border-white/10 text-slate-300 hover:bg-white/5 font-bold text-sm transition-colors"
                        >
                            Cancel
                        </button>

                        <button
                            type="button"
                            onClick={handleConfirmShutdown}
                            disabled={isShuttingDown}
                            className="flex-1 py-3 px-4 rounded-xl bg-rose-600 hover:bg-rose-700 text-white font-bold text-sm transition-all shadow-lg shadow-rose-600/30 flex items-center justify-center gap-2"
                        >
                            {isShuttingDown ? (
                                <>
                                    <RefreshCw className="w-4 h-4 animate-spin" />
                                    <span>Stopping...</span>
                                </>
                            ) : (
                                <>
                                    <Power className="w-4 h-4" />
                                    <span>Shut Down</span>
                                </>
                            )}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};
