import { BoxIconLine, GridIcon, InfoIcon, UserIcon } from "@/ui/icons";
import { HomeShell } from "./home-shell";

export const DefaultHome: React.FC = () => (
  <HomeShell
    eyebrow="Home"
    title="Dashboard"
    description="Vista base para experiencias todavía no especializadas en el frontend."
    metrics={[
      {
        label: "Acceso",
        value: "Activo",
        helper: "La sesión está habilitada para entrar al dashboard.",
        tone: "primary",
      },
      {
        label: "Vista",
        value: "Base",
        helper: "El contenido específico puede conectarse después por permisos.",
        tone: "info",
      },
      {
        label: "Estado",
        value: "Listo",
        helper: "Listo para conectar vistas específicas.",
        tone: "light",
      },
    ]}
    actions={[
      {
        title: "Resumen general",
        description: "Punto de entrada neutral para módulos futuros.",
        icon: <GridIcon className="size-5" />,
        tone: "primary",
      },
      {
        title: "Contexto de acceso",
        description: "El contenido puede adaptarse a permisos y sesión activa.",
        icon: <InfoIcon className="size-5" />,
        tone: "info",
      },
      {
        title: "Perfil",
        description: "Datos básicos de la cuenta autenticada.",
        icon: <UserIcon className="size-5" />,
        tone: "light",
      },
      {
        title: "Módulos",
        description: "Espacio reservado para navegación por permisos.",
        icon: <BoxIconLine className="size-5" />,
        tone: "success",
      },
    ]}
  />
);
