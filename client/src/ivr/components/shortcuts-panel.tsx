import { Modal } from "@/ui/components/modal/modal";

type ShortcutsPanelProps = {
  isOpen: boolean;
  onClose: () => void;
};

const Kbd: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <kbd className="inline-flex min-w-7 items-center justify-center rounded-md border border-gray-300 bg-gray-50 px-2 py-1 text-xs font-semibold text-gray-700 shadow-theme-xs dark:border-gray-600 dark:bg-gray-800 dark:text-gray-200">
    {children}
  </kbd>
);

type Shortcut = {
  keys: string[];
  description: string;
};

const SHORTCUTS: Shortcut[] = [
  { keys: ["Supr"], description: "Eliminar el/los nodo(s) seleccionados" },
  { keys: ["Shift", "arrastrar"], description: "Selección múltiple (marquee)" },
  { keys: ["Ctrl", "D"], description: "Duplicar la selección" },
  { keys: ["Ctrl", "Z"], description: "Deshacer" },
  { keys: ["Ctrl", "Y"], description: "Rehacer" },
  { keys: ["Ctrl", "A"], description: "Seleccionar todos los nodos" },
  { keys: ["Arrastrar lienzo"], description: "Desplazar el lienzo (pan)" },
  { keys: ["Rueda"], description: "Zoom in / zoom out" },
];

/** Panel visual de atajos de teclado del diseñador IVR. */
export const ShortcutsPanel: React.FC<ShortcutsPanelProps> = ({ isOpen, onClose }) => (
  <Modal isOpen={isOpen} onClose={onClose} className="m-4 max-w-lg p-6">
    <h4 className="mb-1 text-lg font-semibold text-gray-800 dark:text-white/90">
      Atajos de teclado
    </h4>
    <p className="mb-5 text-sm text-gray-500 dark:text-gray-400">
      Acelera el diseño del flujo con estas combinaciones.
    </p>

    <ul className="flex flex-col divide-y divide-gray-100 dark:divide-gray-800">
      {SHORTCUTS.map((s) => (
        <li key={s.description} className="flex items-center justify-between gap-4 py-3">
          <span className="text-sm text-gray-600 dark:text-gray-300">{s.description}</span>
          <span className="flex flex-shrink-0 items-center gap-1">
            {s.keys.map((k, i) => (
              <span key={k} className="flex items-center gap-1">
                {i > 0 && <span className="text-xs text-gray-400">+</span>}
                <Kbd>{k}</Kbd>
              </span>
            ))}
          </span>
        </li>
      ))}
    </ul>
  </Modal>
);
