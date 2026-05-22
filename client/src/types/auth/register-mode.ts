export type RegisterMode = "admin" | "user";

export const REGISTER_PANEL = {
  admin: {
    badge: "Gestión empresarial",
    title: "Registra tu",
    highlight: "tu empresa",
    description:
      "Configura tu empresa y gestiona tu equipo desde un solo lugar. Control total, resultados profesionales.",
  },
  user: {
    badge: "Acceso personal",
    title: "Únete a",
    highlight: "la plataforma",
    description:
      "Crea tu cuenta personal y accede a todas las funcionalidades. Registro rápido, seguridad garantizada.",
  },
} as const;
