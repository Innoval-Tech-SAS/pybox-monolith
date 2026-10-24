import type { TourStep } from "@/hooks/use-tour";

export const ORG_TOUR_KEY = "org-modules-tour-seen";

// El orden debe seguir el de ORG_MODULES: los pasos se filtran contra los
// módulos visibles, así que un módulo sin paso queda fuera del tour.
export const ORG_MODULE_TOUR_STEPS: TourStep[] = [
  {
    id: "tour-module-portfolios",
    title: "Portafolios",
    description:
      "Visualiza y gestiona todos los portafolios de clientes de la empresa. Aquí podrás filtrar, buscar y hacer seguimiento a cada cartera.",
  },
  {
    id: "tour-module-users",
    title: "Usuarios",
    description:
      "Consulta el listado de usuarios vinculados a esta empresa, su rol y estado de acceso.",
  },
  {
    id: "tour-module-payment-methods",
    title: "Métodos de Pago",
    description:
      "Administra los medios de pago habilitados para la empresa. Registra nuevos métodos y edita los existentes según tu operación.",
  },
  {
    id: "tour-module-billing",
    title: "Facturación",
    description:
      "Consulta las facturas de la empresa, revisa su estado y realiza los pagos pendientes en línea.",
  },
  {
    id: "tour-module-reports",
    title: "Reportes",
    description:
      "Genera y consulta reportes de gestión sobre el rendimiento de tus portafolios, pagos recibidos y actividad de clientes.",
  },
  {
    id: "tour-module-settings",
    title: "Configuración",
    description:
      "Edita el nombre, país, documentos fiscales y mercantiles de la empresa. Mantén la información legal siempre actualizada.",
  },
];
