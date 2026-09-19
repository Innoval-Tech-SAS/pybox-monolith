import { useState } from "react";
import { useNavigate, useParams, useSearchParams } from "react-router";
import { ModuleBase } from "@/ui/components/common/module-base";
import { Card, CardTitle } from "@/ui/components/card";
import { useUserPortfolioAccess } from "../hooks/use-user-portfolio-access";
import { Loader } from "@/ui/components/loader/loader";
import { Spinner } from "@/ui/components/loader/spinner";
import EmptyState from "@/ui/components/common/empty-state";
import { FolderOpen } from "lucide-react";
import { Button } from "@/ui/components/button/button";

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
        {busy && <Spinner size="xs" tone="brand" />}
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
  const userId = id ?? "";

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
            <Loader size="sm" loaderText="Cargando portafolios..." />
          ) : portfolios.length === 0 ? (
            <EmptyState icon={FolderOpen} title="Sin portafolios en esta empresa" className="py-6" />
          ) : (
            <div className="flex flex-col gap-3">
              {portfolios.map((p) => (
                <PortfolioToggle
                  key={p.portfolioId}
                  portfolioId={p.portfolioId}
                  name={p.name}
                  hasAccess={p.hasAccess}
                  onToggle={(checked) => handleToggle(p.portfolioId, checked)}
                />
              ))}
            </div>
          )}

          <div className="flex justify-end mt-6 pt-5 border-t border-gray-100 dark:border-gray-800">
            <Button type="button" size="sm" onClick={() => navigate(backPath)}>
              Listo
            </Button>
          </div>
        </Card>
      </div>
    </ModuleBase>
  );
};
