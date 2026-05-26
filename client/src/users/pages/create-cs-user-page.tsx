import { useState } from "react";
import { useNavigate } from "react-router";
import { ModuleBase } from "@/ui/components/common/module-base";
import { Card, CardTitle } from "@/ui/components/card";
import { Input } from "@/ui/components/input";
import { useCreateCsUser } from "../hooks/use-create-cs-user";

const INITIAL_FORM = {
  firstname: "",
  lastname: "",
  email: "",
  phoneNumber: "",
  password: "",
};

export const CreateCsUserPage: React.FC = () => {
  const navigate = useNavigate();
  const { createCsUser, loading, error } = useCreateCsUser();
  const [form, setForm] = useState(INITIAL_FORM);

  const handleChange = (field: keyof typeof INITIAL_FORM, value: string) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const result = await createCsUser({
      ...form,
      role: "ATENCION AL CLIENTE",
    });
    if (result) navigate("/my-users");
  };

  return (
    <ModuleBase
      pageTitle="Nuevo agente de soporte"
      breadcrumbItems={[{ label: "Usuarios", path: "/my-users" }]}
    >
      <form onSubmit={handleSubmit} className="max-w-2xl">
        <Card>
          <CardTitle>Información del agente</CardTitle>
          <div className="grid grid-cols-1 gap-5 sm:grid-cols-2">
            <Input
              label="Nombre"
              id="firstname"
              value={form.firstname}
              onChange={(e) => handleChange("firstname", e.target.value)}
              placeholder="Nombre"
              required
            />
            <Input
              label="Apellido"
              id="lastname"
              value={form.lastname}
              onChange={(e) => handleChange("lastname", e.target.value)}
              placeholder="Apellido"
              required
            />
            <Input
              label="Email"
              id="email"
              type="email"
              value={form.email}
              onChange={(e) => handleChange("email", e.target.value)}
              placeholder="correo@ejemplo.com"
              required
            />
            <Input
              label="Teléfono"
              id="phoneNumber"
              value={form.phoneNumber}
              onChange={(e) => handleChange("phoneNumber", e.target.value)}
              placeholder="+57 300 000 0000"
              required
            />
            <div className="sm:col-span-2">
              <Input
                label="Contraseña temporal"
                id="password"
                type="password"
                value={form.password}
                onChange={(e) => handleChange("password", e.target.value)}
                placeholder="Mínimo 8 caracteres"
                required
              />
            </div>
          </div>

          {error && <p className="mt-4 text-sm text-error-500">{error}</p>}

          <div className="flex items-center justify-end gap-3 mt-6 pt-5 border-t border-gray-100 dark:border-gray-800">
            <button
              type="button"
              onClick={() => navigate("/my-users")}
              className="rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm font-medium text-gray-700 shadow-theme-xs hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-300"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={loading}
              className="rounded-lg bg-brand-500 px-4 py-2.5 text-sm font-medium text-white shadow-theme-xs hover:bg-brand-600 disabled:opacity-50"
            >
              {loading ? "Creando..." : "Crear agente"}
            </button>
          </div>
        </Card>
      </form>
    </ModuleBase>
  );
};
