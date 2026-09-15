import { useNavigate } from "react-router";
import { Receipt } from "lucide-react";
import { PageMeta } from "@/ui/pages/page-meta";
import { ModuleBase } from "@/ui/components/common/module-base";
import { Loader } from "@/ui/components/loader/loader";
import { useOrgModule } from "@/companies/hooks/use-org-module";
import { useBreadcrumb } from "@/companies/hooks/use-breadcrumb";
import { useBilling } from "../hooks/use-billing";
import { BillingLockAlert } from "../components/billing-lock-alert";
import { CurrentInvoiceCard } from "../components/current-invoice-card";
import { InvoiceListTable } from "../components/invoice-list-table";

export const BillingPage: React.FC = () => {
  const navigate = useNavigate();
  const { orgId, buildOrgPath } = useOrgModule();
  const { build } = useBreadcrumb();

  const { currentInvoice, invoices, status, loading } = useBilling(orgId);

  const goToInvoice = (invoiceId: string) => navigate(buildOrgPath("/my-companies/billing", { invoice: invoiceId }));

  return (
    <>
      <PageMeta title="Facturación" description="Facturación y pagos de la organización" />
      <ModuleBase pageTitle="Facturación" pageIcon={Receipt} breadcrumbItems={build()}>
        {loading ? (
          <div className="py-20">
            <Loader />
          </div>
        ) : (
          <div className="flex flex-col gap-5">
            {status && <BillingLockAlert status={status} />}

            {currentInvoice && <CurrentInvoiceCard invoice={currentInvoice} onViewDetail={() => goToInvoice(currentInvoice.id)} />}

            <InvoiceListTable invoices={invoices} onViewDetail={goToInvoice} />
          </div>
        )}
      </ModuleBase>
    </>
  );
};
