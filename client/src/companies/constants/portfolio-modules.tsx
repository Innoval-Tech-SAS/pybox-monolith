import {
  CalendarDays,
  Plus,
  Send,
  ShieldCheck,
  UserPlus,
  Users,
} from "lucide-react";
import type { OrgModule } from "@/types/companies/company-types";

export const PORTFOLIO_MODULES: OrgModule[] = [
  {
    key: "debtors",
    title: "Clientes",
    description: "Gestión de clientes, segmentación y análisis de cartera.",
    icon: <Users size={24} className="text-white" />,
    gradient: "from-indigo-500 to-blue-600",
    path: null,
  },
  {
    key: "portfolio-update-strict",
    title: "Actualizar clientes",
    description: "Actualiza información de clientes que ya existen en esta cartera.",
    icon: <ShieldCheck size={24} className="text-white" />,
    gradient: "from-amber-500 to-orange-600",
    path: null,
  },
  {
    key: "portfolio-update-append",
    title: "Subir nuevos clientes",
    description: "Sube un CSV para registrar nuevos clientes y actualizar los existentes.",
    icon: <UserPlus size={24} className="text-white" />,
    gradient: "from-emerald-500 to-teal-600",
    path: null,
  },
  {
    key: "messages",
    title: "Comunicaciones",
    description: "Flujos, campañas masivas y plantillas de mensajería.",
    icon: <Send size={24} className="text-white" />,
    gradient: "from-indigo-500 to-blue-600",
    path: null,
  },
  {
    key: "messages-calendar",
    title: "Calendario de Comunicaciones",
    description: "Consulta campañas por fecha y estado en una vista temporal.",
    icon: <CalendarDays size={24} className="text-white" />,
    gradient: "from-emerald-500 to-teal-600",
    path: null,
  },
  {
    key: "upcoming",
    title: "Próximos Módulos",
    description: "Aquí se irán agregando nuevos módulos operativos.",
    icon: <Plus size={24} className="text-white" />,
    gradient: "from-slate-400 to-slate-500",
    path: null,
  },
];
