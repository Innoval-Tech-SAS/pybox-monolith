import { useTour, type TourStep } from "@/hooks/use-tour";
import { useDismissedTours } from "@/hooks/use-dismissed-tours";
import {
  ORG_MODULE_TOUR_STEPS,
  ORG_TOUR_KEY,
} from "../constants/org-tour";

const STEPS: TourStep[] = [
  {
    id: "tour-back-btn",
    title: "Mis Empresas",
    description: "Vuelve al listado de todas tus empresas en cualquier momento desde aquí.",
    side: "bottom",
    align: "start",
  },
  {
    id: "tour-modules-grid",
    title: "Módulos de la empresa",
    description:
      "Cada tarjeta es un módulo de gestión. Iremos habilitándolos progresivamente. A continuación te explicamos cada uno.",
    align: "center",
  },
  ...ORG_MODULE_TOUR_STEPS,
];

export const useOrgTour = (ready: boolean) => {
  const { isDismissed, dismiss, loading } = useDismissedTours();

  useTour(ready && !loading, ORG_TOUR_KEY, STEPS, {
    dismissed: isDismissed(ORG_TOUR_KEY),
    onPermanentDismiss: () => dismiss(ORG_TOUR_KEY),
  });
};
