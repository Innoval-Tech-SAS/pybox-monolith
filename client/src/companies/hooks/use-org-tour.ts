import { useEffect } from "react";
import { driver } from "driver.js";
import "driver.js/dist/driver.css";
import "../styles/tour.css";

const TOUR_KEY = "org-modules-tour-seen";

const MODULE_STEPS = [
  {
    id: "tour-module-portfolios",
    title: "Mis Portafolios",
    description:
      "Visualiza y gestiona todos los portafolios de clientes de la organización. Aquí podrás filtrar, buscar y hacer seguimiento a cada cartera.",
  },
  {
    id: "tour-module-portfolios-create",
    title: "Crear Portafolio",
    description:
      "Carga un nuevo portafolio mediante un archivo CSV con los datos de tus clientes o deudores. El sistema validará el formato automáticamente.",
  },
  {
    id: "tour-module-payment-methods",
    title: "Métodos de Pago",
    description:
      "Configura los canales de pago habilitados para la organización — transferencias, PSE, efectivo u otros según tu operación. (Próximamente)",
  },
  {
    id: "tour-module-users",
    title: "Usuarios",
    description:
      "Consulta el listado de usuarios vinculados a esta organización, su rol y estado de acceso.",
  },
  {
    id: "tour-module-users-add",
    title: "Crear Usuario",
    description:
      "Invita o registra un nuevo usuario y asígnale un rol dentro de la organización. (Próximamente)",
  },
  {
    id: "tour-module-reports",
    title: "Reportes",
    description:
      "Genera reportes de gestión sobre el rendimiento de tus portafolios, pagos recibidos y actividad de clientes. (Próximamente)",
  },
  {
    id: "tour-module-roles",
    title: "Roles",
    description:
      "Administra los permisos de cada perfil de usuario dentro de la organización. Define qué puede ver y hacer cada rol. (Próximamente)",
  },
  {
    id: "tour-module-settings",
    title: "Configuración",
    description:
      "Edita el nombre, país, documentos fiscales y mercantiles de la organización. Mantén la información legal siempre actualizada.",
  },
];

export const useOrgTour = (ready: boolean) => {
  useEffect(() => {
    if (!ready || sessionStorage.getItem(TOUR_KEY)) return;

    const driverObj = driver({
      showProgress: true,
      popoverClass: "driverjs-theme",
      nextBtnText: "Siguiente →",
      prevBtnText: "← Anterior",
      doneBtnText: "¡Entendido!",
      steps: [
        {
          element: "#tour-back-btn",
          popover: {
            title: "Mis Empresas",
            description: "Vuelve al listado de todas tus empresas en cualquier momento desde aquí.",
            side: "bottom",
            align: "start",
          },
        },
        {
          element: "#tour-modules-grid",
          popover: {
            title: "Módulos de la organización",
            description:
              "Cada tarjeta es un módulo de gestión. Iremos habilitándolos progresivamente. A continuación te explicamos cada uno.",
            side: "top",
            align: "center",
          },
        },
        ...MODULE_STEPS.map((step) => ({
          element: `#${step.id}`,
          popover: {
            title: step.title,
            description: step.description,
            side: "top" as const,
            align: "center" as const,
          },
        })),
      ],
      onDestroyed: () => {
        sessionStorage.setItem(TOUR_KEY, "1");
      },
    });

    const timeout = setTimeout(() => driverObj.drive(), 600);
    return () => clearTimeout(timeout);
  }, [ready]);
};
