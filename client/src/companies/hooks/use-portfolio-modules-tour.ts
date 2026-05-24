import { useDismissedTours } from "@/hooks/use-dismissed-tours";
import { useTour } from "@/hooks/use-tour";
import { PORTFOLIO_MODULES_TOUR_KEY, PORTFOLIO_MODULES_TOUR_STEPS } from "../constants/portfolio-modules-tour";

export const usePortfolioModulesTour = (ready: boolean) => {
  const { isDismissed, dismiss, loading } = useDismissedTours();
  useTour(ready && !loading, PORTFOLIO_MODULES_TOUR_KEY, PORTFOLIO_MODULES_TOUR_STEPS, {
    dismissed: isDismissed(PORTFOLIO_MODULES_TOUR_KEY),
    onPermanentDismiss: () => dismiss(PORTFOLIO_MODULES_TOUR_KEY),
  });
};
