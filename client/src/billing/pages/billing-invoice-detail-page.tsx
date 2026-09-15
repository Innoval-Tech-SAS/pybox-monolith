import { useSearchParams } from "react-router";
import { Receipt } from "lucide-react";
import { PageMeta } from "@/ui/pages/page-meta";
import { ModuleBase } from "@/ui/components/common/module-base";
import { Loader } from "@/ui/components/loader/loader";
import { getSession } from "@/auth/utils/auth-session-utils";
import { PaymentResultModal } from "@/billing/components/payment-result-modal";
import { useOrgModule } from "@/companies/hooks/use-org-module";
import { useBreadcrumb } from "@/companies/hooks/use-breadcrumb";
import { useInvoiceDetail } from "../hooks/use-invoice-detail";
import { InvoiceSummaryCard } from "../components/invoice-summary-card";
import { InvoicePaymentSection } from "../components/invoice-payment-section";
import { InvoiceItemsTable } from "../components/invoice-items-table";
import { InvoicePaymentAttemptsTable } from "../components/invoice-payment-attempts-table";

export const BillingInvoiceDetailPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const invoiceId = searchParams.get("invoice") ?? "";
  const { orgId, buildOrgPath } = useOrgModule();
  const { build } = useBreadcrumb();
  const isAdminMode = !orgId;

  const invoiceBreadcrumb = isAdminMode
    ? [{ label: "Facturación", path: "/billing", icon: Receipt }]
    : build({ trail: [{ label: "Facturación", path: buildOrgPath("/my-companies/billing"), icon: Receipt }] });

  const session = getSession();
  const canPay = !isAdminMode && session?.scope !== "GLOBAL";

  const {
    invoice,
    loading,
    paymentLink,
    paying,
    syncing,
    chargeResult,
    isPayable,
    pay,
    chargeMercadoPago,
    sync,
    dismissChargeResult,
  } = useInvoiceDetail(invoiceId, orgId, canPay);

  if (loading) {
    return (
      <div className="py-20">
        <Loader />
      </div>
    );
  }

  if (!invoice) {
    return (
      <ModuleBase pageTitle="Factura" pageIcon={Receipt} breadcrumbItems={[]} showBack>
        <p className="py-12 text-center text-sm text-gray-400 dark:text-gray-500">Factura no encontrada.</p>
      </ModuleBase>
    );
  }

  return (
    <>
      <PageMeta title="Detalle de factura" description="Detalle de la factura de facturación" />
      <ModuleBase pageTitle="Detalle de factura" pageIcon={Receipt} breadcrumbItems={invoiceBreadcrumb}>
        <div className="flex flex-col gap-6">
          <div className="rounded-xl border border-gray-200 p-5 dark:border-gray-800">
            <InvoiceSummaryCard invoice={invoice} isAdminMode={isAdminMode} syncing={syncing} onSync={sync} />
            {isPayable && (
              <InvoicePaymentSection
                paymentLink={paymentLink}
                paying={paying}
                onPay={pay}
                onMercadoPagoCharge={chargeMercadoPago}
              />
            )}
          </div>

          <div>
            <p className="mb-3 text-sm font-semibold text-gray-800 dark:text-white/90">Desglose por campaña</p>
            <InvoiceItemsTable items={invoice.items} />
          </div>

          {invoice.attempts.length > 0 && (
            <div>
              <p className="mb-3 text-sm font-semibold text-gray-800 dark:text-white/90">Intentos de pago</p>
              <InvoicePaymentAttemptsTable attempts={invoice.attempts} />
            </div>
          )}
        </div>

        <PaymentResultModal
          isOpen={chargeResult !== null}
          status={chargeResult ?? "PENDING"}
          onClose={dismissChargeResult}
          onRetry={dismissChargeResult}
        />
      </ModuleBase>
    </>
  );
};
