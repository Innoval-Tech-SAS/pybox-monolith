import { Building2, Home, Users } from "lucide-react";

export const signInNavbarItems = [
  {
    name: "Home",
    icon: <Home size={20} />,
    path: "/dashboard",
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
  },
];
