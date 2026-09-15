import { useState } from "react";
import { Link } from "react-router";
import { Input } from "../../ui/components/inputs/input";
import { Label } from "../../ui/components/inputs/label";
import { PasswordInput } from "../../ui/components/inputs/password-input";
import { useAuth } from "../../hooks/use-auth";
import { GoogleButton } from "./google-button";

export const AuthForm: React.FC = () => {
  const { login, loginWithGoogle, oauthLoading } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  const isLoading = loading || oauthLoading;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await login({ email, password });
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleToken = async (token: string) => {
    await loginWithGoogle(token);
  };

  return (
    <div className="flex flex-col flex-1">
      <div className="flex flex-col justify-center flex-1 w-full max-w-md mx-auto">
        <div>
          <div className="mb-5 sm:mb-8 flex items-center justify-start gap-4">
            <h1 className="mb-2 font-semibold text-brand-500 text-title-sm dark:text-white/90 sm:text-title-md">
              Ingresa a tu cuenta
            </h1>
          </div>
          <div>
            <form onSubmit={handleSubmit}>
              <div className="space-y-6">
                <div>
                  <Label htmlFor="login-email" className="text-gray-500">
                    Correo electrónico <span className="text-error-500">*</span>
                  </Label>
                  <Input
                    id="login-email"
                    type="email"
                    placeholder="Correo electrónico"
                    name="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    autoComplete="username"
                  />
                </div>
                <PasswordInput
                  id="login-password"
                  label="Contraseña *"
                  placeholder="Ingresa tu contraseña"
                  name="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  autoComplete="current-password"
                />

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
                <span className="px-4 py-1 text-gray-400 bg-white dark:bg-gray-900">
                  O
                </span>
              </div>
            </div>

            <GoogleButton
              onToken={handleGoogleToken}
              text={
                oauthLoading
                  ? "Iniciando con Google..."
                  : "Iniciar Sesión con Google"
              }
              disabled={isLoading}
            />

            <div className="mt-4 text-center">
              <Link
                to="/admin/forgot-password"
                className="text-sm text-brand-500 hover:text-brand-600 dark:text-brand-400"
              >
                ¿Olvidaste tu contraseña?
              </Link>
            </div>

            <div className="mt-4 text-center">
              <Link
                to="/admin/sign-up"
                className="inline-flex items-center justify-center w-full px-4 py-3 text-sm font-medium text-brand-600 border border-brand-300 rounded-lg hover:bg-brand-50 dark:text-brand-400 dark:border-brand-700 dark:hover:bg-brand-950 transition-colors"
              >
                {"¿No tienes una cuenta? Regístrate"}
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
