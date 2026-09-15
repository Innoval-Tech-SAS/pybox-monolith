import { useState } from "react";
import { Link } from "react-router";
import { Label } from "@/ui/components/inputs/label";
import { useForgotPassword } from "../hooks/use-forgot-password";
import type { Channel } from "../hooks/use-forgot-password";
import type { ForgotPasswordStep2Props } from "@/auth/types/props/forgot-password-step-2-props";

export const ForgotPasswordStep2: React.FC<ForgotPasswordStep2Props> = ({
  lookup,
  docType,
  docNumber,
  onNext,
  loading,
}) => {
  const { sendCode } = useForgotPassword();
  const [channel, setChannel] = useState<Channel>("EMAIL");
  const hasAnyChannel = !!lookup.maskedEmail || !!lookup.maskedPhone;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const ok = await sendCode(docType, docNumber, channel);
    if (ok) onNext(channel);
  };

  if (!hasAnyChannel) {
    // Documento sin cuenta asociada (o cuenta sin canales verificados). No decimos cuál
    // de las dos cosas es: revelarlo permitiría enumerar documentos registrados.
    return (
      <div className="space-y-5">
        <div className="rounded-lg border border-gray-100 bg-gray-50 px-4 py-3 dark:border-gray-800 dark:bg-gray-800/50">
          <p className="text-sm text-gray-600 dark:text-gray-300">
            No pudimos encontrar un canal para enviarte el código. Verifica el documento o
            contacta a soporte si el problema persiste.
          </p>
        </div>
        <Link
          to="/login"
          className="flex w-full items-center justify-center rounded-lg border border-gray-300 px-4 py-3 text-sm font-medium text-gray-700 transition hover:bg-gray-50 dark:border-gray-700 dark:text-gray-300 dark:hover:bg-gray-800"
        >
          Volver al inicio de sesión
        </Link>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit}>
      <div className="space-y-5">
        <div className="rounded-lg border border-gray-100 bg-gray-50 px-4 py-3 dark:border-gray-800 dark:bg-gray-800/50">
          <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">Cuenta encontrada</p>
          {lookup.maskedEmail && (
            <p className="text-sm font-medium text-gray-700 dark:text-gray-300">{lookup.maskedEmail}</p>
          )}
          {lookup.maskedPhone && (
            <p className="text-sm font-medium text-gray-700 dark:text-gray-300">{lookup.maskedPhone}</p>
          )}
        </div>

        <div>
          <Label className="text-gray-500">¿Dónde enviamos el código?</Label>
          <div className="mt-2 flex gap-2">
            {(["EMAIL", "SMS"] as Channel[]).map((ch) => {
              const available = ch === "EMAIL" ? !!lookup.maskedEmail : !!lookup.maskedPhone;
              return (
                <button
                  key={ch}
                  type="button"
                  disabled={!available}
                  onClick={() => setChannel(ch)}
                  className={`flex-1 rounded-lg border px-4 py-2.5 text-sm font-medium transition-colors disabled:opacity-40 disabled:cursor-not-allowed ${
                    channel === ch && available
                      ? "border-brand-500 bg-brand-500 text-white"
                      : "border-gray-300 bg-white text-gray-700 hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-gray-700"
                  }`}
                >
                  {ch === "EMAIL" ? "Correo electrónico" : "SMS"}
                </button>
              );
            })}
          </div>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="flex w-full items-center justify-center rounded-lg bg-brand-500 px-4 py-3 text-sm font-medium text-white transition hover:bg-brand-600 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? "Enviando..." : "Enviar código"}
        </button>
      </div>
    </form>
  );
};
