import { useEffect } from "react";
import { driver } from "driver.js";
import "driver.js/dist/driver.css";
import "../styles/tour.css";
import {
  ORG_MODULE_TOUR_STEPS,
  ORG_TOUR_KEY,
} from "../constants/org-tour";

export const useOrgTour = (ready: boolean) => {
  useEffect(() => {
    if (!ready || sessionStorage.getItem(ORG_TOUR_KEY)) return;

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
        ...ORG_MODULE_TOUR_STEPS.map((step) => ({
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
        sessionStorage.setItem(ORG_TOUR_KEY, "1");
      },
    });

    const timeout = setTimeout(() => driverObj.drive(), 600);
    return () => clearTimeout(timeout);
  }, [ready]);
};
