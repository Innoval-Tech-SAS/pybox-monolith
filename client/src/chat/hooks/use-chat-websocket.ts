import { useCallback, useEffect, useRef } from "react";
import { API_URL } from "../../config/api";
import type { WsChatEvent } from "../../types/chat/chat-types";

const WS_URL = API_URL.replace(/^http/, "ws");

type Pending = { resolve: (data: unknown) => void; reject: (err: Error) => void };

export const useChatWebSocket = (onEvent: (event: WsChatEvent) => void) => {
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const onEventRef = useRef(onEvent);
  const stoppedRef = useRef(false);
  const pendingRef = useRef<Map<string, Pending>>(new Map());
  onEventRef.current = onEvent;

  const connect = useCallback(() => {
    const token = sessionStorage.getItem("accessToken");
    if (!token) return;

    const ws = new WebSocket(`${WS_URL}/chats/ws?token=${encodeURIComponent(token)}`);

    ws.onmessage = (e) => {
      try {
        const parsed = JSON.parse(e.data) as WsChatEvent & { requestId?: string };
        if (parsed.requestId) {
          const pending = pendingRef.current.get(parsed.requestId);
          if (pending) {
            pendingRef.current.delete(parsed.requestId);
            pending.resolve(parsed.data);
            return;
          }
        }
        onEventRef.current(parsed);
      } catch {
        // ignore malformed
      }
    };

    ws.onclose = () => {
      wsRef.current = null;
      if (!stoppedRef.current) {
        reconnectRef.current = setTimeout(connect, 3000);
      }
    };

    ws.onerror = () => ws.close();
    wsRef.current = ws;
  }, []);

  useEffect(() => {
    stoppedRef.current = false;
    connect();
    return () => {
      stoppedRef.current = true;
      if (reconnectRef.current) clearTimeout(reconnectRef.current);
      wsRef.current?.close();
    };
  }, [connect]);

  const send = useCallback((event: string, data: unknown) => {
    wsRef.current?.send(JSON.stringify({ event, data }));
  }, []);

  const request = useCallback(<T>(event: string, data: object): Promise<T> => {
    return new Promise<T>((resolve, reject) => {
      const ws = wsRef.current;
      if (!ws || ws.readyState !== WebSocket.OPEN) {
        reject(new Error("WebSocket not connected"));
        return;
      }
      const requestId = crypto.randomUUID();
      pendingRef.current.set(requestId, { resolve: resolve as (d: unknown) => void, reject });
      ws.send(JSON.stringify({ event, data: { ...data, requestId } }));
      setTimeout(() => {
        if (pendingRef.current.has(requestId)) {
          pendingRef.current.delete(requestId);
          reject(new Error("Request timed out"));
        }
      }, 10000);
    });
  }, []);

  return { send, request };
};
