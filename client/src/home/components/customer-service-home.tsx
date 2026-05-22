import { ChatIcon, CheckCircleIcon, ListIcon, TimeIcon } from "@/ui/icons";
import { HomeShell } from "./home-shell";

export const CustomerServiceHome: React.FC = () => (
  <HomeShell
    eyebrow="Home de soporte"
    title="Atención y seguimiento"
    description="Vista enfocada en solicitudes, verificación de casos y continuidad de servicio para usuarios y entidades."
    metrics={[
      {
        label: "Casos",
        value: "Abiertos",
        helper: "Prioriza solicitudes recientes y bloqueos.",
        tone: "warning",
      },
      {
        label: "Respuesta",
        value: "En curso",
        helper: "Mantén trazabilidad de conversaciones activas.",
        tone: "info",
      },
      {
        label: "Resolución",
        value: "Validación",
        helper: "Confirma cierres antes de finalizar cada caso.",
        tone: "success",
      },
    ]}
    actions={[
      {
        title: "Bandeja de solicitudes",
        description: "Consulta tickets asignados y próximos vencimientos.",
        icon: <ListIcon className="size-5" />,
        tone: "warning",
      },
      {
        title: "Conversaciones",
        description: "Continúa el seguimiento con usuarios y entidades.",
        icon: <ChatIcon className="size-5" />,
        tone: "info",
      },
      {
        title: "Verificaciones",
        description: "Valida datos o documentos relacionados con el caso.",
        icon: <CheckCircleIcon className="size-5" />,
        tone: "success",
      },
      {
        title: "Tiempos de atención",
        description: "Revisa prioridades y acuerdos de servicio pendientes.",
        icon: <TimeIcon className="size-5" />,
        tone: "primary",
      },
    ]}
  />
);
