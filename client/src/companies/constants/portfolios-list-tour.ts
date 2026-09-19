import type { TourStep } from "@/hooks/use-tour";

export const PORTFOLIOS_LIST_TOUR_KEY = "portfolios-list-tour-seen";

export const PORTFOLIOS_LIST_TOUR_STEPS: TourStep[] = [
  {
    id: "tour-create-portfolio",
    title: "Crea tu primer portafolio",
    description:
      "Haz clic aquí para cargar un nuevo portafolio. Sube un CSV con los datos de tus clientes y comienza a gestionar tu cartera.",
    side: "right",
    align: "start",
  },
];
