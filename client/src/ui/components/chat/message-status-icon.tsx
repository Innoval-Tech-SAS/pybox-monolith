import React from "react";
import type { MessageStatusIconProps } from "@/types/props/message-bubble-props";

/** Ícono de estado de entrega (enviado/entregado/leído) para burbujas de mensaje propias. */
export const StatusIcon: React.FC<MessageStatusIconProps> = ({ status }) => {
  if (status === "read") return <span className="text-brand-500 text-theme-xs">✓✓</span>;
  if (status === "delivered") return <span className="text-gray-400 text-theme-xs">✓✓</span>;
  return <span className="text-gray-400 text-theme-xs">✓</span>;
};
