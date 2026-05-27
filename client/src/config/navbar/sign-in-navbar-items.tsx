import { Building2, Home, TicketCheck, Users } from "lucide-react";

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

export const otherSignInItems = [
  {
    name: "Usuarios",
    icon: <Users size={20} />,
    path: "/my-users",
    permission: "org.users",
  },
];

export const supportNavItems = [
  {
    name: "Tickets",
    icon: <TicketCheck size={20} />,
    path: "/cs/tickets",
  },
];
