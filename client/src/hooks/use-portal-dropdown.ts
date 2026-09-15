import {
  useEffect,
  useLayoutEffect,
  useRef,
  useState,
  type CSSProperties,
  type RefObject,
} from "react";

type DropdownAlign = "left" | "right";

interface UsePortalDropdownOptions<T extends HTMLElement> {
  open: boolean;
  onClose: () => void;
  /** Alineación horizontal del panel respecto al disparador. Por defecto "left". */
  align?: DropdownAlign;
  /** Separación vertical en px entre el disparador y el panel. Por defecto 4. */
  gap?: number;
  /** Si el panel debe copiar el ancho del disparador. Por defecto true. */
  matchWidth?: boolean;
  /** Ref externo del disparador. Si se omite, el hook crea uno propio. */
  triggerRef?: RefObject<T | null>;
}

interface UsePortalDropdownResult<
  T extends HTMLElement,
  D extends HTMLElement,
> {
  /** Ref para el disparador (botón). Se usa para calcular la posición. */
  triggerRef: RefObject<T | null>;
  /** Ref para el panel del portal. Se usa para el click-outside. */
  dropdownRef: RefObject<D | null>;
  /** Estilo `position: fixed` listo para el panel; undefined mientras no hay medida. */
  dropdownStyle: CSSProperties | undefined;
}

/**
 * Posiciona un dropdown que se renderiza en un portal (position: fixed) para que
 * ningún ancestro con overflow lo recorte. Reposiciona en cada scroll/resize
 * mientras está abierto y cierra al hacer click fuera del disparador o del panel.
 *
 * El consumidor decide dónde montar el portal (típicamente document.body) y aplica
 * `dropdownStyle` + `dropdownRef` al contenedor del panel, y `triggerRef` al botón.
 */
export function usePortalDropdown<
  T extends HTMLElement = HTMLElement,
  D extends HTMLElement = HTMLElement,
>({
  open,
  onClose,
  align = "left",
  gap = 4,
  matchWidth = true,
  triggerRef: externalTriggerRef,
}: UsePortalDropdownOptions<T>): UsePortalDropdownResult<T, D> {
  const internalTriggerRef = useRef<T | null>(null);
  const triggerRef = externalTriggerRef ?? internalTriggerRef;
  const dropdownRef = useRef<D | null>(null);
  const [rect, setRect] = useState<DOMRect | null>(null);

  useLayoutEffect(() => {
    if (!open) {
      setRect(null);
      return;
    }
    const update = () => {
      if (triggerRef.current) setRect(triggerRef.current.getBoundingClientRect());
    };
    update();
    window.addEventListener("scroll", update, true);
    window.addEventListener("resize", update);
    return () => {
      window.removeEventListener("scroll", update, true);
      window.removeEventListener("resize", update);
    };
  }, [open]);

  useEffect(() => {
    if (!open) return;
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as Node;
      if (
        !triggerRef.current?.contains(target) &&
        !dropdownRef.current?.contains(target)
      ) {
        onClose();
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [open, onClose]);

  const dropdownStyle: CSSProperties | undefined = rect
    ? {
        position: "fixed",
        top: rect.bottom + gap,
        zIndex: 100000,
        ...(matchWidth
          ? { left: rect.left, width: rect.width }
          : align === "right"
            ? { right: Math.max(0, window.innerWidth - rect.right) }
            : { left: rect.left }),
      }
    : undefined;

  return { triggerRef, dropdownRef, dropdownStyle };
}
