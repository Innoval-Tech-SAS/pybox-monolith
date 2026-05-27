import { useCallback, useEffect, useRef } from "react";
import { API_URL } from "../../config/api";
import type { WsChatEvent } from "../../types/chat/chat-types";

const WS_URL = API_URL.replace(/^http/, "ws");

export const useChatWebSocket = (
  onEvent: (event: WsChatEvent) => void,
) => {
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const onEventRef = useRef(onEvent);
  onEventRef.current = onEvent;

  const connect = useCallback(() => {
    const token = sessionStorage.getItem("accessToken");
    if (!token) return;

    const ws = new WebSocket(`${WS_URL}/chats/ws?token=${encodeURIComponent(token)}`);

    ws.onmessage = (e) => {
      try {
        const parsed = JSON.parse(e.data) as WsChatEvent;
        onEventRef.current(parsed);
      } catch {
        // ignore malformed
      }
    };

    ws.onclose = () => {
      wsRef.current = null;
      reconnectRef.current = setTimeout(connect, 3000);
    };

    ws.onerror = () => ws.close();

    wsRef.current = ws;
  }, []);

  useEffect(() => {
    connect();
    return () => {
      if (reconnectRef.current) clearTimeout(reconnectRef.current);
      wsRef.current?.close();
    };
  }, [connect]);
};
