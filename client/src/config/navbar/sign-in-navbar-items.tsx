import { Building2, Home } from "lucide-react";

export const signInNavbarItems = [
  {
    name: "Home",
    icon: <Home size={20} />,
    path: "/dashboard",
    new: true,
  },
  {
    name: "Mis Empresas",
    icon: <Building2 size={20} />,
    path: "/my-companies",
    new: true,
  },
];

export const otherSignInItems = [];
