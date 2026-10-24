import { useDismissedTours } from "@/hooks/use-dismissed-tours";
import { useTour } from "@/hooks/use-tour";
import { PORTFOLIO_MODULES_TOUR_KEY, PORTFOLIO_MODULES_TOUR_STEPS } from "../constants/portfolio-modules-tour";

export const usePortfolioModulesTour = (ready: boolean, visibleModuleKeys: string[]) => {
  const { isDismissed, dismiss, loading } = useDismissedTours();

  const steps = PORTFOLIO_MODULES_TOUR_STEPS.filter((step) =>
    visibleModuleKeys.some((key) => step.id === `tour-pf-module-${key}`),
  );

  // Sin módulos visibles (permisos insuficientes) no hay nada que el tour
  // pueda señalar en el grid — evita arrancarlo apuntando a tarjetas que no existen.
  useTour(ready && !loading && steps.length > 0, PORTFOLIO_MODULES_TOUR_KEY, steps, {
    dismissed: isDismissed(PORTFOLIO_MODULES_TOUR_KEY),
    onDismiss: () => dismiss(PORTFOLIO_MODULES_TOUR_KEY),
  });
};
