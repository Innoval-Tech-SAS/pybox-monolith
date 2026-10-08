import { useEffect } from "react";
import { driver, type Config } from "driver.js";

export interface TourStep {
  id?: string;
  title: string;
  description: string;
  side?: "top" | "right" | "bottom" | "left";
  align?: "start" | "center" | "end";
}

type TourOptions = Partial<
  Pick<Config, "nextBtnText" | "prevBtnText" | "doneBtnText" | "popoverClass" | "showProgress">
> & {
  dismissed?: boolean;
  onDismiss?: () => void;
};

const DEFAULTS = {
  showProgress: true,
  popoverClass: "driverjs-theme",
  nextBtnText: "Siguiente →",
  prevBtnText: "← Anterior",
  doneBtnText: "¡Entendido!",
};

export const useTour = (
  ready: boolean,
  storageKey: string,
  steps: TourStep[],
  options?: TourOptions,
) => {
  const { dismissed, onDismiss, ...driverOptions } = options ?? {};

  useEffect(() => {
    if (!ready || dismissed || sessionStorage.getItem(storageKey)) return;

    const driverObj = driver({
      ...DEFAULTS,
      ...driverOptions,
      steps: steps.map((step) => ({
        ...(step.id ? { element: `#${step.id}` } : {}),
        popover: {
          title: step.title,
          description: step.description,
          side: step.side ?? "top",
          align: step.align ?? "center",
        },
      })),
      // driver.js dispara esto para CUALQUIER cierre (botón "¡Entendido!", X, Esc,
      // click afuera) — no solo al completar todos los pasos. Antes solo el botón
      // "No volver a mostrar" secundario llamaba a onDismiss; cerrar con la acción
      // obvia (el botón azul) solo marcaba sessionStorage y nunca persistía en el
      // backend, así que el tour volvía a aparecer en la siguiente sesión aunque el
      // usuario ya lo hubiera "cerrado". Unificar aquí hace que cualquier cierre
      // cuente como visto, igual que ya hacía sessionStorage.
      onDestroyed: () => {
        sessionStorage.setItem(storageKey, "1");
        onDismiss?.();
      },
    });

    const timeout = setTimeout(() => {
      driverObj.drive();
    }, 600);

    return () => clearTimeout(timeout);
  }, [ready, dismissed]); // eslint-disable-line react-hooks/exhaustive-deps
};
