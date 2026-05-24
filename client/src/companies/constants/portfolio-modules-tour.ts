import type { TourStep } from "@/hooks/use-tour";

export const PORTFOLIO_MODULES_TOUR_KEY = "portfolio-modules-tour-seen";

export const PORTFOLIO_MODULES_TOUR_STEPS: TourStep[] = [
  {
    id: "tour-pf-module-debtors",
    title: "Clientes",
    description:
      "Visualiza y segmenta todos los clientes de este portafolio. Analiza indicadores de mora, pagos y comportamiento de cada deudor.",
    side: "top",
    align: "center",
  },
  {
    id: "tour-pf-module-portfolio-update-strict",
    title: "Actualizar clientes",
    description:
      "Sube un CSV para actualizar la información de clientes que ya existen en este portafolio. Solo modifica registros existentes, sin agregar nuevos.",
    side: "top",
    align: "center",
  },
  {
    id: "tour-pf-module-portfolio-update-append",
    title: "Subir nuevos clientes",
    description:
      "Agrega clientes al portafolio mediante un CSV. También actualiza los ya existentes en la misma carga.",
    side: "top",
    align: "center",
  },
  {
    id: "tour-pf-module-messages",
    title: "Comunicaciones",
    description:
      "Diseña flujos de mensajería, lanza campañas masivas y administra plantillas para contactar a tus clientes de forma eficiente.",
    side: "top",
    align: "center",
  },
  {
    id: "tour-pf-module-messages-calendar",
    title: "Calendario de Comunicaciones",
    description:
      "Consulta en vista de calendario todas las campañas programadas, su estado y los envíos realizados por fecha.",
    side: "top",
    align: "center",
  },
  {
    id: "tour-pf-module-upcoming",
    title: "Próximos Módulos",
    description:
      "Seguimos construyendo. Pronto encontrarás aquí nuevas herramientas operativas para mejorar tu gestión de cartera.",
    side: "top",
    align: "center",
  },
];
