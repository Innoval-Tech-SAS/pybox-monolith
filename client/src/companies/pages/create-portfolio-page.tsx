import { useSearchParams } from "react-router";
import { PageMeta } from "@/ui/pages/page-meta";
import { ModuleBase } from "@/ui/components/common/module-base";
import { CreatePortfolioForm } from "../components/create-portfolio-form";

export const CreatePortfolioPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const orgId = searchParams.get("org");

  return (
    <>
      <PageMeta title="Crear portafolio" description="Carga un nuevo portafolio de clientes" />
      <ModuleBase
        pageTitle="Crear portafolio"
        breadcrumbItems={[
          { label: "Mis Empresas", path: "/my-companies" },
          ...(orgId ? [{ label: "Empresa", path: `/my-companies?org=${orgId}` }] : []),
        ]}
      >
        <div className="mx-auto w-full max-w-2xl">
          <div className="rounded-3xl border border-gray-200 bg-white/80 p-6 shadow-lg backdrop-blur-md dark:border-gray-700 dark:bg-white/3 sm:p-8">
            <div className="mb-6">
              <h2 className="text-xl font-bold text-gray-800 dark:text-white/90">
                Cargar portafolio
              </h2>
              <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                Sube un archivo CSV con los datos de los clientes del portafolio.
              </p>
            </div>
            <CreatePortfolioForm />
          </div>
        </div>
      </ModuleBase>
    </>
  );
};
