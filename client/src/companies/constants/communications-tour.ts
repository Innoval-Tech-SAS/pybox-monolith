import type { TourStep } from "@/hooks/use-tour";

export const COMMUNICATIONS_TOUR_KEY = "communications-modules-tour-seen";

// El orden debe seguir el de COMMUNICATIONS_MODULES: los pasos se filtran
// contra los módulos visibles, así que un módulo sin paso queda fuera del tour.
export const COMMUNICATIONS_TOUR_STEPS: TourStep[] = [
  {
    id: "tour-comm-module-segments",
    title: "Segmentos",
    description:
      "Crea listas dinámicas de deudores y sus relaciones. Filtra, une tablas y exporta el resultado para usarlo en tus campañas.",
    side: "top",
    align: "center",
  },
  {
    id: "tour-comm-module-templates",
    title: "Plantillas",
    description:
      "Diseña y gestiona las plantillas de email y SMS que reutilizarás en tus envíos.",
    side: "top",
    align: "center",
  },
  {
    id: "tour-comm-module-campaigns",
    title: "Campañas",
    description:
      "Lanza y haz seguimiento a campañas masivas de mensajería sobre los segmentos que definiste.",
    side: "top",
    align: "center",
  },
  {
    id: "tour-comm-module-bulk-send",
    title: "Envío masivo",
    description:
      "Envía mensajes masivos directamente desde un archivo CSV o Excel, sin depender de un segmento.",
    side: "top",
    align: "center",
  },
];
