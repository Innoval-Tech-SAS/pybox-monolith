export type RoleOption = { label: string; role: string };

export const GLOBAL_ADMIN_ROLE_OPTIONS: RoleOption[] = [
  { label: "Administrador", role: "ADMINISTRADOR" },
  { label: "Atención al cliente", role: "ATENCION_AL_CLIENTE" },
];

export const ORG_ADMIN_ROLE_OPTIONS: RoleOption[] = [
  { label: "Atención al cliente", role: "ATENCION_AL_CLIENTE" },
  { label: "Usuario", role: "USUARIO" },
];
