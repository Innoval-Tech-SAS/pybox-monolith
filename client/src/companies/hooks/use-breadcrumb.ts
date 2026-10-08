import { Building2, Briefcase, Send, User, Users } from "lucide-react";
import { useOrgModule } from "@/companies/hooks/use-org-module";
import type { BreadcrumbItem } from "@/types/props/breadcrumb-props";

interface BuildBreadcrumbConfig {
  /** Include the empresa (org) crumb. Defaults to true. */
  org?: boolean;
  /** Portfolio crumb; pass id and name to include it. */
  portfolio?: { id?: string; name?: string };
  /** Append the "Comunicaciones" crumb (requires portfolio.id). */
  communications?: boolean;
  /** Page-specific trailing crumbs, rendered after the org/portfolio chain. */
  trail?: BreadcrumbItem[];
}

interface DebtorBreadcrumbConfig {
  portfolioId: string;
  portfolioName: string;
  debtorId?: string | null;
  /** Append the "Detalle de cliente" crumb. */
  includeDetail?: boolean;
}

/**
 * Single source of truth for org/portfolio breadcrumbs. Every module should
 * build its breadcrumb through this hook so the chain stays consistent (no
 * "Mis Empresas"/"Mis Portafolios" label nodes — only the empresa/portfolio
 * names, each with its icon).
 */
export const useBreadcrumb = () => {
  const { orgId, orgName, buildOrgPath } = useOrgModule();

  const build = ({
    org = true,
    portfolio,
    communications = false,
    trail = [],
  }: BuildBreadcrumbConfig = {}): BreadcrumbItem[] => {
    const items: BreadcrumbItem[] = [];

    if (org && orgId) {
      items.push({
        label: orgName || "Empresa",
        path: buildOrgPath("/my-companies"),
        icon: Building2,
      });
    }

    if (portfolio?.id) {
      items.push({
        label: portfolio.name || "Portafolio",
        path: buildOrgPath("/my-companies/portfolios", { portfolio: portfolio.id }),
        icon: Briefcase,
      });
      if (communications) {
        items.push({
          label: "Comunicaciones",
          path: buildOrgPath("/my-companies/portfolios/communications", {
            portfolio: portfolio.id,
          }),
          icon: Send,
        });
      }
    }

    return [...items, ...trail];
  };

  const debtor = ({
    portfolioId,
    portfolioName,
    debtorId,
    includeDetail = false,
  }: DebtorBreadcrumbConfig): BreadcrumbItem[] => {
    const trail: BreadcrumbItem[] = [
      {
        label: "Clientes",
        path: buildOrgPath("/my-companies/portfolios/debtors", { portfolio: portfolioId }),
        icon: Users,
      },
    ];
    if (includeDetail) {
      trail.push({
        label: "Detalle de cliente",
        path: buildOrgPath("/my-companies/portfolios/debtors", {
          portfolio: portfolioId,
          clientId: debtorId ?? "",
        }),
        icon: User,
      });
    }
    return build({ portfolio: { id: portfolioId, name: portfolioName }, trail });
  };

  return { build, debtor, buildOrgPath, orgId, orgName };
};
