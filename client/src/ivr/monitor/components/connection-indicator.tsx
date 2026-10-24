import { RefreshCw, Wifi, WifiOff } from "lucide-react";

interface ConnectionIndicatorProps {
  connected: boolean;
  onRefresh: () => void;
}

/**
 * Sin este indicador, un stream caído se ve exactamente igual que una campaña
 * sin actividad: la tabla simplemente deja de moverse.
 */
export const ConnectionIndicator: React.FC<ConnectionIndicatorProps> = ({
  connected,
  onRefresh,
}) => (
  <div className="flex items-center gap-2">
    <span
      className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-medium ${
        connected
          ? "bg-success-50 text-success-600 dark:bg-success-500/15 dark:text-success-400"
          : "bg-warning-50 text-warning-600 dark:bg-warning-500/15 dark:text-warning-400"
      }`}
    >
      {connected ? <Wifi size={13} /> : <WifiOff size={13} />}
      {connected ? "En vivo" : "Reconectando…"}
    </span>
    <button
      type="button"
      onClick={onRefresh}
      title="Actualizar"
      className="rounded-lg p-1.5 text-gray-400 hover:bg-gray-100 hover:text-gray-600 dark:hover:bg-gray-800 dark:hover:text-gray-200"
    >
      <RefreshCw size={15} />
    </button>
  </div>
);
