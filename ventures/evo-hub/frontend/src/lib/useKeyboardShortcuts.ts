/**
 * Global keyboard shortcuts for EVO-DASH.
 * Phase 3.3: Keyboard shortcuts (g, t, c, /, h)
 */
import { useEffect, useCallback } from 'react';

export interface ShortcutConfig {
  onGenerate?: () => void;
  onTest?: () => void;
  onCouncil?: () => void;
  onSearch?: () => void;
  onHelp?: () => void;
  onThemeToggle?: () => void;
}

export function useKeyboardShortcuts(config: ShortcutConfig) {
  const handleKey = useCallback((e: KeyboardEvent) => {
    // Ignore if user is typing in an input/textarea
    const target = e.target as HTMLElement;
    if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || target.isContentEditable) {
      return;
    }

    switch (e.key.toLowerCase()) {
      case 'g':
        e.preventDefault();
        config.onGenerate?.();
        break;
      case 't':
        e.preventDefault();
        config.onTest?.();
        break;
      case 'c':
        e.preventDefault();
        config.onCouncil?.();
        break;
      case '/':
        e.preventDefault();
        config.onSearch?.();
        break;
      case '?':
      case 'h':
        if (e.shiftKey || e.key === '?') {
          e.preventDefault();
          config.onHelp?.();
        }
        break;
      case 'd':
        if (e.altKey) {
          e.preventDefault();
          config.onThemeToggle?.();
        }
        break;
    }
  }, [config]);

  useEffect(() => {
    window.addEventListener('keydown', handleKey);
    return () => window.removeEventListener('keydown', handleKey);
  }, [handleKey]);
}
