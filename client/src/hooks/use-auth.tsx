import { useNavigate } from "react-router";
import { jwtDecode } from "jwt-decode";
import { User } from "@/types/auth/user";
import { GooglePayload } from "@/types/auth/google";
import { DEFAULT_ROLE_SCOPE, Role, RoleScope, Scope } from "@/types/auth/role";
import { getFirstAssignment } from "@/home/utils/home-session-utils";
import { useApiClient } from "./use-api-client";
import { useOAuthRegister } from "./use-oauth-register";

interface LoginCredentials {
  email: string;
  password: string;
}

interface AuthTokenResponse {
  accessToken: string;
  refreshToken: string;
}

const getSession = (): User | null => {
  try {
    const raw = sessionStorage.getItem("user");
    return raw ? (JSON.parse(raw) as User) : null;
  } catch {
    return null;
  }
};

export const useAuth = () => {
  const navigate = useNavigate();
  const { apiClient } = useApiClient();
  const { oauthRegister, loading: oauthLoading } = useOAuthRegister();
  const user = getSession();

  const login = async ({ email, password }: LoginCredentials): Promise<void> => {
    const data: AuthTokenResponse = await apiClient("/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    sessionStorage.setItem("accessToken", data.accessToken);
    sessionStorage.setItem("refreshToken", data.refreshToken);
    sessionStorage.setItem("user", JSON.stringify({ email }));
    navigate("/dashboard", { replace: true });
  };

  const loginWithGoogle = async (token: string): Promise<void> => {
    let payload: GooglePayload;
    try {
      payload = jwtDecode<GooglePayload>(token);
    } catch {
      throw new Error("No se pudo leer la cuenta de Google seleccionada.");
    }
    await oauthRegister({ provider: "GOOGLE", token }, "/auth/oauth/login");
    sessionStorage.setItem("user", JSON.stringify({ email: payload.email }));
    navigate("/dashboard", { replace: true });
  };

  const getRoleScope = (): RoleScope => {
    const u = getSession();
    const first = getFirstAssignment(u);
    const role = (u?.userRole ?? u?.role ?? first?.role ?? DEFAULT_ROLE_SCOPE.role) as Role;
    const scope = (u?.userScope ?? u?.scope ?? first?.scope ?? DEFAULT_ROLE_SCOPE.scope) as Scope;
    return { role, scope } as RoleScope;
  };

  const fetchMe = async (): Promise<User> => {
    return await apiClient("/users/me", {});
  };

  const logout = () => {
    sessionStorage.clear();
    navigate("/admin/sign-in");
  };

  return { user, getSession, getRoleScope, login, loginWithGoogle, oauthLoading, fetchMe, logout };
};
