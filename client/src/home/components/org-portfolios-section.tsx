import { usePortfolios } from "@/companies/hooks/use-portfolios";
import { Loader } from "@/ui/components/loader/loader";
import type { OrgPortfoliosSectionProps } from "@/types/props/org-portfolios-section-props";
import { InitialsBadge } from "./initials-badge";
import { PortfolioDashboardCharts } from "./portfolio-dashboard-charts";

/** Portafolios a los que el usuario tiene acceso dentro de una organización (no todos los de la org). */
export const OrgPortfoliosSection: React.FC<OrgPortfoliosSectionProps> = ({ organizationId }) => {
  const { portfolios, loading } = usePortfolios(organizationId);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader />
      </div>
    );
  }

  if (portfolios.length === 0) {
    return (
      <p className="py-6 text-center text-sm text-gray-400 dark:text-gray-500">
        No tienes acceso a ningún portafolio en esta organización todavía.
      </p>
    );
  }

  return (
    <div className="flex flex-col gap-6">
      {portfolios.map((portfolio) => (
        <div key={portfolio.id} className="flex flex-col gap-3">
          <InitialsBadge name={portfolio.name} />
          <PortfolioDashboardCharts portfolioId={portfolio.id} />
        </div>
      ))}
    </div>
  );
};
