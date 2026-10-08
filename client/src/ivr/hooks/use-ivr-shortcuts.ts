import { useEffect } from "react";

type ShortcutHandlers = {
  onDuplicate: () => void;
  onUndo: () => void;
  onRedo: () => void;
  onSelectAll: () => void;
};

const isEditableTarget = (target: EventTarget | null): boolean => {
  const el = target as HTMLElement | null;
  if (!el) return false;
  const tag = el.tagName;
  return (
    tag === "INPUT" ||
    tag === "TEXTAREA" ||
    tag === "SELECT" ||
    el.isContentEditable
  );
};

/**
 * Atajos de teclado del diseñador IVR (los que no cubre React Flow de forma
 * nativa). Del/Supr y la selección múltiple con Shift los maneja <ReactFlow>.
 * Se ignoran cuando el foco está en un campo editable de la config inline.
 */
export const useIvrShortcuts = ({
  onDuplicate,
  onUndo,
  onRedo,
  onSelectAll,
}: ShortcutHandlers) => {
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      const mod = e.ctrlKey || e.metaKey;
      if (!mod || isEditableTarget(e.target)) return;

      const key = e.key.toLowerCase();
      if (key === "d") {
        e.preventDefault();
        onDuplicate();
      } else if (key === "z" && !e.shiftKey) {
        e.preventDefault();
        onUndo();
      } else if (key === "y" || (key === "z" && e.shiftKey)) {
        e.preventDefault();
        onRedo();
      } else if (key === "a") {
        e.preventDefault();
        onSelectAll();
      }
    };

    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [onDuplicate, onUndo, onRedo, onSelectAll]);
};
