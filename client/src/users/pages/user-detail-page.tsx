import { Link, useNavigate, useParams } from "react-router";
import { ModuleBase } from "@/ui/components/common/module-base";
import { Badge } from "@/ui/components/badge";
import { Card, CardTitle } from "@/ui/components/card";
import { useUser } from "../hooks/use-user";

const InfoRow = ({ label, value }: { label: string; value: React.ReactNode }) => (
  <div>
    <p className="mb-1 text-xs leading-normal text-gray-500 dark:text-gray-400">{label}</p>
    <p className="text-sm font-medium text-gray-800 dark:text-white/90">{value || "—"}</p>
  </div>
);

const BoolBadge = ({ value, trueLabel = "Sí", falseLabel = "No" }: { value: boolean; trueLabel?: string; falseLabel?: string }) => (
  <Badge size="sm" color={value ? "success" : "light"} variant="light">
    {value ? trueLabel : falseLabel}
  </Badge>
);

const SCOPE_LABELS: Record<string, string> = {
  GLOBAL: "Global",
  ORGANIZATION: "Empresa",
  SELF: "Personal",
};

export const UserDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { user, loading, notFound } = useUser(id);

  if (loading) {
    return (
      <ModuleBase pageTitle="Usuario" breadcrumbItems={[{ label: "Usuarios", path: "/my-users" }]}>
        <div className="flex items-center justify-center h-48 text-gray-400">Cargando...</div>
      </ModuleBase>
    );
  }

  if (notFound || !user) {
    return (
      <ModuleBase pageTitle="Usuario no encontrado" breadcrumbItems={[{ label: "Usuarios", path: "/my-users" }]}>
        <div className="flex flex-col items-center justify-center h-48 gap-4">
          <p className="text-gray-500">Usuario no encontrado.</p>
        </div>
      </ModuleBase>
    );
  }

  return (
    <ModuleBase
      pageTitle={user.fullName}
      breadcrumbItems={[{ label: "Usuarios", path: "/my-users" }]}
    >
      <div className="flex flex-col gap-5">
        {/* Header actions */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Badge color={user.isActive ? "success" : "error"} variant="light" size="sm">
              {user.isActive ? "Activo" : "Inactivo"}
            </Badge>
            <span className="text-sm text-gray-500">{user.email}</span>
          </div>
          <Link
            to={`/my-users/${user.id}/edit`}
            className="inline-flex items-center gap-2 rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-theme-xs hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-white/5"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
            Editar
          </Link>
        </div>

        <div className="grid grid-cols-1 gap-5 lg:grid-cols-2">
          {/* Información personal */}
          <Card>
            <CardTitle>Información personal</CardTitle>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <InfoRow label="Nombre" value={user.firstname} />
              <InfoRow label="Apellido" value={user.lastname} />
              <InfoRow label="Email" value={user.email} />
              <InfoRow label="Teléfono" value={user.phoneNumber} />
              <InfoRow label="Tipo documento" value={user.documentType} />
              <InfoRow label="N° documento" value={user.documentNumber} />
              <InfoRow label="Proveedor auth" value={user.authProvider} />
              <InfoRow
                label="Registrado"
                value={user.createdAt ? new Date(user.createdAt).toLocaleDateString("es-CO", { day: "2-digit", month: "short", year: "numeric" }) : null}
              />
            </div>
          </Card>

          {/* Estado y seguridad */}
          <Card>
            <CardTitle>Estado y seguridad</CardTitle>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <p className="mb-1 text-xs text-gray-500 dark:text-gray-400">Cuenta activa</p>
                <BoolBadge value={user.isActive} trueLabel="Activa" falseLabel="Inactiva" />
              </div>
              <div>
                <p className="mb-1 text-xs text-gray-500 dark:text-gray-400">Sesión activa</p>
                <BoolBadge value={user.isActiveSessions} trueLabel="En línea" falseLabel="Desconectado" />
              </div>
              <div>
                <p className="mb-1 text-xs text-gray-500 dark:text-gray-400">Email verificado</p>
                <BoolBadge value={user.isEmailVerified} />
              </div>
              <div>
                <p className="mb-1 text-xs text-gray-500 dark:text-gray-400">Teléfono verificado</p>
                <BoolBadge value={user.isPhoneVerified} />
              </div>
              <div>
                <p className="mb-1 text-xs text-gray-500 dark:text-gray-400">MFA habilitado</p>
                <BoolBadge value={user.mfaEnabled} />
              </div>
              {user.updatedAt && (
                <InfoRow
                  label="Última actualización"
                  value={new Date(user.updatedAt).toLocaleDateString("es-CO", { day: "2-digit", month: "short", year: "numeric" })}
                />
              )}
            </div>
          </Card>

          {/* Roles */}
          {user.roles.length > 0 && (
            <Card className="lg:col-span-2">
              <CardTitle>Roles y acceso</CardTitle>
              <div className="flex flex-col gap-3">
                {user.roles.map((r, i) => (
                  <div key={i} className="flex items-center justify-between rounded-lg border border-gray-100 dark:border-gray-800 px-4 py-3">
                    <div className="flex items-center gap-3">
                      <Badge color="primary" variant="light" size="sm">{r.role}</Badge>
                      <Badge color="light" variant="light" size="sm">{SCOPE_LABELS[r.scope] ?? r.scope}</Badge>
                    </div>
                    {r.orgName && (
                      <span className="text-sm text-gray-500 dark:text-gray-400">{r.orgName}</span>
                    )}
                  </div>
                ))}
              </div>
            </Card>
          )}
        </div>
      </div>
    </ModuleBase>
  );
};
