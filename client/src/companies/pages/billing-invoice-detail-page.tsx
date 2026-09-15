import { useEffect, useState } from "react";

const PAGE_SIZE = 10;
import { useSearchParams } from "react-router";
import { RefreshCw, FileText, Receipt } from "lucide-react";
import EmptyState from "@/ui/components/common/empty-state";
import { PageMeta } from "@/ui/pages/page-meta";
import { ModuleBase } from "@/ui/components/common/module-base";
import { Loader } from "@/ui/components/loader/loader";
import { Table, TableHeader, TableBody, TableRow, TableCell } from "@/ui/components/table/table";
import { PaginationWithIcon } from "@/ui/components/table/pagination-with-icon";
import { getSession } from "@/auth/utils/auth-session-utils";
import { InvoiceStatusBadge } from "@/billing/components/invoice-status-badge";
import { Button } from "@/ui/components/button/button";
import { BoldPaymentButton } from "@/billing/components/bold-payment-button";
import { MercadoPagoCardForm } from "@/billing/components/mercadopago-card-form";
import { PaymentResultModal } from "@/billing/components/payment-result-modal";
import {
  attemptStatusToResult,
  type PaymentResultStatus,
} from "@/billing/constants/payment-result-config";
import { formatCop, formatPeriod, formatUsd } from "@/billing/utils/format-currency";
import type { AdminInvoice, Invoice, PaymentLinkData } from "@/types/billing/billing-types";
import { useBillingActions } from "../hooks/use-billing-actions";
import { useAdminInvoiceActions } from "@/billing/hooks/use-admin-invoice-actions";
import { useOrgModule } from "../hooks/use-org-module";
import { useBreadcrumb } from "../hooks/use-breadcrumb";

const PAYABLE_STATUSES = ["EMITIDA", "PAGO_PENDIENTE", "VENCIDA", "BLOQUEADA"];
const TERMINAL_STATUSES = ["PAGADA", "CANCELADA"];

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

  const orgActions = useBillingActions(orgId);
  const adminActions = useAdminInvoiceActions();

  const [invoice, setInvoice] = useState<Invoice | AdminInvoice | null>(null);
  const [loading, setLoading] = useState(true);
  const [paymentLink, setPaymentLink] = useState<PaymentLinkData | null>(null);
  const [paying, setPaying] = useState(false);
  const [syncing, setSyncing] = useState(false);
  const [chargeResult, setChargeResult] = useState<PaymentResultStatus | null>(null);
  const [itemsPage, setItemsPage] = useState(1);
  const [attemptsPage, setAttemptsPage] = useState(1);

  const load = async () => {
    setLoading(true);
    const result = isAdminMode ? await adminActions.getInvoice(invoiceId) : await orgActions.getInvoice(invoiceId);
    setInvoice(result);
    setLoading(false);
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [invoiceId, orgId]);

  const handlePay = async () => {
    setPaying(true);
    const link = await orgActions.createPaymentLink(invoiceId);
    setPaymentLink(link);
    setPaying(false);
  };

  const handleMercadoPagoCharge = async (
    token: string,
    paymentMethodId: string,
    paymentTypeId: string,
    installments: number,
  ) => {
    if (!paymentLink) return;
    const updated = await orgActions.chargeMercadoPago(
      invoiceId,
      paymentLink.attemptId,
      token,
      paymentMethodId,
      paymentTypeId,
      installments,
    );
    if (updated) {
      setInvoice(updated);
      const attempt = updated.attempts.find((a) => a.id === paymentLink.attemptId);
      setChargeResult(attemptStatusToResult(attempt?.status));
      if (TERMINAL_STATUSES.includes(updated.status)) {
        setPaymentLink(null);
      }
    } else {
      // `chargeMercadoPago` devolvio null: error tecnico (ej. 400 de MP, red). El rechazo
      // legitimo del banco no cae aqui, vuelve como intento REJECTED en `updated`.
      setChargeResult("ERROR");
    }
  };

  const handleSync = async () => {
    setSyncing(true);
    const updated = await orgActions.syncInvoice(invoiceId);
    if (updated) {
      setInvoice(updated);
      if (TERMINAL_STATUSES.includes(updated.status)) {
        setPaymentLink(null);
      }
    }
    setSyncing(false);
  };

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

  const isPayable = canPay && PAYABLE_STATUSES.includes(invoice.status);
  const organizationName = (invoice as AdminInvoice).organizationName;

  return (
    <>
      <PageMeta title="Detalle de factura" description="Detalle de la factura de facturación" />
      <ModuleBase
        pageTitle="Detalle de factura"
        pageIcon={Receipt}
        breadcrumbItems={invoiceBreadcrumb}
      >
        <div className="flex flex-col gap-6">
          <div className="rounded-xl border border-gray-200 p-5 dark:border-gray-800">
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                {organizationName && (
                  <p className="text-xs uppercase tracking-wide text-gray-400">{organizationName}</p>
                )}
                <p className="text-lg font-semibold text-gray-800 dark:text-white/90">
                  {formatPeriod(invoice.periodYear, invoice.periodMonth)}
                </p>
                <p className="text-2xl font-bold text-gray-800 dark:text-white/90">
                  {formatCop(invoice.totalAmount)}
                </p>
                <p className="text-xs text-gray-400">
                  Subtotal {formatUsd(invoice.subtotalBaseAmount)} · TRM {invoice.exchangeRate} · Impuesto{" "}
                  {formatCop(invoice.taxAmount)}
                </p>
              </div>
              <div className="flex items-center gap-3">
                <InvoiceStatusBadge status={invoice.status} />
                {!isAdminMode && (
                  <button
                    type="button"
                    onClick={handleSync}
                    disabled={syncing}
                    title="Actualizar estado"
                    className="rounded-lg border border-gray-200 p-2 text-gray-500 hover:bg-gray-50 hover:text-gray-700 disabled:opacity-50 dark:border-gray-700 dark:text-gray-400 dark:hover:bg-white/5"
                  >
                    <RefreshCw size={16} className={syncing ? "animate-spin" : ""} />
                  </button>
                )}
              </div>
            </div>

            <div className="mt-4 grid grid-cols-2 gap-3 text-sm sm:grid-cols-4">
              <div>
                <p className="text-xs text-gray-400">Emitida</p>
                <p className="text-gray-700 dark:text-gray-300">
                  {invoice.issuedAt ? new Date(invoice.issuedAt).toLocaleDateString("es-CO") : "—"}
                </p>
              </div>
              <div>
                <p className="text-xs text-gray-400">Vence</p>
                <p className="text-gray-700 dark:text-gray-300">
                  {invoice.dueAt ? new Date(invoice.dueAt).toLocaleDateString("es-CO") : "—"}
                </p>
              </div>
              <div>
                <p className="text-xs text-gray-400">Bloqueo</p>
                <p className="text-gray-700 dark:text-gray-300">
                  {invoice.blockAt ? new Date(invoice.blockAt).toLocaleDateString("es-CO") : "—"}
                </p>
              </div>
              <div>
                <p className="text-xs text-gray-400">Pagada</p>
                <p className="text-gray-700 dark:text-gray-300">
                  {invoice.paidAt ? new Date(invoice.paidAt).toLocaleDateString("es-CO") : "—"}
                </p>
              </div>
            </div>

            {isPayable && (
              <div className="mt-5 border-t border-gray-100 pt-5 dark:border-gray-800">
                {!paymentLink ? (
                  <Button type="button" size="sm" onClick={handlePay} loading={paying} loadingText="Generando enlace de pago...">
                    Pagar factura
                  </Button>
                ) : paymentLink.provider === "MERCADO_PAGO" ? (
                  <MercadoPagoCardForm data={paymentLink} onCharge={handleMercadoPagoCharge} />
                ) : (
                  <BoldPaymentButton data={paymentLink} />
                )}
              </div>
            )}
          </div>

          <div>
            <p className="mb-3 text-sm font-semibold text-gray-800 dark:text-white/90">
              Desglose por campaña
            </p>
            {invoice.items.length === 0 ? (
              <EmptyState icon={FileText} title="Sin consumo registrado en este periodo" className="py-6" />
            ) : (() => {
              const itemsTotalPages = Math.max(1, Math.ceil(invoice.items.length / PAGE_SIZE));
              const visibleItems = invoice.items.slice((itemsPage - 1) * PAGE_SIZE, itemsPage * PAGE_SIZE);
              return (
                <div className="overflow-hidden rounded-xl border border-gray-200 dark:border-gray-800">
                  <div className="overflow-x-auto">
                    <Table>
                      <TableHeader>
                        <TableRow className="border-b border-gray-200 dark:border-gray-800">
                          {["Campaña", "Canal", "Cantidad", "Subtotal"].map((h) => (
                            <TableCell
                              key={h}
                              isHeader
                              className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wide text-gray-500 dark:text-gray-400"
                            >
                              {h}
                            </TableCell>
                          ))}
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {visibleItems.map((item) => (
                          <TableRow key={item.id} className="border-b border-gray-100 last:border-0 dark:border-gray-800">
                            <TableCell className="px-4 py-3 text-sm font-medium text-gray-800 dark:text-white/90">
                              {item.campaignName}
                            </TableCell>
                            <TableCell className="px-4 py-3 text-sm text-gray-600 dark:text-gray-400">
                              {item.channelName}
                            </TableCell>
                            <TableCell className="px-4 py-3 text-sm text-gray-600 dark:text-gray-400">
                              {item.quantity}
                            </TableCell>
                            <TableCell className="px-4 py-3 text-sm text-gray-600 dark:text-gray-400">
                              {formatUsd(item.subtotalBase)}
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </div>
                  <div className="flex flex-col gap-2 border-t border-gray-100 px-4 py-3 dark:border-gray-800 sm:flex-row sm:items-center sm:justify-between">
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      Mostrando {(itemsPage - 1) * PAGE_SIZE + 1}–{Math.min(itemsPage * PAGE_SIZE, invoice.items.length)} de {invoice.items.length}
                    </p>
                    <PaginationWithIcon totalPages={itemsTotalPages} initialPage={itemsPage} onPageChange={setItemsPage} />
                  </div>
                </div>
              );
            })()}
          </div>

          {invoice.attempts.length > 0 && (
            <div>
              <p className="mb-3 text-sm font-semibold text-gray-800 dark:text-white/90">Intentos de pago</p>
              {(() => {
                const attemptsTotalPages = Math.max(1, Math.ceil(invoice.attempts.length / PAGE_SIZE));
                const visibleAttempts = invoice.attempts.slice((attemptsPage - 1) * PAGE_SIZE, attemptsPage * PAGE_SIZE);
                return (
                  <div className="overflow-hidden rounded-xl border border-gray-200 dark:border-gray-800">
                    <div className="overflow-x-auto">
                      <Table>
                        <TableHeader>
                          <TableRow className="border-b border-gray-200 dark:border-gray-800">
                            {["#", "Referencia", "Estado", "Fecha"].map((h) => (
                              <TableCell
                                key={h}
                                isHeader
                                className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wide text-gray-500 dark:text-gray-400"
                              >
                                {h}
                              </TableCell>
                            ))}
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          {visibleAttempts.map((attempt) => (
                            <TableRow key={attempt.id} className="border-b border-gray-100 last:border-0 dark:border-gray-800">
                              <TableCell className="px-4 py-3 text-sm text-gray-600 dark:text-gray-400">
                                {attempt.attemptNumber}
                              </TableCell>
                              <TableCell className="px-4 py-3 text-sm text-gray-600 dark:text-gray-400">
                                {attempt.providerReference ?? "—"}
                              </TableCell>
                              <TableCell className="px-4 py-3 text-sm text-gray-600 dark:text-gray-400">
                                {attempt.status}
                              </TableCell>
                              <TableCell className="px-4 py-3 text-sm text-gray-600 dark:text-gray-400">
                                {new Date(attempt.createdAt).toLocaleString("es-CO")}
                              </TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </div>
                    <div className="flex flex-col gap-2 border-t border-gray-100 px-4 py-3 dark:border-gray-800 sm:flex-row sm:items-center sm:justify-between">
                      <p className="text-sm text-gray-500 dark:text-gray-400">
                        Mostrando {(attemptsPage - 1) * PAGE_SIZE + 1}–{Math.min(attemptsPage * PAGE_SIZE, invoice.attempts.length)} de {invoice.attempts.length}
                      </p>
                      <PaginationWithIcon totalPages={attemptsTotalPages} initialPage={attemptsPage} onPageChange={setAttemptsPage} />
                    </div>
                  </div>
                );
              })()}
            </div>
          )}
        </div>

        <PaymentResultModal
          isOpen={chargeResult !== null}
          status={chargeResult ?? "PENDING"}
          onClose={() => setChargeResult(null)}
          onRetry={() => setChargeResult(null)}
        />
      </ModuleBase>
    </>
  );
};
