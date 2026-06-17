import { useState } from "react";
import { useNavigate, useSearchParams, useLocation } from "react-router";
import { CheckCircle, UserPlus, Settings2, FolderOpen, User, ShieldCheck, PartyPopper, Eye, EyeOff } from "lucide-react";
import { ModuleBase } from "@/ui/components/common/module-base";
import { Label } from "@/ui/components/inputs/label";
import { useCreateCsUser } from "../hooks/use-create-cs-user";
import { useCreateOrgMember } from "../hooks/use-create-org-member";
import { usePermissionsCatalog } from "../hooks/use-permissions-catalog";
import { useUserPermissions } from "../hooks/use-user-permissions";
import { useUserPortfolioAccess } from "../hooks/use-user-portfolio-access";
import type { ManagedUserCreate } from "@/types/users/managed-user-types";
import type { CreateUserStepDef } from "@/users/types/create-user-step-def";

const ROLE_LABELS: Record<string, string> = {
  ADMINISTRADOR: "Administrador",
  "ATENCION AL CLIENTE": "Agente de soporte",
  "USUARIO ORGANIZACIÓN": "Usuario",
  USUARIO: "Usuario",
};

const GLOBAL_ROLE_LABELS: Record<string, string> = {
  ADMINISTRADOR: "Administrador",
  "ATENCION AL CLIENTE": "Soporte técnico",
};

const IS_USER_ORG = "USUARIO ORGANIZACIÓN";

const INPUT_BASE =
  "h-11 w-full rounded-lg border appearance-none px-4 py-2.5 text-sm shadow-theme-xs placeholder:text-gray-400 focus:outline-hidden focus:ring-3 bg-transparent text-gray-800 border-gray-300 focus:border-brand-300 focus:ring-brand-500/20 dark:bg-gray-900 dark:text-white/90 dark:placeholder:text-white/30 dark:border-gray-700 dark:focus:border-brand-800";

// ─── Vertical step sidebar ───────────────────────────────────────────────────

const StepSidebar: React.FC<{ steps: CreateUserStepDef[]; current: number }> = ({ steps, current }) => (
  <div className="flex flex-col gap-0">
    {steps.map((s, i) => {
      const n = i + 1;
      const done = n < current;
      const active = n === current;
      return (
        <div key={n} className="flex gap-4">
          <div className="flex flex-col items-center">
            <div
              className={`flex size-9 shrink-0 items-center justify-center rounded-full border-2 text-sm font-semibold transition-all ${
                done
                  ? "border-brand-500 bg-brand-500 text-white"
                  : active
                    ? "border-brand-500 bg-white text-brand-600 dark:bg-gray-900"
                    : "border-gray-200 bg-white text-gray-400 dark:border-gray-700 dark:bg-gray-900"
              }`}
            >
              {done ? <CheckCircle size={16} /> : s.icon}
            </div>
            {i < steps.length - 1 && (
              <div
                className={`w-px flex-1 min-h-10 my-1 transition-colors ${
                  done ? "bg-brand-500" : "bg-gray-200 dark:bg-gray-700"
                }`}
              />
            )}
          </div>
          <div className="pb-8">
            <p
              className={`text-sm font-semibold leading-9 ${
                active
                  ? "text-gray-800 dark:text-white/90"
                  : done
                    ? "text-brand-600 dark:text-brand-400"
                    : "text-gray-400 dark:text-gray-600"
              }`}
            >
              {s.label}
            </p>
            <p
              className={`text-xs -mt-1 ${
                active || done ? "text-gray-500 dark:text-gray-400" : "text-gray-300 dark:text-gray-700"
              }`}
            >
              {s.description}
            </p>
          </div>
        </div>
      );
    })}
  </div>
);

// ─── Step 2 sub-components ───────────────────────────────────────────────────

const PermissionCheckboxes: React.FC<{ orgId: string; userId: string }> = ({ orgId, userId }) => {
  const { catalog, loading } = usePermissionsCatalog();
  const { permissions, assignPermission, removePermission } = useUserPermissions(orgId, userId);
  const [busy, setBusy] = useState<string | null>(null);
  const [localOverride, setLocalOverride] = useState<Set<string> | null>(null);

  const serverGranted = new Set(permissions.filter((p) => p.effect === "GRANT").map((p) => p.name));
  const effective = localOverride ?? serverGranted;

  const toggle = async (name: string, checked: boolean) => {
    setBusy(name);
    const base = localOverride ?? serverGranted;
    const next = new Set(base);
    checked ? next.add(name) : next.delete(name);
    setLocalOverride(next);
    const ok = checked ? await assignPermission(name, "GRANT") : await removePermission(name);
    if (!ok) setLocalOverride(base);
    setBusy(null);
  };

  if (loading) return <p className="text-sm text-gray-400">Cargando...</p>;
  if (catalog.length === 0) return <p className="text-sm text-gray-400">No hay permisos configurados.</p>;

  return (
    <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-3">
      {catalog.map((perm) => {
        const checked = effective.has(perm.name);
        const isBusy = busy === perm.name;
        return (
          <label
            key={perm.name}
            className="flex items-start gap-3 rounded-lg border border-gray-200 p-3 cursor-pointer hover:bg-gray-50 dark:border-gray-700 dark:hover:bg-white/5"
          >
            <input
              type="checkbox"
              checked={checked}
              disabled={isBusy}
              onChange={(e) => toggle(perm.name, e.target.checked)}
              className="mt-0.5 h-4 w-4 rounded border-gray-300 text-brand-500 focus:ring-brand-500"
            />
            <span>
              <span className="block text-sm font-medium text-gray-800 dark:text-white/90">
                {perm.label ?? perm.name}
              </span>
              {perm.description && (
                <span className="block text-xs text-gray-400 dark:text-gray-500 mt-0.5">
                  {perm.description}
                </span>
              )}
            </span>
          </label>
        );
      })}
    </div>
  );
};

const PortfolioCheckboxes: React.FC<{ orgId: string; userId: string }> = ({ orgId, userId }) => {
  const { portfolios, loading, grantAccess, revokeAccess } = useUserPortfolioAccess(orgId, userId);
  const [busy, setBusy] = useState<string | null>(null);

  const toggle = async (portfolioId: string, checked: boolean) => {
    setBusy(portfolioId);
    if (checked) await grantAccess(portfolioId);
    else await revokeAccess(portfolioId);
    setBusy(null);
  };

  if (loading) return <p className="text-sm text-gray-400">Cargando...</p>;
  if (portfolios.length === 0)
    return <p className="text-sm text-gray-400">No hay portafolios disponibles en esta empresa.</p>;

  return (
    <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-3">
      {portfolios.map((p) => {
        const isBusy = busy === p.portfolio_id;
        return (
          <label
            key={p.portfolio_id}
            className="flex items-center gap-3 rounded-lg border border-gray-200 p-3 cursor-pointer hover:bg-gray-50 dark:border-gray-700 dark:hover:bg-white/5"
          >
            <input
              type="checkbox"
              checked={p.has_access}
              disabled={isBusy}
              onChange={(e) => toggle(p.portfolio_id, e.target.checked)}
              className="h-4 w-4 rounded border-gray-300 text-brand-500 focus:ring-brand-500"
            />
            <span className="text-sm font-medium text-gray-800 dark:text-white/90">{p.name}</span>
          </label>
        );
      })}
    </div>
  );
};

// ─── Main page ───────────────────────────────────────────────────────────────

const INITIAL_FORM = { firstname: "", lastname: "", email: "", phoneNumber: "", password: "" };

export const CreateUserPage: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { state } = useLocation() as { state?: { role?: string } };
  const role = state?.role ?? "";
  const orgId = searchParams.get("org") ?? "";

  const { createCsUser, loading: loadingGlobal, error: errorGlobal } = useCreateCsUser();
  const { createOrgMember, loading: loadingOrg, error: errorOrg } = useCreateOrgMember();

  const [form, setForm] = useState(INITIAL_FORM);
  const [step, setStep] = useState(1);
  const [createdUserId, setCreatedUserId] = useState<number | null>(null);
  const [showPassword, setShowPassword] = useState(false);

  const isUserOrg = role === IS_USER_ORG;
  const hasStep2 = isUserOrg && !!orgId;
  const loading = orgId ? loadingOrg : loadingGlobal;
  const error = orgId ? errorOrg : errorGlobal;
  const roleLabel = ROLE_LABELS[role] ?? role;
  const backPath = orgId ? `/my-companies/users?org=${orgId}` : "/my-users";

  const isGlobalContext = !orgId;
  const pageTitle = isGlobalContext ? "Nuevo usuario" : `Nuevo ${roleLabel.toLowerCase()}`;
  const breadcrumbItems = isGlobalContext
    ? [{ label: "Usuarios", path: backPath }, { label: GLOBAL_ROLE_LABELS[role] ?? roleLabel }]
    : [{ label: "Usuarios", path: backPath }];

  const stepDefs: StepDef[] = [
    { label: "Datos", description: "Información de la cuenta", icon: <User size={14} /> },
    ...(hasStep2
      ? [{ label: "Acceso", description: "Módulos y portafolios", icon: <ShieldCheck size={14} /> }]
      : []),
    { label: "Listo", description: "Cuenta creada", icon: <PartyPopper size={14} /> },
  ];

  const totalSteps = stepDefs.length;

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    const payload: ManagedUserCreate = { ...form, role: role as ManagedUserCreate["role"] };
    const result = orgId ? await createOrgMember(orgId, payload) : await createCsUser(payload);
    if (!result) return;
    setCreatedUserId(result.id);
    setStep(hasStep2 ? 2 : totalSteps);
  };

  // ── Step 1 ──
  const renderStep1 = () => (
    <form onSubmit={handleCreate} className="space-y-8">
      <div>
        <h2 className="text-xl font-bold text-gray-800 dark:text-white/90">
          Datos del {roleLabel.toLowerCase()}
        </h2>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Completa la información básica para crear la cuenta.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
        <div>
          <Label htmlFor="firstname">Nombre <span className="text-error-500">*</span></Label>
          <input id="firstname" type="text" placeholder="Nombre" value={form.firstname}
            onChange={(e) => setForm((p) => ({ ...p, firstname: e.target.value }))}
            required className={INPUT_BASE} />
        </div>
        <div>
          <Label htmlFor="lastname">Apellido <span className="text-error-500">*</span></Label>
          <input id="lastname" type="text" placeholder="Apellido" value={form.lastname}
            onChange={(e) => setForm((p) => ({ ...p, lastname: e.target.value }))}
            required className={INPUT_BASE} />
        </div>
        <div>
          <Label htmlFor="email">Correo electrónico <span className="text-error-500">*</span></Label>
          <input id="email" type="email" placeholder="correo@ejemplo.com" value={form.email}
            onChange={(e) => setForm((p) => ({ ...p, email: e.target.value }))}
            required className={INPUT_BASE} />
        </div>
        <div>
          <Label htmlFor="phoneNumber">Teléfono <span className="text-error-500">*</span></Label>
          <input id="phoneNumber" type="text" placeholder="+57 300 000 0000" value={form.phoneNumber}
            onChange={(e) => setForm((p) => ({ ...p, phoneNumber: e.target.value }))}
            required className={INPUT_BASE} />
        </div>
        <div className="sm:col-span-2">
          <Label htmlFor="password">Contraseña temporal <span className="text-error-500">*</span></Label>
          <div className="relative">
            <input id="password" type={showPassword ? "text" : "password"} placeholder="Mínimo 8 caracteres" value={form.password}
              onChange={(e) => setForm((p) => ({ ...p, password: e.target.value }))}
              required minLength={8} className={INPUT_BASE} />
            <button type="button" onClick={() => setShowPassword((v) => !v)}
              className="absolute inset-y-0 right-3 flex items-center text-gray-400 hover:text-gray-600 dark:hover:text-gray-300">
              {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
            </button>
          </div>
        </div>
      </div>

      {error && <p className="text-sm text-error-500">{error}</p>}

      <div className="flex flex-col-reverse gap-3 sm:flex-row sm:justify-end pt-2">
        <button type="button" onClick={() => navigate(backPath)}
          className="inline-flex items-center justify-center gap-2 rounded-lg bg-white px-5 py-3 text-sm font-medium text-gray-700 ring-1 ring-inset ring-gray-300 transition hover:bg-gray-50 dark:bg-gray-800 dark:text-gray-400 dark:ring-gray-700 dark:hover:bg-white/3">
          Cancelar
        </button>
        <button type="submit" disabled={loading}
          className="inline-flex items-center justify-center gap-2 rounded-lg bg-brand-500 px-6 py-3 text-sm font-medium text-white shadow-theme-xs transition hover:bg-brand-600 disabled:opacity-50">
          <UserPlus size={16} />
          {loading ? "Creando..." : `Crear ${roleLabel.toLowerCase()}`}
        </button>
      </div>
    </form>
  );

  // ── Step 2 ──
  const renderStep2 = () => (
    <div className="space-y-8">
      <div>
        <h2 className="text-xl font-bold text-gray-800 dark:text-white/90">Permisos y portafolios</h2>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Usuario creado. Configura los módulos y portafolios a los que tendrá acceso.
        </p>
      </div>

      <div>
        <div className="mb-4 flex items-center gap-2">
          <Settings2 size={15} className="text-gray-500" />
          <span className="text-sm font-semibold text-gray-700 dark:text-gray-300">Módulos</span>
        </div>
        <PermissionCheckboxes orgId={orgId} userId={createdUserId!} />
      </div>

      <div>
        <div className="mb-4 flex items-center gap-2">
          <FolderOpen size={15} className="text-gray-500" />
          <span className="text-sm font-semibold text-gray-700 dark:text-gray-300">Portafolios</span>
        </div>
        <PortfolioCheckboxes orgId={orgId} userId={createdUserId!} />
      </div>

      <div className="flex flex-col-reverse gap-3 sm:flex-row sm:justify-end pt-2">
        <button type="button" onClick={() => setStep(totalSteps)}
          className="inline-flex items-center justify-center gap-2 rounded-lg bg-white px-5 py-3 text-sm font-medium text-gray-700 ring-1 ring-inset ring-gray-300 transition hover:bg-gray-50 dark:bg-gray-800 dark:text-gray-400 dark:ring-gray-700 dark:hover:bg-white/3">
          Omitir
        </button>
        <button type="button" onClick={() => setStep(totalSteps)}
          className="inline-flex items-center justify-center gap-2 rounded-lg bg-brand-500 px-6 py-3 text-sm font-medium text-white shadow-theme-xs transition hover:bg-brand-600">
          Finalizar configuración
        </button>
      </div>
    </div>
  );

  // ── Step 3 ──
  const renderStep3 = () => (
    <div className="flex flex-1 items-center justify-center py-20">
      <div className="flex flex-col items-center gap-6 text-center max-w-sm">
        <div className="flex size-20 items-center justify-center rounded-full bg-brand-50 dark:bg-brand-500/10">
          <CheckCircle className="size-10 text-brand-500" />
        </div>
        <div>
          <h5 className="mb-2 text-xl font-semibold text-gray-800 dark:text-white/90">
            {roleLabel} creado
          </h5>
          <p className="text-sm text-gray-500 dark:text-gray-400 leading-relaxed">
            La cuenta fue creada exitosamente y ya puede iniciar sesión.
          </p>
        </div>
        <button type="button" onClick={() => navigate(backPath)}
          className="w-full rounded-lg bg-brand-500 px-6 py-3 text-sm font-medium text-white transition hover:bg-brand-600">
          Ir a usuarios
        </button>
      </div>
    </div>
  );

  const currentContent =
    step === 1 ? renderStep1() :
    step === 2 && hasStep2 ? renderStep2() :
    renderStep3();

  return (
    <ModuleBase
      pageTitle={pageTitle}
      breadcrumbItems={breadcrumbItems}
    >
      <div className="flex gap-10">
        {/* Left sidebar — step indicator */}
        <aside className="hidden w-52 shrink-0 pt-1 lg:block">
          <StepSidebar steps={stepDefs} current={step} />
        </aside>

        {/* Vertical divider */}
        <div className="hidden lg:block w-px self-stretch bg-gray-100 dark:bg-white/5" />

        {/* Main content */}
        <div className="min-w-0 flex-1">
          {currentContent}
        </div>
      </div>
    </ModuleBase>
  );
};
