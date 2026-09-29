import { useEffect } from 'react';

export type StudioView = 
  | 'home' 
  | 'config' 
  | 'upload' 
  | 'gallery' 
  | 'characters' 
  | 'story_doctor' 
  | 'table_read' 
  | 'graphic_novel' 
  | 'examples';

interface UseNleKeyboardShortcutsOptions {
  currentView: StudioView;
  onNavigate: (view: StudioView) => void;
  onToggleShortcutsModal?: () => void;
  onPlayPause?: () => void;
  onStepForward?: () => void;
  onStepBackward?: () => void;
  onToggleFullscreen?: () => void;
  enabled?: boolean;
}

export function useNleKeyboardShortcuts({
  currentView,
  onNavigate,
  onToggleShortcutsModal,
  onPlayPause,
  onStepForward,
  onStepBackward,
  onToggleFullscreen,
  enabled = true,
}: UseNleKeyboardShortcutsOptions) {
  useEffect(() => {
    if (!enabled) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      // Ignore if user is currently typing in an input, textarea, or contentEditable element
      const target = e.target as HTMLElement | null;
      if (
        target &&
        (target.tagName === 'INPUT' ||
          target.tagName === 'TEXTAREA' ||
          target.tagName === 'SELECT' ||
          target.isContentEditable)
      ) {
        // Exception: Escape key can blur active input
        if (e.key === 'Escape') {
          target.blur();
        }
        return;
      }

      // Modifier key guard: Don't trigger if Ctrl/Cmd or Alt is held
      if (e.ctrlKey || e.metaKey || e.altKey) {
        return;
      }

      // 1. Studio Navigation (1-9)
      switch (e.key) {
        case '1':
          e.preventDefault();
          onNavigate('home');
          return;
        case '2':
          e.preventDefault();
          onNavigate('upload');
          return;
        case '3':
          e.preventDefault();
          onNavigate('gallery');
          return;
        case '4':
          e.preventDefault();
          onNavigate('characters');
          return;
        case '5':
          e.preventDefault();
          onNavigate('table_read');
          return;
        case '6':
          e.preventDefault();
          onNavigate('story_doctor');
          return;
        case '7':
          e.preventDefault();
          onNavigate('graphic_novel');
          return;
        case '8':
          e.preventDefault();
          onNavigate('examples');
          return;
        case '9':
          e.preventDefault();
          onNavigate('config');
          return;
      }

      // 2. Help / Shortcuts Overlay ('?' or '/')
      if (e.key === '?' || (e.shiftKey && e.key === '/')) {
        e.preventDefault();
        onToggleShortcutsModal?.();
        return;
      }

      // 3. Fullscreen ('f' or 'F')
      if (e.key.toLowerCase() === 'f') {
        e.preventDefault();
        onToggleFullscreen?.();
        return;
      }

      // 4. J-K-L NLE Scrubbing & Playback
      // Spacebar: Play/Pause Audition
      if (e.code === 'Space' || e.key === ' ') {
        if (onPlayPause) {
          e.preventDefault();
          onPlayPause();
        }
        return;
      }

      // 'L' or Right Arrow: Step/Play forward
      if (e.key.toLowerCase() === 'l' || e.key === 'ArrowRight') {
        if (onStepForward) {
          e.preventDefault();
          onStepForward();
        }
        return;
      }

      // 'J' or Left Arrow: Step/Play backward
      if (e.key.toLowerCase() === 'j' || e.key === 'ArrowLeft') {
        if (onStepBackward) {
          e.preventDefault();
          onStepBackward();
        }
        return;
      }

      // 'K': Pause
      if (e.key.toLowerCase() === 'k') {
        if (onPlayPause) {
          e.preventDefault();
          onPlayPause();
        }
        return;
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [
    enabled,
    currentView,
    onNavigate,
    onToggleShortcutsModal,
    onPlayPause,
    onStepForward,
    onStepBackward,
    onToggleFullscreen,
  ]);
}
