import { useSearchParams } from "react-router";
import { CalendarCheck } from "lucide-react";
import { PageMeta } from "@/ui/pages/page-meta";
import { ModuleBase } from "@/ui/components/common/module-base";
import { UploadInstallmentsForm } from "../components/upload-installments-form";
import { useOrgModule } from "../hooks/use-org-module";
import { useBreadcrumb } from "../hooks/use-breadcrumb";
import { usePortfolios } from "../hooks/use-portfolios";

export const UploadInstallmentsPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const portfolioId = searchParams.get("portfolio") ?? "";

  const { orgId } = useOrgModule();
  const { build } = useBreadcrumb();
  const { portfolios } = usePortfolios(orgId);
  const portfolioName = portfolios.find((p) => p.id === portfolioId)?.name ?? "Portafolio";

  return (
    <>
      <PageMeta title="Cargar plan de cuotas" description="Carga masiva del plan de cuotas de un portafolio" />
      <ModuleBase
        pageTitle="Cargar plan de cuotas"
        pageIcon={CalendarCheck}
        breadcrumbItems={build({ portfolio: { id: portfolioId, name: portfolioName } })}
      >
        <UploadInstallmentsForm />
      </ModuleBase>
    </>
  );
};
