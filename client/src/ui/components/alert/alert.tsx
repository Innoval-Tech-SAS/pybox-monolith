import { Link } from "react-router";
import { variantClasses, icons } from "@/ui/utils/alert-utils";
import { AlertProps } from "@/types/props/alert-props";

/**
 * Componente visual para mostrar alertas informativas con estilos y variantes.
 *
 * @param variant - Tipo de alerta para definir el estilo (success, error, warning, info).
 * @param title - Título de la alerta.
 * @param message - Contenido del mensaje de la alerta.
 * @param showLink - Si se debe mostrar un enlace adicional.
 * @param linkHref - URL a la que redirige el enlace.
 * @param linkText - Texto que se muestra en el enlace.
 * @returns Componente React de alerta.
 */
export const Alert: React.FC<AlertProps> = ({
  variant,
  title,
  message,
  showLink = false,
  linkHref = "#",
  linkText = "Learn more",
}) => {
  return (
    <div
      className={`rounded-xl border p-4 ${variantClasses[variant].container}`}
    >
      <div className="flex items-start gap-3">
        <div className={`-mt-0.5 ${variantClasses[variant].icon}`}>
          {icons[variant]}
        </div>

        <div>
          <h4 className="mb-1 text-sm font-semibold text-gray-800 dark:text-white/90">
            {title}
          </h4>

          <p className="text-sm text-gray-500 dark:text-gray-400">{message}</p>

          {showLink && (
            <Link
              to={linkHref}
              className="inline-block mt-3 text-sm font-medium text-gray-500 underline dark:text-gray-400"
            >
              {linkText}
            </Link>
          )}
        </div>
      </div>
    </div>
  );
};
