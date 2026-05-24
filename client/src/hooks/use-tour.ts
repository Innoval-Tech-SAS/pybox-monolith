import { useEffect } from "react";
import { driver, type Config } from "driver.js";

export interface TourStep {
  id: string;
  title: string;
  description: string;
  side?: "top" | "right" | "bottom" | "left" | "over";
  align?: "start" | "center" | "end";
}

type TourOptions = Partial<
  Pick<Config, "nextBtnText" | "prevBtnText" | "doneBtnText" | "popoverClass" | "showProgress">
>;

const DEFAULTS: Required<TourOptions> = {
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
  useEffect(() => {
    if (!ready || sessionStorage.getItem(storageKey)) return;

    const driverObj = driver({
      ...DEFAULTS,
      ...options,
      steps: steps.map((step) => ({
        element: `#${step.id}`,
        popover: {
          title: step.title,
          description: step.description,
          side: step.side ?? "top",
          align: step.align ?? "center",
        },
      })),
      onDestroyed: () => {
        sessionStorage.setItem(storageKey, "1");
      },
    });

    const timeout = setTimeout(() => {
      driverObj.drive();
    }, 600);

    return () => clearTimeout(timeout);
  }, [ready]); // eslint-disable-line react-hooks/exhaustive-deps
};
