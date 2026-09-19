import { Briefcase } from "lucide-react";
import { PageMeta } from "@/ui/pages/page-meta";
import { ModuleBase } from "@/ui/components/common/module-base";
import { CreatePortfolioForm } from "../components/create-portfolio-form";
import { useBreadcrumb } from "../hooks/use-breadcrumb";

export const CreatePortfolioPage: React.FC = () => {
  const { build } = useBreadcrumb();

  return (
    <>
      <PageMeta title="Crear portafolio" description="Carga un nuevo portafolio de clientes" />
      <ModuleBase
        pageTitle="Crear portafolio"
        pageIcon={Briefcase}
        breadcrumbItems={build()}
      >
        <CreatePortfolioForm />
      </ModuleBase>
    </>
  );
};
