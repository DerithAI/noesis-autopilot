/**
 * WebSocket hook for real-time generation progress.
 * Phase 3.2: Real-time WebSocket progress on generation
 */
import { useEffect, useRef, useState, useCallback } from 'react';

export interface GenerationProgress {
  type: 'generation';
  seed: string;
  stage: 'starting' | 'research' | 'architect' | 'implement' | 'test' | 'deploy' | 'complete' | 'failed' | 'timeout' | 'error';
  progress: number;
}

export interface StatusUpdate {
  type: 'status';
  data: {
    evo_hub: boolean;
    lumen: boolean;
    ollama: boolean;
    ventures: number;
  };
}

export type WsMessage = GenerationProgress | StatusUpdate;

const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

export function useWebSocket() {
  const wsRef = useRef<WebSocket | null>(null);
  const [connected, setConnected] = useState(false);
  const [generation, setGeneration] = useState<GenerationProgress | null>(null);
  const [status, setStatus] = useState<StatusUpdate['data'] | null>(null);

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    const wsUrl = API_BASE.replace(/^http/, 'ws') + '/ws/dashboard';
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => setConnected(true);
    ws.onclose = () => setConnected(false);
    ws.onerror = () => setConnected(false);

    ws.onmessage = (event) => {
      try {
        const msg: WsMessage = JSON.parse(event.data);
        if (msg.type === 'generation') {
          setGeneration(msg);
        } else if (msg.type === 'status') {
          setStatus(msg.data);
        }
      } catch {
        // Ignore malformed messages
      }
    };
  }, []);

  const disconnect = useCallback(() => {
    wsRef.current?.close();
    wsRef.current = null;
    setConnected(false);
  }, []);

  useEffect(() => {
    connect();
    return () => disconnect();
  }, [connect, disconnect]);

  return { connected, generation, status, reconnect: connect };
}
