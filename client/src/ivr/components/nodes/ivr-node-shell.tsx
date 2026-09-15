import { Handle, Position } from "@xyflow/react";
import { Flag } from "lucide-react";

export type SourceHandleDef = {
  id: string;
  label: string;
};

type IvrNodeShellProps = {
  icon: React.ReactNode;
  title: string;
  /** Clases tailwind para el color de acento del encabezado (texto/fondo). */
  accent: string;
  selected: boolean;
  children: React.ReactNode;
  /** Handles de salida (uno por cada acción "Ir a nodo" activa). */
  sourceHandles: SourceHandleDef[];
  /** Si este nodo es el de entrada (inicio de la llamada). */
  isEntry: boolean;
  /** Marca este nodo como entrada. */
  onMarkEntry: () => void;
};

/**
 * Contenedor visual común de todos los nodos IVR. Aporta la regla transversal:
 * un handle de ENTRADA arriba y N handles de SALIDA abajo (uno por cada acción
 * "Ir a nodo"), más el marcador de "nodo de entrada" del flujo.
 */
export const IvrNodeShell: React.FC<IvrNodeShellProps> = ({
  icon,
  title,
  accent,
  selected,
  children,
  sourceHandles,
  isEntry,
  onMarkEntry,
}) => (
  <div
    className={`w-72 rounded-2xl border bg-white shadow-theme-sm dark:bg-gray-900 ${
      isEntry
        ? "border-success-500 ring-2 ring-success-500/30 dark:border-success-400"
        : selected
          ? "border-brand-500 ring-2 ring-brand-500/30 dark:border-brand-400"
          : "border-gray-200 dark:border-gray-700"
    }`}
  >
    {/* Entrada (arriba) */}
    <Handle
      type="target"
      position={Position.Top}
      className="h-3! w-3! border-2! border-white! bg-gray-400! dark:border-gray-900!"
    />

    <div className={`flex items-center justify-between gap-2 rounded-t-2xl px-3 py-2 ${accent}`}>
      <div className="flex items-center gap-2">
        <span className="flex items-center">{icon}</span>
        <span className="text-sm font-semibold">{title}</span>
      </div>
      <button
        type="button"
        onClick={onMarkEntry}
        title={isEntry ? "Nodo de entrada" : "Marcar como entrada"}
        aria-label={isEntry ? "Nodo de entrada" : "Marcar como entrada"}
        className={`flex items-center gap-1 rounded-md px-1.5 py-0.5 text-[10px] font-medium transition ${
          isEntry
            ? "bg-success-500 text-white"
            : "bg-white/60 text-gray-500 hover:bg-white dark:bg-white/10 dark:text-gray-300"
        }`}
      >
        <Flag size={11} />
        {isEntry ? "Entrada" : "Inicio"}
      </button>
    </div>

    <div className="flex flex-col gap-3 p-3 text-xs">{children}</div>

    {/* Salidas (abajo) — una por acción "Ir a nodo" */}
    {sourceHandles.length > 0 && (
      <div className="relative min-h-8 border-t border-gray-100 px-3 pb-3 pt-2 dark:border-gray-800">
        <div className="flex items-end justify-around gap-1">
          {sourceHandles.map((h) => (
            <span
              key={h.id}
              className="max-w-16 truncate text-center text-[10px] font-medium text-gray-500 dark:text-gray-400"
              title={h.label}
            >
              {h.label}
            </span>
          ))}
        </div>
        {sourceHandles.map((h, i) => (
          <Handle
            key={h.id}
            id={h.id}
            type="source"
            position={Position.Bottom}
            style={{ left: `${((i + 1) / (sourceHandles.length + 1)) * 100}%` }}
            className="h-3! w-3! border-2! border-white! bg-brand-500! dark:border-gray-900!"
          />
        ))}
      </div>
    )}
  </div>
);
