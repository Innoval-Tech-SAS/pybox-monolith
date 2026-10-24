import { Filter, Mail, Phone, Send, Upload } from "lucide-react";
import type { OrgModule } from "@/types/companies/company-types";

export const COMMUNICATIONS_MODULES: OrgModule[] = [
  {
    key: "segments",
    title: "Segmentos",
    description: "Listas dinámicas de deudores y sus relaciones. Filtra, une tablas y exporta.",
    icon: Filter,
    gradient: "from-violet-500 to-purple-600",
    path: "/my-companies/portfolios/segments",
    requiredPermission: "portfolio.clients",
  },
  {
    key: "templates",
    title: "Plantillas",
    description: "Diseña y gestiona plantillas de email y SMS.",
    icon: Mail,
    gradient: "from-emerald-500 to-teal-600",
    path: "/my-companies/templates",
    requiredPermission: "org.templates",
  },
  {
    key: "campaigns",
    title: "Campañas",
    description: "Lanza y gestiona campañas masivas de mensajería.",
    icon: Send,
    gradient: "from-indigo-500 to-blue-600",
    path: "/my-companies/campaigns",
    requiredPermission: "org.campaigns",
  },
  {
    key: "ivr",
    title: "Flujos IVR",
    description: "Diseña árboles de llamada IVR para campañas de voz masivas.",
    icon: Phone,
    gradient: "from-sky-500 to-cyan-600",
    path: "/my-companies/campaigns/ivr",
    requiredPermission: "org.campaigns",
  },
  {
    key: "bulk-send",
    title: "Envío masivo",
    description: "Envía mensajes masivos desde un archivo CSV o Excel.",
    icon: Upload,
    gradient: "from-amber-500 to-orange-600",
    path: "/my-companies/bulk-send",
    requiredPermission: "portfolio.communications",
  },
];
