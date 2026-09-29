"""Registro en memoria de las conexiones WebSocket activas de chats de WhatsApp."""

from app_platform.chats.websocket.connection_manager import ChatConnectionManager

# Instancia independiente del chat interno (app_platform.chats) — mismo mecanismo
# de conexiones por usuario, pero no se mezcla el tráfico de chat interno con el de
# WhatsApp.
whatsapp_ws_manager = ChatConnectionManager()
