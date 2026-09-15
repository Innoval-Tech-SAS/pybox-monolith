import { useState } from "react";
import { useNavigate, useSearchParams, useLocation } from "react-router";
import { CheckCircle, UserPlus, Settings2, FolderOpen, User, ShieldCheck, PartyPopper } from "lucide-react";
import { ModuleBase } from "@/ui/components/common/module-base";
import { Label } from "@/ui/components/inputs/label";
import { PasswordInput } from "@/ui/components/inputs/password-input";
import { useCreateCsUser } from "../hooks/use-create-cs-user";
import { useCreateOrgMember } from "../hooks/use-create-org-member";
import { CreateUserStepSidebar } from "../components/create-user-step-sidebar";
import { CreateUserPermissionCheckboxes } from "../components/create-user-permission-checkboxes";
import { CreateUserPortfolioCheckboxes } from "../components/create-user-portfolio-checkboxes";
import { ROLE_LABELS, GLOBAL_ROLE_LABELS, IS_USER_ORG, INPUT_BASE, CREATE_USER_INITIAL_FORM } from "../constants/create-user-constants";
import type { ManagedUserCreate } from "@/types/users/managed-user-types";
import type { CreateUserStepDef } from "@/users/types/create-user-step-def";

export const CreateUserPage: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { state } = useLocation() as { state?: { role?: string } };
  const role = state?.role ?? "";
  const orgId = searchParams.get("org") ?? "";

  const { createCsUser, loading: loadingGlobal, error: errorGlobal } = useCreateCsUser();
  const { createOrgMember, loading: loadingOrg, error: errorOrg } = useCreateOrgMember();

  const [form, setForm] = useState(CREATE_USER_INITIAL_FORM);
  const [step, setStep] = useState(1);
  const [createdUserId, setCreatedUserId] = useState<string | null>(null);

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

  const stepDefs: CreateUserStepDef[] = [
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
            required aria-required="true" className={INPUT_BASE} />
        </div>
        <div>
          <Label htmlFor="lastname">Apellido <span className="text-error-500">*</span></Label>
          <input id="lastname" type="text" placeholder="Apellido" value={form.lastname}
            onChange={(e) => setForm((p) => ({ ...p, lastname: e.target.value }))}
            required aria-required="true" className={INPUT_BASE} />
        </div>
        <div>
          <Label htmlFor="email">Correo electrónico <span className="text-error-500">*</span></Label>
          <input id="email" type="email" placeholder="correo@ejemplo.com" value={form.email}
            onChange={(e) => setForm((p) => ({ ...p, email: e.target.value }))}
            required aria-required="true" className={INPUT_BASE} />
        </div>
        <div>
          <Label htmlFor="phoneNumber">Teléfono <span className="text-error-500">*</span></Label>
          <input id="phoneNumber" type="text" placeholder="+57 300 000 0000" value={form.phoneNumber}
            onChange={(e) => setForm((p) => ({ ...p, phoneNumber: e.target.value }))}
            required aria-required="true" className={INPUT_BASE} />
        </div>
        <div className="sm:col-span-2">
          <PasswordInput
            id="password"
            label="Contraseña temporal *"
            placeholder="Mínimo 8 caracteres"
            value={form.password}
            onChange={(e) => setForm((p) => ({ ...p, password: e.target.value }))}
            required
            minLength={8}
            autoComplete="new-password"
          />
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
        <CreateUserPermissionCheckboxes orgId={orgId} userId={createdUserId!} />
      </div>

      <div>
        <div className="mb-4 flex items-center gap-2">
          <FolderOpen size={15} className="text-gray-500" />
          <span className="text-sm font-semibold text-gray-700 dark:text-gray-300">Portafolios</span>
        </div>
        <CreateUserPortfolioCheckboxes orgId={orgId} userId={createdUserId!} />
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
          <CreateUserStepSidebar steps={stepDefs} current={step} />
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
