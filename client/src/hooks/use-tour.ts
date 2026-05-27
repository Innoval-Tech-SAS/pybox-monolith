import { useEffect } from "react";
import { driver, type Config, type PopoverDOM } from "driver.js";

export interface TourStep {
  id?: string;
  title: string;
  description: string;
  side?: "top" | "right" | "bottom" | "left" | "over";
  align?: "start" | "center" | "end";
}

type TourOptions = Partial<
  Pick<Config, "nextBtnText" | "prevBtnText" | "doneBtnText" | "popoverClass" | "showProgress">
> & {
  dismissed?: boolean;
  dismissBtnText?: string;
  onPermanentDismiss?: () => void;
  showPermanentDismissOnEveryStep?: boolean;
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
  const {
    dismissed,
    dismissBtnText = "No volver a mostrar",
    onPermanentDismiss,
    showPermanentDismissOnEveryStep = false,
    ...driverOptions
  } = options ?? {};

  useEffect(() => {
    if (!ready || dismissed || sessionStorage.getItem(storageKey)) return;

    let driverObj: ReturnType<typeof driver>;

    driverObj = driver({
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
      onPopoverRender: onPermanentDismiss
        ? (popover: PopoverDOM, { state, config }: { state: { activeIndex?: number }; config: { steps?: unknown[] } }) => {
            popover.wrapper.querySelector(".tour-dismiss-btn")?.remove();
            const isLastStep = (state.activeIndex ?? 0) === (config.steps?.length ?? 1) - 1;
            if (!showPermanentDismissOnEveryStep && !isLastStep) return;
            const btn = document.createElement("button");
            btn.textContent = dismissBtnText;
            btn.className = "tour-dismiss-btn";
            btn.onclick = () => {
              onPermanentDismiss();
              driverObj.destroy();
            };
            popover.footer.after(btn);
          }
        : undefined,
      onDestroyed: () => {
        sessionStorage.setItem(storageKey, "1");
      },
    });

    const timeout = setTimeout(() => {
      driverObj.drive();
    }, 600);

    return () => clearTimeout(timeout);
  }, [ready, dismissed]); // eslint-disable-line react-hooks/exhaustive-deps
};
