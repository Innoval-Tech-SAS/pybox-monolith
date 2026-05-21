import React, { useState } from "react";
import { OtpInput } from "@/ui/components/inputs/otp-input";
import { VerificationChannel } from "@/types/onboarding/onboarding-types";

interface Props {
  title: string;
  description: string;
  defaultChannel: VerificationChannel;
  onDone: () => void;
  requestOtp: (channel: VerificationChannel) => Promise<void>;
  verifyOtp: (channel: VerificationChannel, code: string) => Promise<void>;
  loading: boolean;
  error: string | null;
  clearError: () => void;
}

export const VerifyChannelStep: React.FC<Props> = ({
  title,
  description,
  defaultChannel,
  onDone,
  requestOtp,
  verifyOtp,
  loading,
  error,
  clearError,
}) => {
  const [channel, setChannel] = useState<VerificationChannel>(defaultChannel);
  const [digits, setDigits] = useState<string[]>(Array(6).fill(""));
  const [codeSent, setCodeSent] = useState(false);

  const handleRequestOtp = async () => {
    clearError();
    await requestOtp(channel);
    setCodeSent(true);
  };

  const handleVerify = async () => {
    clearError();
    await verifyOtp(channel, digits.join(""));
    onDone();
  };

  return (
    <div className="space-y-5">
      <div>
        <h2 className="text-lg font-semibold text-gray-800 dark:text-white/90">{title}</h2>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">{description}</p>
      </div>

      {!codeSent ? (
        <>
          <div className="space-y-2">
            <p className="text-sm font-medium text-gray-700 dark:text-gray-300">
              ¿Por dónde quieres recibir el código?
            </p>
            <div className="flex gap-3">
              {(["EMAIL", "SMS"] as VerificationChannel[]).map((ch) => (
                <button
                  key={ch}
                  type="button"
                  onClick={() => setChannel(ch)}
                  className={`flex-1 rounded-lg border py-2.5 text-sm font-medium transition-colors ${
                    channel === ch
                      ? "border-brand-500 bg-brand-50 text-brand-600 dark:bg-brand-900/20 dark:text-brand-400"
                      : "border-gray-300 text-gray-600 hover:border-gray-400 dark:border-gray-700 dark:text-gray-400"
                  }`}
                >
                  {ch === "EMAIL" ? "Correo electrónico" : "SMS"}
                </button>
              ))}
            </div>
          </div>
          <button
            type="button"
            disabled={loading}
            onClick={handleRequestOtp}
            className="flex w-full items-center justify-center rounded-lg bg-brand-500 px-4 py-3 text-sm font-medium text-white transition hover:bg-brand-600 disabled:opacity-50"
          >
            {loading ? "Enviando..." : "Enviar código"}
          </button>
        </>
      ) : (
        <>
          <div className="space-y-3">
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Ingresa el código de 6 dígitos enviado por{" "}
              <span className="font-medium">{channel === "EMAIL" ? "correo" : "SMS"}</span>.
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
              Cambiar canal o reenviar código
            </button>
          </div>
        </>
      )}
    </div>
  );
};
