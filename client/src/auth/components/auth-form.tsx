import { useState } from "react";
import { Link, useNavigate } from "react-router";
import { jwtDecode } from "jwt-decode";
import { Input } from "../../ui/components/inputs/input";
import { Label } from "../../ui/components/inputs/label";
import { EyeCloseIcon, EyeIcon } from "../../ui/icons";
import { useGoogleAuth } from "../../hooks/use-google-auth";
import { useOAuthRegister } from "../../hooks/use-oauth-register";
import { GooglePayload } from "../../types/auth/google";
import { GoogleButton } from "./google-button";

const API_URL = import.meta.env.VITE_API_URL as string;

export const AuthForm: React.FC = () => {
  const navigate = useNavigate();
  const [showPassword, setShowPassword] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const { signIn } = useGoogleAuth();
  const { oauthRegister, loading: loadingGoogle } = useOAuthRegister();

  const isLoading = loading || loadingGoogle;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const res = await fetch(`${API_URL}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      const data = await res.json();

      if (!res.ok) {
        setError(data.error ?? "Error al iniciar sesión.");
        return;
      }

      sessionStorage.setItem("accessToken", data.accessToken);
      sessionStorage.setItem("refreshToken", data.refreshToken);
      sessionStorage.setItem("user", JSON.stringify({ email }));
      navigate("/dashboard", { replace: true });
    } catch {
      setError("No se pudo conectar con el servidor.");
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleClick = () => {
    setError(null);
    signIn(async (token) => {
      let payload: GooglePayload;
      try {
        payload = jwtDecode<GooglePayload>(token);
      } catch {
        setError("No se pudo leer la cuenta de Google seleccionada.");
        return;
      }

      try {
        await oauthRegister({ provider: "GOOGLE", token }, "/auth/oauth/login");
        sessionStorage.setItem("user", JSON.stringify({ email: payload.email }));
        navigate("/dashboard", { replace: true });
      } catch (err) {
        const message = err instanceof Error ? err.message : "Error al iniciar sesión con Google.";
        setError(message);
      }
    });
  };

  return (
    <div className="flex flex-col flex-1">
      <div className="flex flex-col justify-center flex-1 w-full max-w-md mx-auto">
        <div>
          <div className="mb-5 sm:mb-8">
            <h1 className="mb-2 font-semibold text-gray-800 text-title-sm dark:text-white/90 sm:text-title-md">
              Ingresa a tu cuenta
            </h1>
          </div>
          <div>
            <form onSubmit={handleSubmit}>
              <div className="space-y-6">
                <div>
                  <Label className="text-gray-500">
                    Usuario <span className="text-error-500">*</span>
                  </Label>
                  <Input
                    type="email"
                    placeholder="Usuario"
                    name="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                  />
                </div>
                <div>
                  <Label className="text-gray-500">
                    Contraseña <span className="text-error-500">*</span>
                  </Label>
                  <div className="relative">
                    <Input
                      type={showPassword ? "text" : "password"}
                      placeholder="Ingresa tu contraseña"
                      name="password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      required
                    />
                    <span
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute z-30 -translate-y-1/2 cursor-pointer right-4 top-1/2"
                    >
                      {showPassword ? (
                        <EyeIcon className="fill-gray-500 dark:fill-gray-400 size-5" />
                      ) : (
                        <EyeCloseIcon className="fill-gray-500 dark:fill-gray-400 size-5" />
                      )}
                    </span>
                  </div>
                </div>

                {error && (
                  <p className="text-sm text-red-500">{error}</p>
                )}

                <div>
                  <button
                    type="submit"
                    disabled={isLoading}
                    className="flex items-center justify-center w-full px-4 py-3 text-sm font-medium text-white transition rounded-lg bg-brand-500 shadow-theme-xs hover:bg-brand-600 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {isLoading ? "Iniciando..." : "Iniciar Sesión"}
                  </button>
                </div>
              </div>
            </form>

            <div className="relative py-4">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-200 dark:border-gray-800" />
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-4 py-1 text-gray-400 bg-white dark:bg-gray-900">O</span>
              </div>
            </div>

            <GoogleButton
              onClick={handleGoogleClick}
              text={loadingGoogle ? "Iniciando con Google..." : "Iniciar Sesión con Google"}
              disabled={isLoading}
            />

            <div className="mt-5">
              <p className="text-sm font-normal text-center text-gray-700 dark:text-gray-400 sm:text-start">
                No tienes cuenta?{" "}
                <Link
                  to="/admin/sign-up"
                  className="text-brand-500 hover:text-brand-600 dark:text-brand-400"
                >
                  Solicita Aquí
                </Link>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
