import { Spinner } from "@/ui/components/loader/spinner";
import type { WompiChallengePanelProps } from "@/credits/types/wompi-challenge-panel-props";

/**
 * Reto 3DS (tarjeta) o espera de confirmación (Nequi push / redirect de banco). El
 * HTML del iframe ya viene decodificado desde el backend (ver `WompiGateway`, skill
 * `wompi-gateway` Paso 6) -- Wompi exige mostrar la marca Mastercard mientras se
 * resuelve el reto.
 */
export const WompiChallengePanel: React.FC<WompiChallengePanelProps> = ({ challengeHtml, statusLabel }) => (
  <div className="flex flex-col items-center gap-4 rounded-lg border border-gray-200 bg-gray-50 p-5 text-center dark:border-gray-800 dark:bg-white/3">
    {challengeHtml ? (
      <>
        <p className="text-xs font-medium text-gray-500 dark:text-gray-400">Mastercard ID Check</p>
        <iframe
          title="Autenticación 3D Secure"
          srcDoc={challengeHtml}
          className="h-64 w-full rounded-lg border border-gray-200 bg-white dark:border-gray-800"
        />
      </>
    ) : (
      <Spinner size="sm" tone="brand" />
    )}
    <p className="text-sm text-gray-700 dark:text-gray-300">{statusLabel}</p>
  </div>
);
