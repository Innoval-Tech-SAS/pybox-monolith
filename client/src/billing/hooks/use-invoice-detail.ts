import { useEffect, useState } from "react";
import { useBillingActions } from "./use-billing-actions";
import { useAdminInvoiceActions } from "./use-admin-invoice-actions";
import { attemptStatusToResult } from "../utils/payment-result";
import { PAYABLE_INVOICE_STATUSES, TERMINAL_INVOICE_STATUSES } from "../constants/invoice-lifecycle";
import type { AdminInvoice, Invoice, PaymentLinkData } from "@/types/billing/billing-types";
import type { PaymentResultStatus } from "../types/payment-result-types";

/** Orquesta la carga y el flujo de pago (Bold/Mercado Pago) de una factura, en modo org o admin. */
export const useInvoiceDetail = (invoiceId: string, organizationId: string, canPay: boolean) => {
  const isAdminMode = !organizationId;
  const orgActions = useBillingActions(organizationId);
  const adminActions = useAdminInvoiceActions();

  const [invoice, setInvoice] = useState<Invoice | AdminInvoice | null>(null);
  const [loading, setLoading] = useState(true);
  const [paymentLink, setPaymentLink] = useState<PaymentLinkData | null>(null);
  const [paying, setPaying] = useState(false);
  const [syncing, setSyncing] = useState(false);
  const [chargeResult, setChargeResult] = useState<PaymentResultStatus | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    const request = isAdminMode ? adminActions.getInvoice(invoiceId) : orgActions.getInvoice(invoiceId);
    request.then((result) => {
      if (cancelled) return;
      setInvoice(result);
      setLoading(false);
    });
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [invoiceId, organizationId]);

  const pay = async () => {
    setPaying(true);
    const link = await orgActions.createPaymentLink(invoiceId);
    setPaymentLink(link);
    setPaying(false);
  };

  const chargeMercadoPago = async (
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
      if (TERMINAL_INVOICE_STATUSES.includes(updated.status)) {
        setPaymentLink(null);
      }
    } else {
      // `chargeMercadoPago` devolvio null: error tecnico (ej. 400 de MP, red). El rechazo
      // legitimo del banco no cae aqui, vuelve como intento REJECTED en `updated`.
      setChargeResult("ERROR");
    }
  };

  const sync = async () => {
    setSyncing(true);
    const updated = await orgActions.syncInvoice(invoiceId);
    if (updated) {
      setInvoice(updated);
      if (TERMINAL_INVOICE_STATUSES.includes(updated.status)) {
        setPaymentLink(null);
      }
    }
    setSyncing(false);
  };

  const dismissChargeResult = () => setChargeResult(null);

  const isPayable = canPay && !!invoice && PAYABLE_INVOICE_STATUSES.includes(invoice.status);

  return {
    isAdminMode,
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
  };
};
