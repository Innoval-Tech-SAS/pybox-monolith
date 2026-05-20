/**
 * Props para el componente Button.
 * @property children - Contenido del botón (texto o elementos).
 * @property size - Tamaño del botón (sm o md).
 * @property variant - Variante del botón (primary u outline).
 * @property startIcon - Ícono opcional antes del texto.
 * @property endIcon - Ícono opcional después del texto.
 * @property onClick - Función que se ejecuta al hacer clic.
 * @property disabled - Indica si el botón está deshabilitado.
 * @property className - Clases CSS adicionales para personalización.
 */
export interface ButtonProps {
  children: React.ReactNode;
  size?: "sm" | "md";
  variant?: "primary" | "outline";
  startIcon?: ReactNode;
  endIcon?: ReactNode;
  onClick?: () => void;
  disabled?: boolean;
  className?: string;
}
