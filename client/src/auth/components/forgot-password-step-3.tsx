import { useState } from "react";
import { Label } from "@/ui/components/inputs/label";
import { OtpInput } from "@/ui/components/inputs/otp-input";
import { useForgotPassword } from "../hooks/use-forgot-password";
import type { ForgotPasswordStep3Props } from "@/auth/types/props/forgot-password-step-3-props";

export const ForgotPasswordStep3: React.FC<ForgotPasswordStep3Props> = ({
  docType,
  docNumber,
  channel,
  onNext,
  loading,
}) => {
  const { verifyCode } = useForgotPassword();
  const [digits, setDigits] = useState<string[]>(Array(6).fill(""));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const code = digits.join("");
    const ok = await verifyCode(docType, docNumber, code, channel);
    if (ok) onNext(code);
  };

  return (
    <form onSubmit={handleSubmit}>
      <div className="space-y-5">
        <div>
          <Label className="text-gray-500 mb-2 block">
            Código enviado por {channel === "EMAIL" ? "correo electrónico" : "SMS"}
          </Label>
          <OtpInput value={digits} onChange={setDigits} disabled={loading} />
        </div>
        <button
          type="submit"
          disabled={loading || digits.join("").length < 6}
          className="flex w-full items-center justify-center rounded-lg bg-brand-500 px-4 py-3 text-sm font-medium text-white transition hover:bg-brand-600 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? "Verificando..." : "Verificar código"}
        </button>
      </div>
    </form>
  );
};
