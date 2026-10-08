import { useState } from "react";
import { useUserPortfolioAccess } from "../hooks/use-user-portfolio-access";
import { Loader } from "@/ui/components/loader/loader";
import EmptyState from "@/ui/components/common/empty-state";
import { FolderOpen } from "lucide-react";

export const CreateUserPortfolioCheckboxes: React.FC<{ orgId: string; userId: string }> = ({ orgId, userId }) => {
  const { portfolios, loading, grantAccess, revokeAccess } = useUserPortfolioAccess(orgId, userId);
  const [busy, setBusy] = useState<string | null>(null);

  const toggle = async (portfolioId: string, checked: boolean) => {
    setBusy(portfolioId);
    if (checked) await grantAccess(portfolioId);
    else await revokeAccess(portfolioId);
    setBusy(null);
  };

  if (loading) return <Loader size="sm" loaderText="Cargando portafolios..." />;
  if (portfolios.length === 0)
    return <EmptyState icon={FolderOpen} title="Sin portafolios en esta empresa" className="py-4" />;

  return (
    <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-3">
      {portfolios.map((p) => {
        const isBusy = busy === p.portfolioId;
        return (
          <label
            key={p.portfolioId}
            className="flex items-center gap-3 rounded-lg border border-gray-200 p-3 cursor-pointer hover:bg-gray-50 dark:border-gray-700 dark:hover:bg-white/5"
          >
            <input
              type="checkbox"
              checked={p.hasAccess}
              disabled={isBusy}
              onChange={(e) => toggle(p.portfolioId, e.target.checked)}
              className="h-4 w-4 rounded border-gray-300 text-brand-500 focus:ring-brand-500"
            />
            <span className="text-sm font-medium text-gray-800 dark:text-white/90">{p.name}</span>
          </label>
        );
      })}
    </div>
  );
};
