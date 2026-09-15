import { useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router";
import { AuthLayout } from "../components/auth-layout";
import { Label } from "@/ui/components/inputs/label";
import { OtpInput } from "@/ui/components/inputs/otp-input";
import { PasswordInput } from "@/ui/components/inputs/password-input";
import { Button } from "@/ui/components/button/button";
import { PageMeta } from "@/ui/pages/page-meta";
import { useForgotPassword } from "../hooks/use-forgot-password";

export const ResetPasswordPage: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const documentType = searchParams.get("doc_type") ?? "";
  const documentNumber = searchParams.get("doc_number") ?? "";
  const channel = (searchParams.get("channel") ?? "EMAIL") as "EMAIL" | "SMS";

  const { resetPassword, loading, error, clearError } = useForgotPassword();
  const [digits, setDigits] = useState<string[]>(Array(6).fill(""));
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [localError, setLocalError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    clearError();
    setLocalError(null);
    if (newPassword !== confirmPassword) {
      setLocalError("Las contraseñas no coinciden.");
      return;
    }
    const code = digits.join("");
    const ok = await resetPassword(documentType, documentNumber, code, channel, newPassword);
    if (ok) navigate("/admin/sign-in");
  };

  const displayError = localError ?? error;

  return (
    <>
      <PageMeta title="Restablecer contraseña" description="Ingresa el código y tu nueva contraseña" />
      <AuthLayout>
        <div className="flex flex-col flex-1">
          <div className="flex flex-col justify-center flex-1 w-full max-w-md mx-auto">
            <div>
              <div className="mb-5 sm:mb-8">
                <h1 className="mb-2 font-semibold text-brand-500 text-title-sm dark:text-white/90 sm:text-title-md">
                  Restablecer contraseña
                </h1>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  Ingresa el código enviado por{" "}
                  <span className="font-medium">{channel === "EMAIL" ? "correo electrónico" : "SMS"}</span>.
                </p>
              </div>

              <form onSubmit={handleSubmit}>
                <div className="space-y-6">
                  <div>
                    <Label className="text-gray-500 mb-2 block">Código de verificación</Label>
                    <OtpInput
                      value={digits}
                      onChange={setDigits}
                      disabled={loading}
                      error={!!displayError}
                    />
                  </div>

                  <PasswordInput
                    id="new-password"
                    label="Nueva contraseña *"
                    placeholder="Nueva contraseña"
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    required
                    autoComplete="new-password"
                  />

                  <PasswordInput
                    id="confirm-password"
                    label="Confirmar contraseña *"
                    placeholder="Confirmar contraseña"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    required
                    autoComplete="new-password"
                  />

                  {displayError && <p className="text-sm text-error-500">{displayError}</p>}

                  <Button
                    type="submit"
                    size="sm"
                    className="w-full"
                    disabled={digits.join("").length < 6 || !newPassword}
                    loading={loading}
                    loadingText="Guardando..."
                  >
                    Restablecer contraseña
                  </Button>
                </div>
              </form>

              <div className="mt-6 text-center">
                <Link
                  to="/admin/forgot-password"
                  className="text-sm text-brand-500 hover:text-brand-600 dark:text-brand-400"
                >
                  ¿No recibiste el código? Solicitar de nuevo
                </Link>
              </div>
            </div>
          </div>
        </div>
      </AuthLayout>
    </>
  );
};
