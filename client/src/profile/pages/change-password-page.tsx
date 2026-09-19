import { useState } from "react";
import { useNavigate } from "react-router";
import { ModuleBase } from "@/ui/components/common/module-base";
import { Card, CardTitle } from "@/ui/components/card";
import { Input } from "@/ui/components/inputs/input";
import { Button } from "@/ui/components/button/button";
import { useChangePassword } from "@/auth/hooks/use-change-password";

export const ChangePasswordPage: React.FC = () => {
  const navigate = useNavigate();
  const { changePassword, loading, error } = useChangePassword();
  const [form, setForm] = useState({ current: "", next: "", confirm: "" });
  const [localError, setLocalError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLocalError(null);
    if (form.next !== form.confirm) {
      setLocalError("Las contraseñas nuevas no coinciden.");
      return;
    }
    const ok = await changePassword(form.current, form.next);
    if (ok) {
      setSuccess(true);
      setTimeout(() => navigate("/profile"), 1500);
    }
  };

  const displayError = localError ?? error;

  return (
    <ModuleBase
      pageTitle="Cambiar contraseña"
      breadcrumbItems={[{ label: "Perfil", path: "/profile" }]}
    >
      <form onSubmit={handleSubmit}>
        <Card>
          <CardTitle>Cambiar contraseña</CardTitle>
          <div className="flex flex-col gap-5 max-w-md">
            <Input
              label="Contraseña actual"
              id="current"
              type="password"
              value={form.current}
              onChange={(e) => setForm((p) => ({ ...p, current: e.target.value }))}
              placeholder="••••••••"
              required
            />
            <Input
              label="Nueva contraseña"
              id="next"
              type="password"
              value={form.next}
              onChange={(e) => setForm((p) => ({ ...p, next: e.target.value }))}
              placeholder="••••••••"
              required
            />
            <Input
              label="Confirmar nueva contraseña"
              id="confirm"
              type="password"
              value={form.confirm}
              onChange={(e) => setForm((p) => ({ ...p, confirm: e.target.value }))}
              placeholder="••••••••"
              required
            />
          </div>
        </Card>

        {displayError && <p className="mt-4 text-sm text-error-500">{displayError}</p>}
        {success && <p className="mt-4 text-sm text-success-500">Contraseña actualizada. Redirigiendo...</p>}

        <div className="flex items-center justify-end gap-3 mt-5">
          <Button type="button" size="sm" variant="outline" onClick={() => navigate("/profile")}>
            Cancelar
          </Button>
          <Button type="submit" size="sm" disabled={success} loading={loading} loadingText="Guardando...">
            Guardar
          </Button>
        </div>
      </form>
    </ModuleBase>
  );
};
