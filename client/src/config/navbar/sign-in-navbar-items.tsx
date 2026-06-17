import { Building2, CreditCard, Home, TicketCheck, Users } from "lucide-react";

interface NavbarItem {
  name: string;
  icon: React.ReactNode;
  path: string;
  permission?: string;
  globalOnly?: boolean;
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
];

export const supportNavItems = [
  {
    name: "Tickets",
    icon: <TicketCheck size={20} />,
    path: "/cs/tickets",
  },
];
