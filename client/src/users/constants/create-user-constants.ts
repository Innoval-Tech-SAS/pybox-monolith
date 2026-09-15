export const ROLE_LABELS: Record<string, string> = {
  ADMINISTRADOR: "Administrador",
  "ATENCION_AL_CLIENTE": "Agente de soporte",
  USUARIO: "Usuario",
};

export const GLOBAL_ROLE_LABELS: Record<string, string> = {
  ADMINISTRADOR: "Administrador",
  "ATENCION_AL_CLIENTE": "Soporte técnico",
};

export const IS_USER_ORG = "USUARIO";

export const INPUT_BASE =
  "h-11 w-full rounded-lg border appearance-none px-4 py-2.5 text-sm shadow-theme-xs placeholder:text-gray-400 focus:outline-hidden focus:ring-3 bg-transparent text-gray-800 border-gray-300 focus:border-brand-300 focus:ring-brand-500/20 dark:bg-gray-900 dark:text-white/90 dark:placeholder:text-white/30 dark:border-gray-700 dark:focus:border-brand-800";

export const CREATE_USER_INITIAL_FORM = {
  firstname: "",
  lastname: "",
  email: "",
  phoneNumber: "",
  password: "",
};
