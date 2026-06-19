import { useNavigate, useParams } from "react-router";
import { ModuleBase } from "@/ui/components/common/module-base";
import { PageMeta } from "@/ui/pages/page-meta";
import { usePaymentMethod } from "../hooks/use-payment-method";
import { PaymentMethodEditForm } from "../components/payment-method-edit-form";
import { useOrgModule } from "../hooks/use-org-module";

export const EditPaymentMethodPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { orgId, buildOrgPath } = useOrgModule();
  const { item, loading } = usePaymentMethod(id ?? "", orgId);

  const backPath = buildOrgPath("/my-companies/payment-methods");

  if (loading) {
    return (
      <ModuleBase pageTitle="Editar método de pago" breadcrumbItems={[{ label: "Métodos de Pago", path: backPath }]}>
        <div className="flex h-48 items-center justify-center text-gray-400">Cargando...</div>
      </ModuleBase>
    );
  }

  if (!item) {
    return (
      <ModuleBase pageTitle="No encontrado" breadcrumbItems={[{ label: "Métodos de Pago", path: backPath }]}>
        <div className="flex h-48 items-center justify-center text-gray-500">Método de pago no encontrado.</div>
      </ModuleBase>
    );
  }

  return (
    <>
      <PageMeta title="Editar método de pago" description="Editar método de pago" />
      <ModuleBase
        pageTitle={`Editar — ${item.name}`}
        breadcrumbItems={[
          { label: "Mis Empresas", path: "/my-companies" },
          { label: "Métodos de Pago", path: backPath },
        ]}
      >
        <PaymentMethodEditForm
          item={item}
          orgId={orgId}
          onSuccess={() => navigate(backPath)}
          onCancel={() => navigate(backPath)}
        />
      </ModuleBase>
    </>
  );
};
