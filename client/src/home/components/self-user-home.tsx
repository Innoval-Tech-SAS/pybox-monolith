import { CheckCircleIcon, DocsIcon, MailIcon, UserCircleIcon } from "@/ui/icons";
import { HomeShell } from "./home-shell";

export const SelfUserHome: React.FC = () => (
  <HomeShell
    eyebrow="Home personal"
    title="Tu cuenta"
    description="Vista principal para revisar tu perfil, completar verificaciones y continuar tus procesos personales."
    metrics={[
      {
        label: "Cuenta",
        value: "Personal",
        helper: "Acceso limitado a tu propia información.",
        tone: "primary",
      },
      {
        label: "Verificación",
        value: "Pendiente",
        helper: "Completa canales requeridos cuando el sistema lo solicite.",
        tone: "warning",
      },
      {
        label: "Documentos",
        value: "Privados",
        helper: "Los datos visibles pertenecen solo a tu cuenta.",
        tone: "info",
      },
    ]}
    actions={[
      {
        title: "Perfil personal",
        description: "Revisa tu nombre, documento y datos de contacto.",
        icon: <UserCircleIcon className="size-5" />,
        tone: "primary",
      },
      {
        title: "Canales de contacto",
        description: "Administra correo y teléfono usados para verificación.",
        icon: <MailIcon className="size-5" />,
        tone: "info",
      },
      {
        title: "Verificaciones",
        description: "Completa pasos pendientes para habilitar tu cuenta.",
        icon: <CheckCircleIcon className="size-5" />,
        tone: "success",
      },
      {
        title: "Mis documentos",
        description: "Consulta información asociada a tu perfil.",
        icon: <DocsIcon className="size-5" />,
        tone: "light",
      },
    ]}
  />
);
