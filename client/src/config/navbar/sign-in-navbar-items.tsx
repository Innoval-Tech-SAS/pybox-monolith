import { Building2, CreditCard, Database, FileStack, FileText, Home, Image, KeyRound, MessageCircle, TicketCheck, Users } from "lucide-react";

interface NavbarItem {
  name: string;
  icon: React.ReactNode;
  path: string;
  permission?: string;
  globalOnly?: boolean;
  adminGlobalOnly?: boolean;
}

export const signInNavbarItems = [
  {
    name: "Inicio",
    icon: <Home size={20} />,
    path: "/home",
  },
  {
    name: "Empresas",
    icon: <Building2 size={20} />,
    path: "/my-companies",
  },
];

// Ítems del aside para el titular (rol USER, scope SELF): además de Inicio (resumen con
// calendario), la sección de obligaciones (lista + detalle con la opción de dar de baja).
// El titular lee "obligaciones" y "entidades"; los tipos y endpoints siguen siendo
// credits/organizations puertas adentro.
export const selfNavbarItems = [
  {
    name: "Mis Obligaciones",
    icon: <FileText size={20} />,
    path: "/my-credits",
  },
  {
    name: "Mis Extractos",
    icon: <FileStack size={20} />,
    path: "/my-statements",
  },
];

export const otherSignInItems: NavbarItem[] = [
  {
    name: "Usuarios",
    icon: <Users size={20} />,
    path: "/my-users",
    permission: "org.users",
  },
  {
    name: "Facturación",
    icon: <CreditCard size={20} />,
    path: "/billing",
    // Vista cruzada de TODAS las organizaciones: solo administradores globales.
    // No usa `permission` porque ese check deja pasar a cualquier org-miembro
    // con org.billing, lo cual mostraria una pagina admin-only equivocada.
    globalOnly: true,
  },
  {
    name: "Bases de datos",
    icon: <Database size={20} />,
    path: "/databases",
    // Herramienta de DDL (crear/alterar tablas): solo administradores globales,
    // no cualquier usuario con scope GLOBAL (ej. Atención al Cliente).
    adminGlobalOnly: true,
  },
  {
    name: "Credenciales",
    icon: <KeyRound size={20} />,
    path: "/provider-credentials",
    // Claves de envío/pasarela cifradas: solo administradores globales.
    adminGlobalOnly: true,
  },
  {
    name: "Chats de WhatsApp",
    icon: <MessageCircle size={20} />,
    path: "/my-companies/whatsapp/chats",
    permission: "org.manage_whatsapp_chats",
  },
  {
    name: "Marca de la plataforma",
    icon: <Image size={20} />,
    path: "/platform/branding",
    // El logo global de fallback lo administra solo un admin global.
    adminGlobalOnly: true,
  },
];

export const supportNavItems = [
  {
    name: "Tickets",
    icon: <TicketCheck size={20} />,
    path: "/cs/tickets",
  },
];
