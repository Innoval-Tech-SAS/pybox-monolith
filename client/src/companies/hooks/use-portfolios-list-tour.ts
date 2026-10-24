import { useDismissedTours } from "@/hooks/use-dismissed-tours";
import { useTour } from "@/hooks/use-tour";
import { PORTFOLIOS_LIST_TOUR_KEY, PORTFOLIOS_LIST_TOUR_STEPS } from "../constants/portfolios-list-tour";

export const usePortfoliosListTour = (ready: boolean) => {
  const { isDismissed, dismiss, loading } = useDismissedTours();
  useTour(ready && !loading, PORTFOLIOS_LIST_TOUR_KEY, PORTFOLIOS_LIST_TOUR_STEPS, {
    dismissed: isDismissed(PORTFOLIOS_LIST_TOUR_KEY),
    onDismiss: () => dismiss(PORTFOLIOS_LIST_TOUR_KEY),
  });
};
