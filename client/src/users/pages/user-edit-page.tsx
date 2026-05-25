import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router";
import { ModuleBase } from "@/ui/components/common/module-base";
import { Card, CardTitle } from "@/ui/components/card";
import { Input } from "@/ui/components/input";
import { Switch } from "@/ui/components/switch";
import { useUser } from "../hooks/use-user";
import { useUpdateUser } from "../hooks/use-update-user";

export const UserEditPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { user, loading } = useUser(id);
  const { updateUser, loading: saving, error } = useUpdateUser();

  const [form, setForm] = useState({
    firstname: "",
    lastname: "",
    email: "",
    phoneNumber: "",
    isActive: true,
  });

  useEffect(() => {
    if (user) {
      setForm({
        firstname: user.firstname,
        lastname: user.lastname,
        email: user.email,
        phoneNumber: user.phoneNumber ?? "",
        isActive: user.isActive,
      });
    }
  }, [user]);

  const handleChange = (field: string, value: string) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user) return;
    const result = await updateUser(user.id, {
      firstname: form.firstname || undefined,
      lastname: form.lastname || undefined,
      email: form.email || undefined,
      phoneNumber: form.phoneNumber || undefined,
      isActive: form.isActive,
    });
    if (result) navigate(`/my-users/${user.id}`);
  };

  if (loading) {
    return (
      <ModuleBase pageTitle="Editar usuario" breadcrumbItems={[{ label: "Usuarios", path: "/my-users" }]}>
        <div className="flex items-center justify-center h-48 text-gray-400">Cargando...</div>
      </ModuleBase>
    );
  }

  if (!user) {
    return (
      <ModuleBase pageTitle="Usuario no encontrado" breadcrumbItems={[{ label: "Usuarios", path: "/my-users" }]}>
        <div className="flex flex-col items-center justify-center h-48 gap-4">
          <p className="text-gray-500">Usuario no encontrado.</p>
          <Link to="/my-users" className="text-brand-500 hover:underline text-sm">← Volver</Link>
        </div>
      </ModuleBase>
    );
  }

  return (
    <ModuleBase
      pageTitle={`Editar — ${user.fullName}`}
      breadcrumbItems={[
        { label: "Usuarios", path: "/my-users" },
        { label: user.fullName, path: `/my-users/${user.id}` },
      ]}
    >
      <form onSubmit={handleSubmit} className="max-w-2xl">
        <Card>
          <CardTitle>Información personal</CardTitle>
          <div className="grid grid-cols-1 gap-5 sm:grid-cols-2">
            <Input
              label="Nombre"
              id="firstname"
              value={form.firstname}
              onChange={(e) => handleChange("firstname", e.target.value)}
              placeholder="Nombre"
            />
            <Input
              label="Apellido"
              id="lastname"
              value={form.lastname}
              onChange={(e) => handleChange("lastname", e.target.value)}
              placeholder="Apellido"
            />
            <Input
              label="Email"
              id="email"
              type="email"
              value={form.email}
              onChange={(e) => handleChange("email", e.target.value)}
              placeholder="correo@ejemplo.com"
            />
            <Input
              label="Teléfono"
              id="phoneNumber"
              value={form.phoneNumber}
              onChange={(e) => handleChange("phoneNumber", e.target.value)}
              placeholder="+57 300 000 0000"
            />
            <div className="sm:col-span-2">
              <p className="mb-2 text-sm font-medium text-gray-700 dark:text-gray-400">Cuenta activa</p>
              <Switch
                checked={form.isActive}
                onChange={(v) => setForm((prev) => ({ ...prev, isActive: v }))}
                label={form.isActive ? "Activa" : "Inactiva"}
              />
            </div>
          </div>

          {error && <p className="mt-4 text-sm text-error-500">{error}</p>}

          <div className="flex items-center justify-end gap-3 mt-6 pt-5 border-t border-gray-100 dark:border-gray-800">
            <button
              type="button"
              onClick={() => navigate(-1)}
              className="rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm font-medium text-gray-700 shadow-theme-xs hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-300"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={saving}
              className="rounded-lg bg-brand-500 px-4 py-2.5 text-sm font-medium text-white shadow-theme-xs hover:bg-brand-600 disabled:opacity-50"
            >
              {saving ? "Guardando..." : "Guardar cambios"}
            </button>
          </div>
        </Card>
      </form>
    </ModuleBase>
  );
};
