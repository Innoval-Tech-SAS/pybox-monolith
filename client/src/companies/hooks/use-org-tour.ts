import { useTour, type TourStep } from "@/hooks/use-tour";
import { useDismissedTours } from "@/hooks/use-dismissed-tours";
import {
  ORG_MODULE_TOUR_STEPS,
  ORG_TOUR_KEY,
} from "../constants/org-tour";

export const useOrgTour = (ready: boolean, visibleModuleKeys: string[]) => {
  const { isDismissed, dismiss, loading } = useDismissedTours();

  const moduleSteps = ORG_MODULE_TOUR_STEPS.filter((step) =>
    visibleModuleKeys.some((key) => step.id === `tour-module-${key}`),
  );

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
    ...moduleSteps,
  ];

  // Sin módulos visibles (permisos insuficientes) no hay nada que el tour
  // pueda señalar en el grid — evita arrancarlo apuntando a una tarjeta vacía.
  useTour(ready && !loading && moduleSteps.length > 0, ORG_TOUR_KEY, STEPS, {
    dismissed: isDismissed(ORG_TOUR_KEY),
    onDismiss: () => dismiss(ORG_TOUR_KEY),
  });
};
