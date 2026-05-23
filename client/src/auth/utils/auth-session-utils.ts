import type { User } from "@/types/auth/user";

export const getSession = (): User | null => {
  try {
    const raw = sessionStorage.getItem("user");
    return raw ? (JSON.parse(raw) as User) : null;
  } catch {
    return null;
  }
};

export const setSessionUser = (user: Partial<User>) => {
  sessionStorage.setItem("user", JSON.stringify(user));
};
