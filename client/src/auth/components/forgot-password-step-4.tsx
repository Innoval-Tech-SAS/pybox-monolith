import { useState } from "react";
import { PasswordInput } from "@/ui/components/inputs/password-input";
import { useToast } from "@/context/toast-context";
import { useForgotPassword } from "../hooks/use-forgot-password";
import type { ForgotPasswordStep4Props } from "@/auth/types/props/forgot-password-step-4-props";

export const ForgotPasswordStep4: React.FC<ForgotPasswordStep4Props> = ({
  docType,
  docNumber,
  code,
  channel,
  onSuccess,
  loading,
}) => {
  const { resetPassword } = useForgotPassword();
  const { error: toastError } = useToast();
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (newPassword !== confirmPassword) {
      toastError("Error", "Las contraseñas no coinciden.");
      return;
    }
    const ok = await resetPassword(docType, docNumber, code, channel, newPassword);
    if (ok) onSuccess();
  };

  return (
    <form onSubmit={handleSubmit}>
      <div className="space-y-5">
        <PasswordInput
          id="forgot-password-new-password"
          label="Nueva contraseña *"
          placeholder="Nueva contraseña"
          value={newPassword}
          onChange={(e) => setNewPassword(e.target.value)}
          required
          autoComplete="new-password"
        />
        <PasswordInput
          id="forgot-password-confirm-password"
          label="Confirmar contraseña *"
          placeholder="Confirmar contraseña"
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
          required
          autoComplete="new-password"
        />
        <button
          type="submit"
          disabled={loading || !newPassword}
          className="flex w-full items-center justify-center rounded-lg bg-brand-500 px-4 py-3 text-sm font-medium text-white transition hover:bg-brand-600 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? "Guardando..." : "Restablecer contraseña"}
        </button>
      </div>
    </form>
  );
};
