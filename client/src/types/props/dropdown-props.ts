import type { RefObject } from "react";

export interface DropdownProps {
  isOpen: boolean;
  onClose: () => void;
  children: React.ReactNode;
  className?: string;
  /**
   * Ref del botón disparador. Si se pasa, el panel se renderiza en un portal
   * (position: fixed) anclado al botón para no quedar recortado por ancestros
   * con overflow. Si se omite, se usa el posicionamiento inline heredado.
   */
  triggerRef?: RefObject<HTMLElement | null>;
  /** Alineación horizontal en modo portal. Por defecto "right". */
  align?: "left" | "right";
}
