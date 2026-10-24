import type { User } from "@/types/auth/user";

// Campos que NO se persisten en sessionStorage: documento de identidad y teléfono
// son PII sensible que, a diferencia del token (cookie httpOnly), un XSS de
// cualquier dependencia de terceros (SDKs de pago, Google OAuth) sí podría leer.
// El estado en memoria de SessionProvider (useSession()) sigue teniendo el objeto
// completo -- esto solo recorta lo que sobrevive a un refresh de página.
const SENSITIVE_FIELDS = ["documentNumber", "documentType", "phoneNumber", "nationality"] as const;

const stripSensitiveFields = (user: Partial<User>): Partial<User> => {
  const safe = { ...user };
  for (const field of SENSITIVE_FIELDS) delete safe[field];
  return safe;
};

export const getSession = (): User | null => {
  try {
    const raw = sessionStorage.getItem("user");
    return raw ? (JSON.parse(raw) as User) : null;
  } catch {
    return null;
  }
};

export const setSessionUser = (user: Partial<User>) => {
  sessionStorage.setItem("user", JSON.stringify(stripSensitiveFields(user)));
};
