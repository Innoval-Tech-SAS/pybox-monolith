import { useNavigate, useParams } from "react-router";
import { CreditCard } from "lucide-react";
import { ModuleBase } from "@/ui/components/common/module-base";
import { PageMeta } from "@/ui/pages/page-meta";
import { usePaymentMethod } from "../hooks/use-payment-method";
import { PaymentMethodEditForm } from "../components/payment-method-edit-form";
import { useOrgModule } from "../hooks/use-org-module";
import { useBreadcrumb } from "../hooks/use-breadcrumb";
import { Loader } from "@/ui/components/loader/loader";
import EmptyState from "@/ui/components/common/empty-state";

export const EditPaymentMethodPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { orgId, buildOrgPath } = useOrgModule();
  const { build } = useBreadcrumb();
  const { item, loading } = usePaymentMethod(id ?? "", orgId);

  const backPath = buildOrgPath("/my-companies/payment-methods");
  const breadcrumbItems = build({ trail: [{ label: "Métodos de Pago", path: backPath, icon: CreditCard }] });

  if (loading) {
    return (
      <ModuleBase pageTitle="Editar método de pago" pageIcon={CreditCard} breadcrumbItems={breadcrumbItems}>
        <div className="flex h-48 items-center justify-center"><Loader loaderText="Cargando método de pago..." /></div>
      </ModuleBase>
    );
  }

  if (!item) {
    return (
      <ModuleBase pageTitle="No encontrado" pageIcon={CreditCard} breadcrumbItems={breadcrumbItems}>
        <EmptyState icon={CreditCard} title="Método de pago no encontrado" className="py-10" />
      </ModuleBase>
    );
  }

  return (
    <>
      <PageMeta title="Editar método de pago" description="Editar método de pago" />
      <ModuleBase
        pageTitle={`Editar — ${item.name}`}
        pageIcon={CreditCard}
        breadcrumbItems={breadcrumbItems}
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
