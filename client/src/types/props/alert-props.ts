/**
 * Props para el componente Alert.
 * @property variant - Tipo de alerta (success, error, warning, info).
 * @property title - Título de la alerta.
 * @property message - Mensaje principal de la alerta.
 * @property showLink - Indica si se debe mostrar un enlace adicional.
 * @property linkHref - URL del enlace.
 * @property linkText - Texto del enlace.
 */
export interface AlertProps {
  variant: "success" | "error" | "warning" | "info";
  title: string;
  message: string;
  showLink?: boolean;
  linkHref?: string;
  linkText?: string;
}
