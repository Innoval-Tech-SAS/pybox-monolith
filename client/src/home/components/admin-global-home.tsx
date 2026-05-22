import { BoxIcon, GridIcon, PieChartIcon, TableIcon } from "@/ui/icons";
import { HomeShell } from "./home-shell";

export const AdminGlobalHome: React.FC = () => (
  <HomeShell
    eyebrow="Home global"
    title="Control general de la plataforma"
    description="Vista para supervisar entidades, configuración base y señales globales del sistema."
    metrics={[
      {
        label: "Acceso",
        value: "Global",
        helper: "Acceso transversal a entidades y configuración.",
        tone: "primary",
      },
      {
        label: "Entidades",
        value: "Monitoreo",
        helper: "Revisa actividad y estado operativo por organización.",
        tone: "info",
      },
      {
        label: "Riesgo",
        value: "Control",
        helper: "Prioriza revisiones de permisos y procesos críticos.",
        tone: "warning",
      },
    ]}
    actions={[
      {
        title: "Mapa de entidades",
        description: "Consulta organizaciones y su estado de habilitación.",
        icon: <GridIcon className="size-5" />,
        tone: "primary",
      },
      {
        title: "Configuración base",
        description: "Administra catálogos, reglas y parámetros globales.",
        icon: <BoxIcon className="size-5" />,
        tone: "info",
      },
      {
        title: "Reportes ejecutivos",
        description: "Analiza señales consolidadas de operación.",
        icon: <PieChartIcon className="size-5" />,
        tone: "success",
      },
      {
        title: "Auditoría",
        description: "Revisa cambios sensibles y actividad administrativa.",
        icon: <TableIcon className="size-5" />,
        tone: "warning",
      },
    ]}
  />
);
