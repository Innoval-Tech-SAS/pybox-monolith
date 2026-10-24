import { useEffect, useRef, useState } from "react";
import { Button } from "@/ui/components/button/button";
import { Badge } from "@/ui/components/badge";
import { Input } from "@/ui/components/inputs/input";
import { Label } from "@/ui/components/inputs/label";
import { Select } from "@/ui/components/inputs/select";
import { useToast } from "@/context/toast-context";
import { useWompiCheckout } from "@/credits/hooks/use-wompi-checkout";
import { captureWompiBrowserInfo } from "@/credits/utils/wompi-browser-info";
import { formatCreditCurrency } from "@/credits/utils/financial-calendar-utils";
import type { WompiCheckoutFormProps } from "@/credits/types/wompi-checkout-form-props";
import type {
  FinancialInstitution,
  PaymentAttemptResult,
  WompiMethod,
} from "@/credits/types/wompi-checkout-types";
import type { CardFieldsValue } from "@/credits/types/wompi-card-fields-props";
import type { PseFieldsValue } from "@/credits/types/wompi-pse-fields-props";
import { WompiCardFields } from "./wompi-card-fields";
import { WompiPseFields } from "./wompi-pse-fields";
import { WompiChallengePanel } from "./wompi-challenge-panel";

const METHOD_OPTIONS: { value: WompiMethod; label: string }[] = [
  { value: "NEQUI", label: "Nequi" },
  { value: "PSE", label: "PSE (débito bancario)" },
  { value: "CARD", label: "Tarjeta de crédito o débito" },
  { value: "BANCOLOMBIA_TRANSFER", label: "Transferencia Bancolombia" },
];

const POLL_INTERVAL_MS = 2500;

const WAITING_LABELS: Record<WompiMethod, string> = {
  NEQUI: "Confirma el pago desde tu app Nequi...",
  PSE: "Estamos verificando tu pago con el banco...",
  CARD: "Verificando tu tarjeta con el banco...",
  BANCOLOMBIA_TRANSFER: "Completa la transferencia desde Bancolombia...",
};

const FINAL_STATUS_META: Record<string, { label: string; color: "success" | "error" | "warning" }> = {
  APPROVED: { label: "Pago aprobado", color: "success" },
  DECLINED: { label: "Pago rechazado", color: "error" },
  ERROR: { label: "Hubo un error con el pago", color: "error" },
  VOIDED: { label: "El pago fue anulado", color: "warning" },
};

export const WompiCheckoutForm: React.FC<WompiCheckoutFormProps> = ({
  payment,
  currencyCode,
  onDone,
  onCancel,
}) => {
  const { createTransaction, listPseInstitutions, fetchAttemptStatus, submitting } =
    useWompiCheckout(payment.id);
  const { success } = useToast();

  const [method, setMethod] = useState<WompiMethod | "">("");
  const [customerEmail, setCustomerEmail] = useState("");
  const [cardFields, setCardFields] = useState<CardFieldsValue>({
    number: "", cvc: "", expMonth: "", expYear: "", cardHolder: "", installments: 1,
  });
  const [pseFields, setPseFields] = useState<PseFieldsValue>({
    userType: "0", userLegalIdType: "CC", userLegalId: "", financialInstitutionCode: "", paymentDescription: "",
  });
  const [nequiPhone, setNequiPhone] = useState("");
  const [institutions, setInstitutions] = useState<FinancialInstitution[]>([]);
  const [loadingInstitutions, setLoadingInstitutions] = useState(false);
  const [attempt, setAttempt] = useState<PaymentAttemptResult | null>(null);
  const [challengeHtml, setChallengeHtml] = useState<string | null>(null);

  const pollTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    if (method !== "PSE" || institutions.length > 0) return;
    setLoadingInstitutions(true);
    listPseInstitutions()
      .then((list) => setInstitutions(list))
      .finally(() => setLoadingInstitutions(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [method]);

  useEffect(() => {
    if (!attempt || attempt.status !== "PENDING") return;
    pollTimer.current = setTimeout(async () => {
      const next = await fetchAttemptStatus(attempt.id);
      if (next) setAttempt(next);
    }, POLL_INTERVAL_MS);
    return () => {
      if (pollTimer.current) clearTimeout(pollTimer.current);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [attempt]);

  useEffect(() => {
    if (attempt?.status === "APPROVED") {
      success("Pago registrado", "Tu pago fue aprobado.");
      onDone();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [attempt?.status]);

  const paymentDescription = `Pago cuota #${payment.installmentNumber ?? payment.id}`;

  const buildBody = (): Record<string, unknown> | null => {
    if (method === "NEQUI") {
      if (!nequiPhone || !customerEmail) return null;
      return { paymentMethodType: "NEQUI", phoneNumber: nequiPhone, customerEmail };
    }
    if (method === "PSE") {
      if (!pseFields.userLegalId || !pseFields.financialInstitutionCode || !customerEmail) return null;
      return {
        paymentMethodType: "PSE",
        userType: Number(pseFields.userType),
        userLegalIdType: pseFields.userLegalIdType,
        userLegalId: pseFields.userLegalId,
        financialInstitutionCode: pseFields.financialInstitutionCode,
        paymentDescription,
        customerEmail,
      };
    }
    if (method === "BANCOLOMBIA_TRANSFER") {
      if (!customerEmail) return null;
      return { paymentMethodType: "BANCOLOMBIA_TRANSFER", paymentDescription, customerEmail };
    }
    if (method === "CARD") {
      if (
        !cardFields.number || !cardFields.cvc || !cardFields.expMonth ||
        !cardFields.expYear || !cardFields.cardHolder || !customerEmail
      ) {
        return null;
      }
      return {
        paymentMethodType: "CARD",
        number: cardFields.number,
        cvc: cardFields.cvc,
        expMonth: cardFields.expMonth,
        expYear: cardFields.expYear,
        cardHolder: cardFields.cardHolder,
        installments: cardFields.installments,
        customerEmail,
        browserInfo: captureWompiBrowserInfo(),
      };
    }
    return null;
  };

  const handleSubmit = async () => {
    const body = buildBody();
    if (!body) return;
    const result = await createTransaction(body);
    if (!result) return;
    if (result.redirectAction) {
      // Bold (PSE, Botón Bancolombia, 3DS): el deudor sale de la app y vuelve por
      // `RECEIVABLES_PAYMENT_REDIRECT_RETURN_URL` -- a diferencia del reto embebido de
      // Wompi, no hay nada más que mostrar aquí.
      window.location.href = result.redirectAction.redirectUrl;
      return;
    }
    setAttempt(result.attempt);
    setChallengeHtml(result.threeDsChallenge?.challengeHtml ?? null);
  };

  const isFinal = attempt && attempt.status !== "PENDING";
  const finalMeta = attempt ? FINAL_STATUS_META[attempt.status] : null;

  if (attempt) {
    return (
      <div className="flex flex-col gap-4">
        {!isFinal && (
          <WompiChallengePanel
            challengeHtml={challengeHtml}
            statusLabel={method ? WAITING_LABELS[method] : "Procesando el pago..."}
          />
        )}
        {isFinal && finalMeta && (
          <div className="flex flex-col items-center gap-3 rounded-lg border border-gray-200 bg-gray-50 p-5 text-center dark:border-gray-800 dark:bg-white/3">
            <Badge color={finalMeta.color} size="md">{finalMeta.label}</Badge>
            {attempt.status !== "APPROVED" && (
              <div className="flex gap-2">
                <Button type="button" size="sm" variant="outline" onClick={onCancel}>
                  Cancelar
                </Button>
                <Button
                  type="button"
                  size="sm"
                  onClick={() => { setAttempt(null); setChallengeHtml(null); }}
                >
                  Intentar de nuevo
                </Button>
              </div>
            )}
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-4">
      <p className="text-sm text-gray-600 dark:text-gray-400">
        Vas a pagar {formatCreditCurrency(payment.paymentAmount, currencyCode)}.
      </p>

      <div>
        <Label htmlFor="wompi-method">Método de pago</Label>
        <Select
          id="wompi-method"
          options={METHOD_OPTIONS}
          value={method}
          placeholder="Selecciona cómo quieres pagar"
          onChange={(v) => setMethod(v as WompiMethod)}
        />
      </div>

      {method !== "" && (
        <>
          <Input
            label="Correo electrónico"
            id="wompi-customer-email"
            type="email"
            value={customerEmail}
            onChange={(e) => setCustomerEmail(e.target.value)}
            placeholder="tucorreo@ejemplo.com"
          />

          {method === "NEQUI" && (
            <Input
              label="Número de celular Nequi"
              id="wompi-nequi-phone"
              maxLength={10}
              value={nequiPhone}
              onChange={(e) => setNequiPhone(e.target.value.replace(/\D/g, ""))}
              placeholder="3001234567"
            />
          )}

          {method === "PSE" && (
            <WompiPseFields
              value={pseFields}
              onChange={setPseFields}
              institutions={institutions}
              loadingInstitutions={loadingInstitutions}
            />
          )}

          {method === "CARD" && <WompiCardFields value={cardFields} onChange={setCardFields} />}

          <div className="flex justify-end gap-2">
            <Button type="button" size="sm" variant="outline" onClick={onCancel} disabled={submitting}>
              Cancelar
            </Button>
            <Button type="button" size="sm" onClick={handleSubmit} loading={submitting} loadingText="Procesando...">
              Pagar
            </Button>
          </div>
        </>
      )}
    </div>
  );
};
