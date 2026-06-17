import { Filter, Mail, Send } from "lucide-react";
import type { OrgModule } from "@/types/companies/company-types";

export const COMMUNICATIONS_MODULES: OrgModule[] = [
  {
    key: "segments",
    title: "Segmentos",
    description: "Listas dinámicas de deudores y sus relaciones. Filtra, une tablas y exporta.",
    icon: <Filter size={24} className="text-white" />,
    gradient: "from-violet-500 to-purple-600",
    path: "/my-companies/portfolios/segments",
    requiredPermission: "portfolio.clients",
  },
  {
    key: "templates",
    title: "Plantillas",
    description: "Diseña y gestiona plantillas de email y SMS.",
    icon: <Mail size={24} className="text-white" />,
    gradient: "from-emerald-500 to-teal-600",
    path: "/my-companies/templates",
    requiredPermission: "org.templates",
  },
  {
    key: "campaigns",
    title: "Campañas",
    description: "Lanza y gestiona campañas masivas de mensajería.",
    icon: <Send size={24} className="text-white" />,
    gradient: "from-indigo-500 to-blue-600",
    path: null,
  },
];
