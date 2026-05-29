import { useSearchParams } from "react-router";
import { PageMeta } from "@/ui/pages/page-meta";
import { ModuleBase } from "@/ui/components/common/module-base";
import { Card, CardTitle } from "@/ui/components/card";
import { Loader } from "@/ui/components/loader/loader";
import { usePortfolioSettings } from "../hooks/use-portfolio-settings";

const REACTIVATION_OPTIONS = [
  { value: "FROM_TODAY", label: "Desde hoy" },
  { value: "CATCH_UP", label: "Ponerse al día" },
];

export const PortfolioSettingsPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const orgId = searchParams.get("org") ?? "";
  const portfolioId = searchParams.get("portfolio") ?? "";

  const { portfolio, config, loading, saving, toggleActive, saveCounterConfig } =
    usePortfolioSettings(portfolioId);

  return (
    <>
      <PageMeta title="Configuración" description="Configuración del portafolio" />
      <ModuleBase
        pageTitle="Configuración"
        breadcrumbItems={[
          { label: "Mis Empresas", path: "/my-companies" },
          ...(orgId ? [{ label: "Empresa", path: `/my-companies?org=${orgId}` }] : []),
          { label: "Portafolios", path: `/my-companies/portfolios?org=${orgId}` },
          ...(portfolioId
            ? [{ label: "Portafolio", path: `/my-companies/portfolios?org=${orgId}&portfolio=${portfolioId}` }]
            : []),
        ]}
      >
        {loading ? (
          <div className="py-20">
            <Loader />
          </div>
        ) : (
          <div className="max-w-2xl space-y-6">
            {/* Estado del portafolio */}
            <Card>
              <CardTitle>Estado del portafolio</CardTitle>
              <label className="flex cursor-pointer items-center justify-between gap-4 rounded-xl border border-gray-200 p-4 dark:border-gray-800">
                <div>
                  <p className="text-sm font-medium text-gray-800 dark:text-white/90">
                    Portafolio activo
                  </p>
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

            {/* Contadores diarios */}
            <Card>
              <CardTitle>Actualización diaria</CardTitle>
              <p className="mb-4 text-sm text-gray-500 dark:text-gray-400">
                Configura la sincronización automática de contadores por día.
              </p>

              <div className="space-y-4">
                <label className="flex cursor-pointer items-center justify-between gap-4 rounded-xl border border-gray-200 p-4 dark:border-gray-800">
                  <div>
                    <p className="text-sm font-medium text-gray-800 dark:text-white/90">
                      Actualización activa
                    </p>
                    {config?.lastSyncedAt && (
                      <p className="mt-0.5 text-xs text-gray-400">
                        Última sync:{" "}
                        {new Date(config.lastSyncedAt).toLocaleDateString("es-CO")}
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
                        saveCounterConfig(
                          e.target.checked,
                          config?.reactivationMode ?? "FROM_TODAY",
                        )
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
                    onChange={(e) =>
                      saveCounterConfig(config?.enabled ?? false, e.target.value)
                    }
                    className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2.5 text-sm text-gray-700 outline-none transition focus:border-brand-500 focus:ring-1 focus:ring-brand-500 disabled:opacity-50 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-300"
                  >
                    {REACTIVATION_OPTIONS.map((o) => (
                      <option key={o.value} value={o.value}>
                        {o.label}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            </Card>
          </div>
        )}
      </ModuleBase>
    </>
  );
};
