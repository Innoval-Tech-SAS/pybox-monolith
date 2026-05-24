import type { TourStep } from "@/hooks/use-tour";

export const PORTFOLIOS_LIST_TOUR_KEY = "portfolios-list-tour-seen";

export const PORTFOLIOS_LIST_TOUR_STEPS: TourStep[] = [
  {
    title: "Mis Portafolios",
    description:
      "Aquí encontrarás todos los portafolios de clientes de tu organización. Cada portafolio agrupa una cartera con sus herramientas de gestión y comunicaciones.",
  },
  {
    id: "tour-create-portfolio",
    title: "Crea tu primer portafolio",
    description:
      "Haz clic aquí para cargar un nuevo portafolio. Podrás subir un CSV con los datos de tus clientes y comenzar a gestionar tu cartera.",
    side: "right",
    align: "start",
  },
];
