export type ForgotPasswordStep = 1 | 2 | 3 | 4;

export const FORGOT_PASSWORD_STEP_TITLES: Record<ForgotPasswordStep, string> = {
  1: "Recuperar contraseña",
  2: "Elige cómo recibir el código",
  3: "Verifica el código",
  4: "Nueva contraseña",
};

export const FORGOT_PASSWORD_STEP_SUBTITLES: Record<ForgotPasswordStep, string> = {
  1: "Ingresa tu tipo y número de documento para encontrar tu cuenta.",
  2: "Encontramos tu cuenta. Elige dónde enviamos el código.",
  3: "Ingresa el código que recibiste para verificar tu identidad.",
  4: "Código verificado. Ahora elige tu nueva contraseña.",
};
