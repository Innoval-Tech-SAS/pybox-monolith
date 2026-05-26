import { useState } from "react";
import { useNavigate, useSearchParams } from "react-router";
import { ModuleBase } from "@/ui/components/common/module-base";
import { Card, CardTitle } from "@/ui/components/card";
import { Input } from "@/ui/components/input";
import { useCreateCsUser } from "../hooks/use-create-cs-user";
import { useCreateOrgMember } from "../hooks/use-create-org-member";
import type { ManagedUserCreate } from "@/types/users/managed-user-types";

const ROLE_LABELS: Record<string, string> = {
  "ADMINISTRADOR": "Administrador",
  "ATENCION AL CLIENTE": "Agente de soporte",
  "USUARIO ORGANIZACIÓN": "Usuario de organización",
};

const INITIAL_FORM = {
  firstname: "",
  lastname: "",
  email: "",
  phoneNumber: "",
  password: "",
};

export const CreateUserPage: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const role = searchParams.get("role") ?? "";
  const orgId = searchParams.get("org") ?? "";

  const { createCsUser, loading: loadingGlobal, error: errorGlobal } = useCreateCsUser();
  const { createOrgMember, loading: loadingOrg, error: errorOrg } = useCreateOrgMember();

  const [form, setForm] = useState(INITIAL_FORM);

  const loading = orgId ? loadingOrg : loadingGlobal;
  const error = orgId ? errorOrg : errorGlobal;
  const roleLabel = ROLE_LABELS[role] ?? role;
  const backPath = orgId ? `/my-companies/users?org=${orgId}` : "/my-users";

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const payload: ManagedUserCreate = {
      ...form,
      role: role as ManagedUserCreate["role"],
    };
    const result = orgId
      ? await createOrgMember(orgId, payload)
      : await createCsUser(payload);
    if (result) navigate(backPath);
  };

  return (
    <ModuleBase
      pageTitle={`Nuevo ${roleLabel.toLowerCase()}`}
      breadcrumbItems={[{ label: "Usuarios", path: backPath }]}
    >
      <form onSubmit={handleSubmit} className="max-w-2xl">
        <Card>
          <CardTitle>{roleLabel}</CardTitle>
          <div className="grid grid-cols-1 gap-5 sm:grid-cols-2">
            <Input
              label="Nombre"
              id="firstname"
              value={form.firstname}
              onChange={(e) => setForm((p) => ({ ...p, firstname: e.target.value }))}
              placeholder="Nombre"
              required
            />
            <Input
              label="Apellido"
              id="lastname"
              value={form.lastname}
              onChange={(e) => setForm((p) => ({ ...p, lastname: e.target.value }))}
              placeholder="Apellido"
              required
            />
            <Input
              label="Email"
              id="email"
              type="email"
              value={form.email}
              onChange={(e) => setForm((p) => ({ ...p, email: e.target.value }))}
              placeholder="correo@ejemplo.com"
              required
            />
            <Input
              label="Teléfono"
              id="phoneNumber"
              value={form.phoneNumber}
              onChange={(e) => setForm((p) => ({ ...p, phoneNumber: e.target.value }))}
              placeholder="+57 300 000 0000"
              required
            />
            <div className="sm:col-span-2">
              <Input
                label="Contraseña temporal"
                id="password"
                type="password"
                value={form.password}
                onChange={(e) => setForm((p) => ({ ...p, password: e.target.value }))}
                placeholder="Mínimo 8 caracteres"
                required
              />
            </div>
          </div>

          {error && <p className="mt-4 text-sm text-error-500">{error}</p>}

          <div className="flex items-center justify-end gap-3 mt-6 pt-5 border-t border-gray-100 dark:border-gray-800">
            <button
              type="button"
              onClick={() => navigate(backPath)}
              className="rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm font-medium text-gray-700 shadow-theme-xs hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-300"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={loading}
              className="rounded-lg bg-brand-500 px-4 py-2.5 text-sm font-medium text-white shadow-theme-xs hover:bg-brand-600 disabled:opacity-50"
            >
              {loading ? "Creando..." : `Crear ${roleLabel.toLowerCase()}`}
            </button>
          </div>
        </Card>
      </form>
    </ModuleBase>
  );
};
