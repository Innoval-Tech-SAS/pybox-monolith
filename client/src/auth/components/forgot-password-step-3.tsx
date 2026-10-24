import { useState } from "react";
import { Label } from "@/ui/components/inputs/label";
import { OtpInput } from "@/ui/components/inputs/otp-input";
import { Button } from "@/ui/components/button/button";
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
        <Button
          type="submit"
          size="sm"
          className="w-full"
          disabled={digits.join("").length < 6}
          loading={loading}
          loadingText="Verificando..."
        >
          Verificar código
        </Button>
      </div>
    </form>
  );
};
