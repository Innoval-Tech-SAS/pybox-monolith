import { Building2 } from "lucide-react";

interface SidebarLogoProps {
  logoUrl?: string | null;
  variant?: "full" | "compact";
}

const SIZES: Record<"full" | "compact", { width: number; height: number }> = {
  full: { width: 150, height: 40 },
  compact: { width: 32, height: 32 },
};

/**
 * Logo del sidebar/navbar: el que resuelve `useSidebarLogo` (organización del
 * usuario, o el global de fallback). Si todavía no hay ninguno configurado, un
 * placeholder neutro -- nunca una ruta de imagen fija que pueda dejar de existir
 * (antes era `/images/logo.png`, un archivo que nunca estuvo en el repo).
 */
export const SidebarLogo: React.FC<SidebarLogoProps> = ({ logoUrl, variant = "full" }) => {
  const { width, height } = SIZES[variant];

  if (logoUrl) {
    return <img src={logoUrl} alt="Logo" width={width} height={height} className="object-contain" />;
  }

  return (
    <div
      style={{ width, height }}
      className="flex items-center justify-center rounded-lg border border-gray-200 bg-gray-50 text-gray-300 dark:border-gray-800 dark:bg-gray-900 dark:text-gray-600"
    >
      <Building2 size={variant === "full" ? 20 : 16} />
    </div>
  );
};
