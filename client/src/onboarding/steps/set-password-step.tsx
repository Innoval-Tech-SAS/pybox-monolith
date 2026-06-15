import React, { useState } from "react";
import { Input } from "@/ui/components/inputs/input";
import { Label } from "@/ui/components/inputs/label";
import { useSetOnboardingPassword } from "@/hooks/use-set-onboarding-password";
import type { SetPasswordStepProps } from "@/onboarding/types/set-password-step-props";

export const SetPasswordStep: React.FC<SetPasswordStepProps> = ({ onDone }) => {
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const { setPassword: savePassword, loading, error } = useSetOnboardingPassword();

  const mismatch = confirm.length > 0 && password !== confirm;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (mismatch || !password) return;
    try {
      await savePassword(password);
      onDone();
    } catch {
      // error handled by hook
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      <div>
        <h2 className="text-lg font-semibold text-gray-800 dark:text-white/90">
          Crea tu contraseña
        </h2>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Tu cuenta fue creada con una contraseña temporal. Establece una contraseña propia para continuar.
        </p>
      </div>

      <div>
        <Label className="text-gray-500">Nueva contraseña</Label>
        <Input
          type="password"
          placeholder="Mínimo 8 caracteres"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
      </div>

      <div>
        <Label className="text-gray-500">Confirmar contraseña</Label>
        <Input
          type="password"
          placeholder="Repite la contraseña"
          value={confirm}
          onChange={(e) => setConfirm(e.target.value)}
        />
        {mismatch && (
          <p className="mt-1 text-xs text-error-500">Las contraseñas no coinciden</p>
        )}
      </div>

      {error && <p className="text-sm text-error-500">{error}</p>}

      <button
        type="submit"
        disabled={loading || !password || !confirm || mismatch}
        className="flex w-full items-center justify-center rounded-lg bg-brand-500 px-4 py-3 text-sm font-medium text-white transition hover:bg-brand-600 disabled:opacity-50"
      >
        {loading ? "Guardando..." : "Continuar"}
      </button>
    </form>
  );
};
