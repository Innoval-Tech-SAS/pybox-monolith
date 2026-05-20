import { GridIcon } from "../../ui/icons";

export const signInNavbarItems = [
  {
    name: "Dashboard",
    icon: <GridIcon />,
    path: "",
    new: false,
    // subItems: [
    //   {
    //     name: "",
    //     path: "",
    //   },
    // ],
  },
  {
    name: "Campañas",
    icon: <GridIcon />,
    path: "",
    new: false,
    subItems: [
      {
        name: "Todas las Campañas",
        path: "/",
      },
    ],
  },
  {
    name: "Bots",
    icon: <GridIcon />,
    path: "",
    new: false,
    subItems: [
      {
        name: "Bots por Campaña",
        path: "/",
      },
    ],
  },
];

export const otherSignInItems = [
  {
    icon: <GridIcon />,
    name: "Sistema",
    subItems: [
      { name: "Estado", path: "/admin/system-status", pro: false },
      { name: "Base de Datos", path: "/admin/database-status", pro: false },
      { name: "Disco", path: "/disk-status", pro: false },
      { name: "Memoria", path: "/memory-status", pro: false },
      { name: "Cache", path: "/cache-status", pro: false },
    ],
  },
  {
    icon: <GridIcon />,
    name: "Soporte",
    subItems: [{ name: "Crear Ticket", path: "/report-bugs", pro: false }],
  },
];
