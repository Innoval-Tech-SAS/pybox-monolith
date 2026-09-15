import { useCallback, useEffect, useRef } from "react";
import { API_URL } from "../../config/api";
import type { WsWhatsAppEvent } from "../types/whatsapp-chat-types";

const WS_URL = API_URL.replace(/^http/, "ws");

type Pending = { resolve: (data: unknown) => void; reject: (err: Error) => void };

export const useWhatsAppWebSocket = (onEvent: (event: WsWhatsAppEvent) => void) => {
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const onEventRef = useRef(onEvent);
  const stoppedRef = useRef(false);
  const pendingRef = useRef<Map<string, Pending>>(new Map());
  const queueRef = useRef<string[]>([]);
  onEventRef.current = onEvent;

  // Abrir el socket es asíncrono: al montar, quien llame `request` lo hace con el
  // socket todavía en CONNECTING. Los frames se encolan y salen en cuanto abre —
  // esto también cubre el hueco entre un onclose y su reconexión.
  const flush = useCallback(() => {
    const ws = wsRef.current;
    if (!ws || ws.readyState !== WebSocket.OPEN) return;
    const queued = queueRef.current;
    queueRef.current = [];
    for (const frame of queued) ws.send(frame);
  }, []);

  const enqueue = useCallback(
    (frame: string) => {
      queueRef.current.push(frame);
      flush();
    },
    [flush],
  );

  const connect = useCallback(() => {
    if (!sessionStorage.getItem("user")) return;

    // El access token vive en una cookie httpOnly; el navegador la adjunta sola
    // en el handshake del WebSocket (mismo sitio), no hace falta pasarla por query.
    const ws = new WebSocket(`${WS_URL}/whatsapp/chats/ws`);

    ws.onopen = () => flush();

    ws.onmessage = (e) => {
      try {
        const parsed = JSON.parse(e.data) as WsWhatsAppEvent & { requestId?: string };
        if (parsed.requestId) {
          const pending = pendingRef.current.get(parsed.requestId);
          if (pending) {
            pendingRef.current.delete(parsed.requestId);
            if (parsed.event === "error") {
              pending.reject(new Error(parsed.data.detail));
            } else {
              pending.resolve(parsed.data);
            }
            return;
          }
        }
        onEventRef.current(parsed);
      } catch {
        // ignore malformed
      }
    };

    ws.onclose = (event) => {
      wsRef.current = null;
      // 1008 = server rechazó la conexión (límite por usuario) — no reconectar en loop
      if (!stoppedRef.current && event.code !== 1008) {
        reconnectRef.current = setTimeout(connect, 3000);
      }
    };

    ws.onerror = () => ws.close();
    wsRef.current = ws;
  }, [flush]);

  useEffect(() => {
    stoppedRef.current = false;
    connect();
    return () => {
      stoppedRef.current = true;
      if (reconnectRef.current) clearTimeout(reconnectRef.current);
      wsRef.current?.close();
    };
  }, [connect]);

  const send = useCallback(
    (event: string, data: unknown) => {
      enqueue(JSON.stringify({ event, data }));
    },
    [enqueue],
  );

  const request = useCallback(
    <T>(event: string, data: object): Promise<T> => {
      return new Promise<T>((resolve, reject) => {
        const requestId = crypto.randomUUID();
        pendingRef.current.set(requestId, { resolve: resolve as (d: unknown) => void, reject });
        enqueue(JSON.stringify({ event, data: { ...data, requestId } }));
        setTimeout(() => {
          if (pendingRef.current.has(requestId)) {
            pendingRef.current.delete(requestId);
            reject(new Error("Request timed out"));
          }
        }, 10000);
      });
    },
    [enqueue],
  );

  return { send, request };
};
