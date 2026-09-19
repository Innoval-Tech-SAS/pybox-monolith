export interface LoaderProps {
  loaderText?: string;
  size?: "sm" | "md";
  /**
   * Encuadre estándar del loader (evita wrappers ad-hoc):
   * - "inline": sin altura forzada (por defecto; para celdas, secciones ya dimensionadas)
   * - "section": altura mínima de sección/tarjeta
   * - "page": altura mínima de página
   */
  variant?: "inline" | "section" | "page";
  /** Clases extra para el contenedor (encuadre/altura puntual). */
  className?: string;
}
