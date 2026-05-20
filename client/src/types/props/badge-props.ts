type BadgeVariant = "light" | "solid";
type BadgeSize = "sm" | "md";
type BadgeColor =
  | "primary"
  | "success"
  | "error"
  | "warning"
  | "info"
  | "light"
  | "dark";

/**
 * Props para el componente Badge.
 * @property variant - Variante del badge (light o solid).
 * @property size - Tamaño del badge (sm o md).
 * @property color - Color del badge (primary, success, error, warning, info, light, dark).
 * @property startIcon - Ícono opcional al inicio del badge.
 * @property endIcon - Ícono opcional al final del badge.
 * @property children - Contenido del badge.
 */
export interface BadgeProps {
  variant?: BadgeVariant;
  size?: BadgeSize;
  color?: BadgeColor;
  startIcon?: React.ReactNode;
  endIcon?: React.ReactNode;
  children: React.ReactNode;
}
