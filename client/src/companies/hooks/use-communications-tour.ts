import { useDismissedTours } from "@/hooks/use-dismissed-tours";
import { useTour } from "@/hooks/use-tour";
import { COMMUNICATIONS_TOUR_KEY, COMMUNICATIONS_TOUR_STEPS } from "../constants/communications-tour";

export const useCommunicationsTour = (ready: boolean, visibleModuleKeys: string[]) => {
  const { isDismissed, dismiss, loading } = useDismissedTours();

  const steps = COMMUNICATIONS_TOUR_STEPS.filter((step) =>
    visibleModuleKeys.some((key) => step.id === `tour-comm-module-${key}`),
  );

  // Sin módulos visibles (permisos insuficientes) no hay nada que el tour
  // pueda señalar en el grid — evita arrancarlo apuntando a tarjetas que no existen.
  useTour(ready && !loading && steps.length > 0, COMMUNICATIONS_TOUR_KEY, steps, {
    dismissed: isDismissed(COMMUNICATIONS_TOUR_KEY),
    onDismiss: () => dismiss(COMMUNICATIONS_TOUR_KEY),
  });
};
