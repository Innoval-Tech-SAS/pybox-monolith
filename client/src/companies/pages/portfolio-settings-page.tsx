import { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router";
import { Pencil, Settings } from "lucide-react";
import { PageMeta } from "@/ui/pages/page-meta";
import { ModuleBase } from "@/ui/components/common/module-base";
import { Card, CardTitle } from "@/ui/components/card";
import { Loader } from "@/ui/components/loader/loader";
import { Spinner } from "@/ui/components/loader/spinner";
import { Badge } from "@/ui/components/badge";
import { Input } from "@/ui/components/inputs/input";
import { Label } from "@/ui/components/inputs/label";
import { CountrySelect } from "@/ui/components/inputs/country-select";
import { Select } from "@/ui/components/inputs/select";
import { InfoRow } from "@/companies/components/info-row";
import { usePortfolioSettings } from "../hooks/use-portfolio-settings";
import { useOrgModule } from "../hooks/use-org-module";
import { useRequireOrg } from "../hooks/use-require-org";
import { useBreadcrumb } from "../hooks/use-breadcrumb";
import { REACTIVATION_OPTIONS } from "@/companies/constants/portfolio-settings-form";
import { formatShortDate as fmt } from "@/profile/utils/format-date";

export const PortfolioSettingsPage: React.FC = () => {
  useRequireOrg();
  const [searchParams] = useSearchParams();
  const portfolioId = searchParams.get("portfolio") ?? "";
  const { orgName, buildOrgPath } = useOrgModule();
  const { build } = useBreadcrumb();
  const navigate = useNavigate();

  const { portfolio, config, loading, saving, toggleActive, updateInfo, saveCounterConfig, syncCounterConfig } =
    usePortfolioSettings(portfolioId);

  // Sin `?portfolio=` (enlace directo, favorito viejo) no hay nada que
  // configurar: en vez de renderizar el módulo con datos en blanco, se manda
  // al listado de portafolios para que el usuario elija uno.
  useEffect(() => {
    if (!portfolioId) {
      navigate(buildOrgPath("/my-companies/portfolios"), { replace: true });
    }
  }, [portfolioId, buildOrgPath, navigate]);

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
        pageIcon={Settings}
        breadcrumbItems={build({ portfolio: { id: portfolioId, name: portfolio?.name } })}
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
                      <Label htmlFor="portfolio-settings-name">
                        Nombre <span className="text-error-500" aria-hidden="true">*</span>
                      </Label>
                      <Input
                        id="portfolio-settings-name"
                        value={form.name}
                        onChange={(e) => setForm((p) => ({ ...p, name: e.target.value }))}
                        placeholder="Nombre del portafolio"
                        required
                        aria-required="true"
                      />
                    </div>
                    <div>
                      <Label>
                        <span className="mb-1.5 block">País</span>
                        <CountrySelect
                          mode="NAME"
                          value={form.country}
                          onChange={(v) => setForm((p) => ({ ...p, country: v }))}
                          disabled={!!portfolio?.country}
                        />
                      </Label>
                      {portfolio?.country && (
                        <p className="mt-1.5 text-xs text-gray-400 dark:text-gray-500">
                          El país no puede modificarse una vez asignado.
                        </p>
                      )}
                    </div>
                    <div className="sm:col-span-2">
                      <Label htmlFor="portfolio-settings-description">Descripción</Label>
                      <textarea
                        id="portfolio-settings-description"
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
                    <Pencil size={16} />
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
                    {saving && <Spinner size="xs" tone="brand" />}
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
                    {saving && <Spinner size="xs" tone="brand" />}
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
                  <Label>
                    <span className="mb-1.5 block">Modo de reactivación</span>
                    <Select
                      options={REACTIVATION_OPTIONS}
                      value={config?.reactivationMode ?? "FROM_TODAY"}
                      disabled={saving}
                      onChange={(v) => saveCounterConfig(config?.enabled ?? false, v)}
                    />
                  </Label>
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
                      <label className="sr-only" htmlFor="portfolio-settings-sync-date">
                        Fecha de corte para sincronización manual
                      </label>
                      <input
                        id="portfolio-settings-sync-date"
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
