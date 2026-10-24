export interface SpinnerProps {
  size?: "xs" | "sm" | "md";
  /**
   * Color del spinner:
   * - "muted": gris/brand (por defecto, para loaders de área)
   * - "white": para botones sobre fondo de color
   * - "current": hereda el color de texto (para icon-buttons)
   * - "brand": acento de marca (para indicadores inline)
   */
  tone?: "muted" | "white" | "current" | "brand";
  className?: string;
}
