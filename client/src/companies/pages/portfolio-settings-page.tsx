import { useState } from "react";
import { useSearchParams } from "react-router";
import { Check, Copy } from "lucide-react";
import { PageMeta } from "@/ui/pages/page-meta";
import { ModuleBase } from "@/ui/components/common/module-base";
import { Card, CardTitle } from "@/ui/components/card";
import { Loader } from "@/ui/components/loader/loader";
import { Badge } from "@/ui/components/badge";
import { Input } from "@/ui/components/inputs/input";
import { Label } from "@/ui/components/inputs/label";
import { CountrySelect } from "@/ui/components/inputs/country-select";
import { usePortfolioSettings } from "../hooks/use-portfolio-settings";
import { useMyCompanies } from "../hooks/use-my-companies";

const REACTIVATION_OPTIONS = [
  { value: "FROM_TODAY", label: "Desde hoy" },
  { value: "CATCH_UP", label: "Ponerse al día" },
];

const fmt = (iso: string | null | undefined) =>
  iso
    ? new Date(iso).toLocaleDateString("es-CO", { day: "2-digit", month: "short", year: "numeric" })
    : "—";

const InfoRow = ({ label, value, copyable = false }: { label: string; value?: string | null; copyable?: boolean }) => {
  const [copied, setCopied] = useState(false);
  return (
    <div>
      <p className="mb-1 text-xs text-gray-500 dark:text-gray-400">{label}</p>
      <p className="flex items-center gap-1 text-sm font-medium text-gray-800 dark:text-white/90">
        <span className={copyable ? "font-mono text-xs" : ""}>{value || "—"}</span>
        {copyable && value && (
          <button
            onClick={() => { navigator.clipboard.writeText(value); setCopied(true); setTimeout(() => setCopied(false), 2000); }}
            className="ml-0.5 inline-flex items-center rounded p-0.5 text-gray-400 hover:bg-gray-100 hover:text-gray-600 dark:hover:bg-gray-700 dark:hover:text-gray-300"
          >
            {copied ? <Check size={12} /> : <Copy size={12} />}
          </button>
        )}
      </p>
    </div>
  );
};

const EditIcon = () => (
  <svg className="fill-current" width="16" height="16" viewBox="0 0 18 18" fill="none">
    <path fillRule="evenodd" clipRule="evenodd" d="M15.0911 2.78206C14.2125 1.90338 12.7878 1.90338 11.9092 2.78206L4.57524 10.116C4.26682 10.4244 4.0547 10.8158 3.96468 11.2426L3.31231 14.3352C3.25997 14.5833 3.33653 14.841 3.51583 15.0203C3.69512 15.1996 3.95286 15.2761 4.20096 15.2238L7.29355 14.5714C7.72031 14.4814 8.11172 14.2693 8.42013 13.9609L15.7541 6.62695C16.6327 5.74827 16.6327 4.32365 15.7541 3.44497L15.0911 2.78206ZM12.9698 3.84272C13.2627 3.54982 13.7376 3.54982 14.0305 3.84272L14.6934 4.50563C14.9863 4.79852 14.9863 5.2734 14.6934 5.56629L14.044 6.21573L12.3204 4.49215L12.9698 3.84272ZM11.2597 5.55281L5.6359 11.1766C5.53309 11.2794 5.46238 11.4099 5.43238 11.5522L5.01758 13.5185L6.98394 13.1037C7.1262 13.0737 7.25666 13.003 7.35947 12.9002L12.9833 7.27639L11.2597 5.55281Z" fill="" />
  </svg>
);

export const PortfolioSettingsPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const orgId = searchParams.get("org") ?? "";
  const portfolioId = searchParams.get("portfolio") ?? "";

  const { portfolio, config, loading, saving, toggleActive, updateInfo, saveCounterConfig, syncCounterConfig } =
    usePortfolioSettings(portfolioId);
  const { orgs } = useMyCompanies();
  const orgName = orgs.find((o) => o.id === orgId)?.name ?? "Empresa";

  const [syncDate, setSyncDate] = useState("");
  const [isEditing, setIsEditing] = useState(false);
  const [form, setForm] = useState({ name: "", description: "", country: "" });

  const startEdit = () => {
    setForm({
      name: portfolio?.name ?? "",
      description: portfolio?.description ?? "",
      country: portfolio?.country ?? "",
    });
    setIsEditing(true);
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    await updateInfo({
      name: form.name || undefined,
      description: form.description || undefined,
      country: form.country || undefined,
    });
    setIsEditing(false);
  };

  return (
    <>
      <PageMeta title="Configuración" description="Configuración del portafolio" />
      <ModuleBase
        pageTitle="Configuración"
        breadcrumbItems={[
          { label: "Mis Empresas", path: "/my-companies" },
          ...(orgId ? [{ label: orgName, path: `/my-companies?org=${orgId}` }] : []),
          { label: "Portafolios", path: `/my-companies/portfolios?org=${orgId}` },
          ...(portfolioId
            ? [{ label: portfolio?.name ?? "Portafolio", path: `/my-companies/portfolios?org=${orgId}&portfolio=${portfolioId}` }]
            : []),
        ]}
      >
        {loading ? (
          <div className="py-20">
            <Loader />
          </div>
        ) : (
          <div className="flex flex-col gap-5">
            {/* ── Header ── */}
            <div className="rounded-2xl border border-gray-200 p-5 dark:border-gray-800 lg:p-6">
              {isEditing ? (
                <form onSubmit={handleSave} className="space-y-5">
                  <div className="grid grid-cols-1 gap-5 sm:grid-cols-2">
                    <div>
                      <Label>Nombre <span className="text-error-500">*</span></Label>
                      <Input
                        value={form.name}
                        onChange={(e) => setForm((p) => ({ ...p, name: e.target.value }))}
                        placeholder="Nombre del portafolio"
                        required
                      />
                    </div>
                    <div>
                      <Label>País</Label>
                      <CountrySelect
                        mode="NAME"
                        value={form.country}
                        onChange={(v) => setForm((p) => ({ ...p, country: v }))}
                        disabled={!!portfolio?.country}
                      />
                      {portfolio?.country && (
                        <p className="mt-1.5 text-xs text-gray-400 dark:text-gray-500">
                          El país no puede modificarse una vez asignado.
                        </p>
                      )}
                    </div>
                    <div className="sm:col-span-2">
                      <Label>Descripción</Label>
                      <textarea
                        value={form.description}
                        onChange={(e) => setForm((p) => ({ ...p, description: e.target.value }))}
                        placeholder="Descripción opcional"
                        rows={3}
                        className="w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/20 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:placeholder:text-white/30 dark:focus:border-brand-800"
                      />
                    </div>
                  </div>
                  <div className="flex items-center justify-end gap-3">
                    <button
                      type="button"
                      onClick={() => setIsEditing(false)}
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
                </form>
              ) : (
                <div className="flex flex-col gap-4 xl:flex-row xl:items-start xl:justify-between">
                  <div>
                    <div className="mb-1 flex flex-wrap items-center gap-2">
                      <h4 className="text-lg font-semibold text-gray-800 dark:text-white/90">
                        {portfolio?.name}
                      </h4>
                      <Badge color={portfolio?.isActive ? "success" : "error"} variant="light" size="sm">
                        {portfolio?.isActive ? "Activo" : "Inactivo"}
                      </Badge>
                    </div>
                    {portfolio?.description && (
                      <p className="text-sm text-gray-500 dark:text-gray-400">{portfolio.description}</p>
                    )}
                    <p className="mt-2 text-xs text-gray-400 dark:text-gray-500">
                      Creado: {fmt(portfolio?.createdAt)}
                      {portfolio?.updatedAt && ` · Actualizado: ${fmt(portfolio.updatedAt)}`}
                    </p>
                  </div>
                  <button
                    onClick={startEdit}
                    className="inline-flex shrink-0 items-center justify-center gap-2 rounded-full border border-gray-300 bg-white px-4 py-2.5 text-sm font-medium text-gray-700 shadow-theme-xs hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-white/5"
                  >
                    <EditIcon />
                    Editar
                  </button>
                </div>
              )}
            </div>

            {/* ── Info + Estado ── */}
            <div className="grid grid-cols-1 gap-5 lg:grid-cols-2">
              <Card>
                <CardTitle>Información</CardTitle>
                <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                  <InfoRow label="ID" value={portfolio?.id} copyable />
                  <InfoRow label="País" value={portfolio?.country} />
                  <InfoRow label="Organización" value={orgName} />
                </div>
              </Card>

              <Card>
                <CardTitle>Estado del portafolio</CardTitle>
                <label className="flex cursor-pointer items-center justify-between gap-4 rounded-xl border border-gray-200 p-4 dark:border-gray-800">
                  <div>
                    <p className="text-sm font-medium text-gray-800 dark:text-white/90">Portafolio activo</p>
                    <p className="mt-0.5 text-xs text-gray-500 dark:text-gray-400">
                      Al desactivar, los clientes no podrán visualizar esta cartera.
                    </p>
                  </div>
                  <div className="flex items-center gap-2 shrink-0">
                    {saving && (
                      <span className="h-4 w-4 animate-spin rounded-full border-2 border-brand-500 border-t-transparent" />
                    )}
                    <input
                      type="checkbox"
                      checked={portfolio?.isActive ?? false}
                      disabled={saving}
                      onChange={(e) => toggleActive(e.target.checked)}
                      className="h-4 w-4 rounded border-gray-300 text-brand-500 focus:ring-brand-500"
                    />
                  </div>
                </label>
              </Card>
            </div>

            {/* ── Actualización diaria ── */}
            <Card>
              <CardTitle>Actualización diaria</CardTitle>
              <p className="mb-4 text-sm text-gray-500 dark:text-gray-400">
                Configura la sincronización automática de contadores por día.
              </p>

              <div className="space-y-4">
                <label className="flex cursor-pointer items-center justify-between gap-4 rounded-xl border border-gray-200 p-4 dark:border-gray-800">
                  <div>
                    <p className="text-sm font-medium text-gray-800 dark:text-white/90">Actualización activa</p>
                    {config?.lastSyncedAt && (
                      <p className="mt-0.5 text-xs text-gray-400">
                        Última sync: {new Date(config.lastSyncedAt).toLocaleDateString("es-CO")}
                        {config.lastSyncedCutoffDate && ` (corte: ${config.lastSyncedCutoffDate})`}
                      </p>
                    )}
                  </div>
                  <div className="flex items-center gap-2 shrink-0">
                    {saving && (
                      <span className="h-4 w-4 animate-spin rounded-full border-2 border-brand-500 border-t-transparent" />
                    )}
                    <input
                      type="checkbox"
                      checked={config?.enabled ?? false}
                      disabled={saving}
                      onChange={(e) =>
                        saveCounterConfig(e.target.checked, config?.reactivationMode ?? "FROM_TODAY")
                      }
                      className="h-4 w-4 rounded border-gray-300 text-brand-500 focus:ring-brand-500"
                    />
                  </div>
                </label>

                <div>
                  <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
                    Modo de reactivación
                  </label>
                  <select
                    value={config?.reactivationMode ?? "FROM_TODAY"}
                    disabled={saving}
                    onChange={(e) => saveCounterConfig(config?.enabled ?? false, e.target.value)}
                    className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2.5 text-sm text-gray-700 outline-none transition focus:border-brand-500 focus:ring-1 focus:ring-brand-500 disabled:opacity-50 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-300"
                  >
                    {REACTIVATION_OPTIONS.map((o) => (
                      <option key={o.value} value={o.value}>{o.label}</option>
                    ))}
                  </select>
                </div>

                {config && (
                  <div className="rounded-xl border border-gray-200 p-4 dark:border-gray-800">
                    <p className="mb-1 text-sm font-medium text-gray-800 dark:text-white/90">
                      Sincronización manual
                    </p>
                    <p className="mb-3 text-xs text-gray-500 dark:text-gray-400">
                      Registra una fecha de corte manualmente. Si no seleccionas fecha se usa hoy.
                    </p>
                    <div className="flex items-center gap-3">
                      <input
                        type="date"
                        value={syncDate}
                        onChange={(e) => setSyncDate(e.target.value)}
                        disabled={saving}
                        className="rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-700 outline-none transition focus:border-brand-500 focus:ring-1 focus:ring-brand-500 disabled:opacity-50 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-300"
                      />
                      <button
                        onClick={() => syncCounterConfig(syncDate || undefined)}
                        disabled={saving}
                        className="rounded-lg bg-brand-500 px-4 py-2 text-sm font-medium text-white transition hover:bg-brand-600 disabled:opacity-50"
                      >
                        {saving ? "Sincronizando..." : "Sincronizar"}
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </Card>
          </div>
        )}
      </ModuleBase>
    </>
  );
};
