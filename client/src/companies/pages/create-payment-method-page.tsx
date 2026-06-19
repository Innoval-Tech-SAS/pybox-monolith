import { useNavigate } from "react-router";
import { ModuleBase } from "@/ui/components/common/module-base";
import { PageMeta } from "@/ui/pages/page-meta";
import { PaymentMethodForm } from "../components/payment-method-form";
import { useOrgModule } from "../hooks/use-org-module";

export const CreatePaymentMethodPage: React.FC = () => {
  const navigate = useNavigate();
  const { orgId, buildOrgPath } = useOrgModule();

  const backPath = buildOrgPath("/my-companies/payment-methods");

  return (
    <>
      <PageMeta title="Nuevo método de pago" description="Crear método de pago" />
      <ModuleBase
        pageTitle="Nuevo método de pago"
        breadcrumbItems={[
          { label: "Mis Empresas", path: "/my-companies" },
          { label: "Métodos de Pago", path: backPath },
        ]}
      >
        <PaymentMethodForm
          orgId={orgId}
          onSuccess={() => navigate(backPath)}
          onCancel={() => navigate(backPath)}
        />
      </ModuleBase>
    </>
  );
};
