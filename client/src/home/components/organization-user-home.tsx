import { DocsIcon, FolderIcon, PageIcon, UserIcon } from "@/ui/icons";
import { HomeShell } from "./home-shell";

export const OrganizationUserHome: React.FC = () => (
  <HomeShell
    eyebrow="Home de usuario interno"
    title="Trabajo asignado"
    description="Vista para ejecutar tareas dentro de una entidad, con acceso limitado a las funciones habilitadas."
    metrics={[
      {
        label: "Asignaciones",
        value: "Activas",
        helper: "Accede a procesos y datos habilitados para tu cuenta.",
        tone: "primary",
      },
      {
        label: "Documentos",
        value: "Disponibles",
        helper: "Consulta recursos internos asociados a tu operación.",
        tone: "info",
      },
      {
        label: "Perfil",
        value: "Vigente",
        helper: "Mantén tus datos personales actualizados.",
        tone: "success",
      },
    ]}
    actions={[
      {
        title: "Mis tareas",
        description: "Continúa con actividades pendientes de tu entidad.",
        icon: <PageIcon className="size-5" />,
        tone: "primary",
      },
      {
        title: "Recursos internos",
        description: "Consulta archivos, guías y documentos habilitados.",
        icon: <FolderIcon className="size-5" />,
        tone: "info",
      },
      {
        title: "Documentación",
        description: "Revisa requisitos y soporte para tus flujos activos.",
        icon: <DocsIcon className="size-5" />,
        tone: "light",
      },
      {
        title: "Mi perfil",
        description: "Actualiza información personal y canales de contacto.",
        icon: <UserIcon className="size-5" />,
        tone: "success",
      },
    ]}
  />
);
