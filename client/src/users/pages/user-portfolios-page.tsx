import { useState } from "react";
import { useNavigate, useParams, useSearchParams } from "react-router";
import { ModuleBase } from "@/ui/components/common/module-base";
import { Card, CardTitle } from "@/ui/components/card";
import { useUserPortfolioAccess } from "../hooks/use-user-portfolio-access";

const PortfolioToggle: React.FC<{
  portfolioId: string;
  name: string;
  hasAccess: boolean;
  onToggle: (checked: boolean) => Promise<void>;
}> = ({ portfolioId: _portfolioId, name, hasAccess, onToggle }) => {
  const [busy, setBusy] = useState(false);

  const handleChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    setBusy(true);
    await onToggle(e.target.checked);
    setBusy(false);
  };

  return (
    <label className="flex items-center justify-between gap-4 rounded-lg border border-gray-200 p-4 cursor-pointer hover:bg-gray-50 dark:border-gray-700 dark:hover:bg-white/5">
      <span className="text-sm font-medium text-gray-800 dark:text-white/90">{name}</span>
      <div className="flex items-center gap-2 shrink-0">
        {busy && (
          <span className="h-4 w-4 animate-spin rounded-full border-2 border-brand-500 border-t-transparent" />
        )}
        <input
          type="checkbox"
          checked={hasAccess}
          disabled={busy}
          onChange={handleChange}
          className="h-4 w-4 rounded border-gray-300 text-brand-500 focus:ring-brand-500"
        />
      </div>
    </label>
  );
};

export const UserPortfoliosPage: React.FC = () => {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  const [searchParams] = useSearchParams();
  const orgId = searchParams.get("org") ?? "";
  const userId = Number(id);

  const { portfolios, loading, grantAccess, revokeAccess } = useUserPortfolioAccess(orgId, userId);

  const backPath = orgId ? `/my-companies/users?org=${orgId}` : "/my-users";

  const handleToggle = async (portfolioId: string, checked: boolean) => {
    if (checked) {
      await grantAccess(portfolioId);
    } else {
      await revokeAccess(portfolioId);
    }
  };

  return (
    <ModuleBase
      pageTitle="Acceso a portafolios"
      breadcrumbItems={[{ label: "Usuarios", path: backPath }]}
    >
      <div className="max-w-2xl">
        <Card>
          <CardTitle>Portafolios de la empresa</CardTitle>
          <p className="mb-5 text-sm text-gray-500 dark:text-gray-400">
            Activa o desactiva el acceso a cada portafolio para este usuario.
          </p>

          {loading ? (
            <p className="text-sm text-gray-400">Cargando...</p>
          ) : portfolios.length === 0 ? (
            <p className="text-sm text-gray-400">No hay portafolios disponibles en esta empresa.</p>
          ) : (
            <div className="flex flex-col gap-3">
              {portfolios.map((p) => (
                <PortfolioToggle
                  key={p.portfolio_id}
                  portfolioId={p.portfolio_id}
                  name={p.name}
                  hasAccess={p.has_access}
                  onToggle={(checked) => handleToggle(p.portfolio_id, checked)}
                />
              ))}
            </div>
          )}

          <div className="flex justify-end mt-6 pt-5 border-t border-gray-100 dark:border-gray-800">
            <button
              type="button"
              onClick={() => navigate(backPath)}
              className="rounded-lg bg-brand-500 px-4 py-2.5 text-sm font-medium text-white shadow-theme-xs hover:bg-brand-600"
            >
              Listo
            </button>
          </div>
        </Card>
      </div>
    </ModuleBase>
  );
};
