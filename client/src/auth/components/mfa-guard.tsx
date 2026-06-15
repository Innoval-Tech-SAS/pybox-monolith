import React, { useState } from "react";
import { OtpInput } from "@/ui/components/inputs/otp-input";
import { useVerifyOtp } from "@/hooks/use-verify-otp";
import { Modal } from "@/ui/components/modal/modal";
import type { MfaGuardProps } from "@/auth/types/mfa-guard-props";

export const MfaGuard: React.FC<MfaGuardProps> = ({ children }) => {
  const verified = sessionStorage.getItem("mfaVerified");
  const [done, setDone] = useState(verified === "true");
  const [digits, setDigits] = useState<string[]>(Array(6).fill(""));
  const [codeSent, setCodeSent] = useState(false);
  const { requestOtp, verifyOtp, loading, error, clearError } = useVerifyOtp();

  if (done) return <>{children}</>;

  const handleRequest = async () => {
    clearError();
    await requestOtp("EMAIL");
    setCodeSent(true);
  };

  const handleVerify = async () => {
    clearError();
    await verifyOtp("EMAIL", digits.join(""));
    sessionStorage.setItem("mfaVerified", "true");
    setDone(true);
  };

  return (
    <Modal isOpen onClose={() => {}} showCloseButton={false} isFullscreen className="flex bg-white dark:bg-gray-900">
      {/* Left panel */}
      <div className="hidden lg:flex lg:w-80 xl:w-96 flex-col justify-between bg-brand-600 px-10 py-12 text-white shrink-0">
        <div>
          <div className="mb-12">
            <span className="text-2xl font-bold tracking-tight">PYBOX</span>
          </div>
          <div className="mb-3">
            <span className="text-sm font-medium text-brand-200 uppercase tracking-widest">
              Verificación de identidad
            </span>
          </div>
          <h1 className="text-3xl font-semibold leading-snug mb-2">
            Confirma tu acceso
          </h1>
          <p className="text-brand-200 text-sm leading-relaxed">
            Por seguridad, verificamos tu identidad en cada inicio de sesión.
          </p>
        </div>
        <div className="text-xs text-brand-300">Autenticación de dos factores</div>
      </div>

      {/* Right panel */}
      <div className="flex flex-1 flex-col items-center justify-center px-6 py-6 sm:px-12 lg:px-16">
        <div className="w-full max-w-lg space-y-5">
          <div>
            <h2 className="text-lg font-semibold text-gray-800 dark:text-white/90">
              Verifica tu correo electrónico
            </h2>
            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
              Enviaremos un código de 6 dígitos a tu correo registrado.
            </p>
          </div>

          {!codeSent ? (
            <button
              type="button"
              disabled={loading}
              onClick={handleRequest}
              className="flex w-full items-center justify-center rounded-lg bg-brand-500 px-4 py-3 text-sm font-medium text-white transition hover:bg-brand-600 disabled:opacity-50"
            >
              {loading ? "Enviando..." : "Enviar código"}
            </button>
          ) : (
            <>
              <div className="space-y-3">
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Ingresa el código de 6 dígitos enviado por <span className="font-medium">correo</span>.
                </p>
                <OtpInput value={digits} onChange={setDigits} disabled={loading} error={!!error} />
                {error && <p className="text-xs text-error-500">{error}</p>}
              </div>
              <div className="flex flex-col gap-2">
                <button
                  type="button"
                  disabled={loading || digits.join("").length < 6}
                  onClick={handleVerify}
                  className="flex w-full items-center justify-center rounded-lg bg-brand-500 px-4 py-3 text-sm font-medium text-white transition hover:bg-brand-600 disabled:opacity-50"
                >
                  {loading ? "Verificando..." : "Verificar"}
                </button>
                <button
                  type="button"
                  disabled={loading}
                  onClick={() => { setCodeSent(false); setDigits(Array(6).fill("")); clearError(); }}
                  className="text-sm text-gray-500 hover:text-gray-700 dark:text-gray-400"
                >
                  Reenviar código
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    </Modal>
  );
};
