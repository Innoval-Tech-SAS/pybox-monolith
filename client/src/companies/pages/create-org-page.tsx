import { PageMeta } from "@/ui/pages/page-meta";
import { ModuleBase } from "@/ui/components/common/module-base";
import { RegisterOrgForm } from "../components/register-org-form";

export const CreateOrgPage: React.FC = () => (
  <>
    <PageMeta title="Crear organización" description="Registra una nueva organización" />
    <ModuleBase
      pageTitle="Crear organización"
      breadcrumbItems={[{ label: "Mis Empresas", path: "/my-companies" }]}
    >
      <div className="mx-auto w-full max-w-3xl">
        <div className="rounded-3xl border border-gray-200 bg-white/80 p-6 shadow-lg backdrop-blur-md dark:border-gray-700 dark:bg-white/3 sm:p-8">
          <div className="mb-6">
            <h2 className="text-xl font-bold text-gray-800 dark:text-white/90">
              Datos de la organización
            </h2>
            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
              Completa el formulario para registrar una nueva organización y asignar su representante legal.
            </p>
          </div>
          <RegisterOrgForm />
        </div>
      </div>
    </ModuleBase>
  </>
);
