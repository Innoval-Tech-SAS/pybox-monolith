import { useState } from "react";
import {
  Play,
  ListTree,
  PhoneForwarded,
  Keyboard,
  GitBranch,
  PhoneOff,
  PanelLeftClose,
  PanelLeftOpen,
} from "lucide-react";
import type { IvrNodeType } from "@/ivr/types/ivr-node-types";
import { isExperimentalNode } from "@/ivr/constants/experimental-nodes";

export const NODE_DND_MIME = "application/ivr-node-type";

type PaletteItem = {
  type: IvrNodeType;
  label: string;
  description: string;
  icon: React.ReactNode;
};

const PALETTE: PaletteItem[] = [
  { type: "play", label: "Reproducir", description: "Reproduce un audio", icon: <Play size={18} /> },
  { type: "menu", label: "Menú", description: "Enruta por dígito", icon: <ListTree size={18} /> },
  {
    type: "transfer",
    label: "Transferir",
    description: "Deriva a una troncal",
    icon: <PhoneForwarded size={18} />,
  },
  {
    type: "capture",
    label: "Captura",
    description: "Captura dígitos",
    icon: <Keyboard size={18} />,
  },
  {
    type: "condition",
    label: "Condición",
    description: "Bifurca por variable",
    icon: <GitBranch size={18} />,
  },
  {
    type: "hangup",
    label: "Colgar",
    description: "Fin de la llamada",
    icon: <PhoneOff size={18} />,
  },
];

/**
 * Lo que realmente se ofrece. Los nodos experimentales se quedan definidos
 * arriba a propósito: habilitarlos cuando Helena los valide es sacarlos de
 * `EXPERIMENTAL_NODE_TYPES`, sin volver a escribir su entrada de paleta.
 */
const VISIBLE_PALETTE = PALETTE.filter((item) => !isExperimentalNode(item.type));

type IvrNodeSidebarProps = {
  /** Inserta un nodo al hacer click (posición central por defecto). */
  onAdd: (type: IvrNodeType) => void;
};

/**
 * Panel lateral colapsable con los tipos de nodo disponibles. Permite arrastrar
 * al canvas (drag & drop) o hacer click para insertar. Los nodos marcados como
 * experimentales no aparecen aquí (ver `constants/experimental-nodes.ts`).
 */
export const IvrNodeSidebar: React.FC<IvrNodeSidebarProps> = ({ onAdd }) => {
  const [collapsed, setCollapsed] = useState(false);

  const onDragStart = (e: React.DragEvent, type: IvrNodeType) => {
    e.dataTransfer.setData(NODE_DND_MIME, type);
    e.dataTransfer.effectAllowed = "move";
  };

  return (
    <aside
      className={`flex flex-col border-r border-gray-200 bg-white transition-all dark:border-gray-800 dark:bg-gray-900 ${
        collapsed ? "w-14" : "w-56"
      }`}
    >
      <div className="flex items-center justify-between border-b border-gray-100 p-3 dark:border-gray-800">
        {!collapsed && (
          <span className="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">
            Nodos
          </span>
        )}
        <button
          type="button"
          onClick={() => setCollapsed((c) => !c)}
          className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
          aria-label={collapsed ? "Expandir panel" : "Colapsar panel"}
        >
          {collapsed ? <PanelLeftOpen size={18} /> : <PanelLeftClose size={18} />}
        </button>
      </div>

      <div className="flex flex-col gap-2 p-2">
        {VISIBLE_PALETTE.map((item) => (
          <button
            key={item.type}
            type="button"
            draggable
            onDragStart={(e) => onDragStart(e, item.type)}
            onClick={() => onAdd(item.type)}
            title={collapsed ? item.label : undefined}
            className={`flex items-center gap-3 rounded-xl border border-gray-200 bg-white p-2.5 text-left transition hover:border-brand-300 hover:bg-brand-50 dark:border-gray-700 dark:bg-gray-900 dark:hover:bg-brand-500/10 ${
              collapsed ? "justify-center" : ""
            }`}
          >
            <span className="text-brand-500 dark:text-brand-400">{item.icon}</span>
            {!collapsed && (
              <span className="flex flex-col">
                <span className="text-sm font-semibold text-gray-800 dark:text-white/90">
                  {item.label}
                </span>
                <span className="text-[11px] text-gray-500 dark:text-gray-400">
                  {item.description}
                </span>
              </span>
            )}
          </button>
        ))}
      </div>

      {!collapsed && (
        <p className="mt-auto p-3 text-[11px] leading-snug text-gray-400 dark:text-gray-500">
          Arrastra un nodo al lienzo o haz click para insertarlo.
        </p>
      )}
    </aside>
  );
};
