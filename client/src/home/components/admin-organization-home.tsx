import { BoxCubeIcon, GroupIcon, TaskIcon, UserCircleIcon } from "@/ui/icons";
import { HomeShell } from "./home-shell";

export const AdminOrganizationHome: React.FC = () => (
  <HomeShell
    eyebrow="Home de entidad"
    title="Operación de tu entidad"
    description="Vista principal para administrar el estado operativo, el equipo y las acciones pendientes de la entidad activa."
    metrics={[
      {
        label: "Estado",
        value: "Activo",
        helper: "La entidad está lista para operar.",
        tone: "success",
      },
      {
        label: "Equipo",
        value: "Permisos",
        helper: "Gestiona usuarios internos y accesos operativos.",
        tone: "primary",
      },
      {
        label: "Pendientes",
        value: "Onboarding",
        helper: "Completa datos corporativos cuando aplique.",
        tone: "warning",
      },
    ]}
    actions={[
      {
        title: "Usuarios y permisos",
        description: "Administra accesos para miembros de la entidad.",
        icon: <GroupIcon className="size-5" />,
        tone: "primary",
      },
      {
        title: "Perfil de entidad",
        description: "Revisa los datos fiscales y documentos de la entidad.",
        icon: <BoxCubeIcon className="size-5" />,
        tone: "info",
      },
      {
        title: "Tareas operativas",
        description: "Da seguimiento a pasos pendientes antes de abrir nuevos flujos.",
        icon: <TaskIcon className="size-5" />,
        tone: "warning",
      },
      {
        title: "Cuenta administradora",
        description: "Mantén actualizado el perfil responsable de la entidad.",
        icon: <UserCircleIcon className="size-5" />,
        tone: "light",
      },
    ]}
  />
);
