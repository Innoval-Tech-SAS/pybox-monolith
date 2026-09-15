import { useEffect, useRef, useState } from "react";
import { useToast } from "@/context/toast-context";
import type { MercadoPagoProviderPayload, PaymentLinkData } from "@/types/billing/billing-types";
import type { IdentificationType, MercadoPagoInstance } from "@/types/billing/mercadopago-sdk-types";
import { MERCADOPAGO_SCRIPT_SRC } from "../constants/payment-provider-scripts";
import { loadExternalScript } from "../utils/load-external-script";

type OnCharge = (
  token: string,
  paymentMethodId: string,
  paymentTypeId: string,
  installments: number,
) => Promise<void>;

/**
 * Orquesta el SDK de Mercado Pago (Secure Fields) para un formulario de tarjeta: carga el
 * script, monta los campos seguros, detecta el medio de pago por BIN y tokeniza al enviar.
 */
export const useMercadoPagoCardForm = (data: PaymentLinkData, onCharge: OnCharge) => {
  const payload = data.providerPayload as MercadoPagoProviderPayload;
  const { error: toastError } = useToast();

  const mpRef = useRef<MercadoPagoInstance | null>(null);
  const paymentMethodIdRef = useRef<string | null>(null);
  const paymentTypeIdRef = useRef<string | null>(null);
  const fieldsMounted = useRef(false);
  const submittingRef = useRef(false);

  const [ready, setReady] = useState(false);
  const [identificationTypes, setIdentificationTypes] = useState<IdentificationType[]>([]);
  const [cardholderName, setCardholderName] = useState("");
  const [identificationType, setIdentificationType] = useState("");
  const [identificationNumber, setIdentificationNumber] = useState("");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (fieldsMounted.current) return;
    fieldsMounted.current = true;

    loadExternalScript(MERCADOPAGO_SCRIPT_SRC, "No se pudo cargar el SDK de Mercado Pago")
      .then(async () => {
        if (!window.MercadoPago) throw new Error("SDK de Mercado Pago no disponible");
        const mp = new window.MercadoPago(payload.publicKey);
        mpRef.current = mp;

        const cardNumber = mp.fields.create("cardNumber", { placeholder: "Número de tarjeta" }).mount("mp-card-number");
        mp.fields.create("expirationDate", { placeholder: "MM/YY" }).mount("mp-expiration-date");
        mp.fields.create("securityCode", { placeholder: "CVV" }).mount("mp-security-code");

        cardNumber.on("binChange", async ({ bin }) => {
          if (!bin) {
            paymentMethodIdRef.current = null;
            paymentTypeIdRef.current = null;
            return;
          }
          try {
            // MP detecta la marca y el tipo (credito/debito) a partir del BIN. Se guardan
            // ambos: la Orders API exige que el `type` corresponda al `id` (visa/master/amex
            // -> credit_card; debvisa/debmaster/... -> debit_card).
            const { results } = await mp.getPaymentMethods({ bin });
            paymentMethodIdRef.current = results[0]?.id ?? null;
            paymentTypeIdRef.current = results[0]?.payment_type_id ?? null;
          } catch {
            paymentMethodIdRef.current = null;
            paymentTypeIdRef.current = null;
          }
        });

        try {
          const types = await mp.getIdentificationTypes();
          setIdentificationTypes(types);
          if (types[0]) setIdentificationType(types[0].id);
        } catch {
          // Algunos paises (ej. Mexico) no exigen tipo/numero de documento para tokenizar
          // la tarjeta; MP responde 404 y el formulario simplemente omite esos campos.
          setIdentificationTypes([]);
        }

        setReady(true);
      })
      .catch(() => {
        toastError("Error", "No se pudo cargar el formulario de pago de Mercado Pago");
      });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [payload.publicKey]);

  const identificationRequired = identificationTypes.length > 0;

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!mpRef.current || submittingRef.current) return;

    if (
      !cardholderName.trim() ||
      (identificationRequired && (!identificationType || !identificationNumber.trim()))
    ) {
      toastError("Error", "Completa los datos del titular de la tarjeta");
      return;
    }
    if (!paymentMethodIdRef.current || !paymentTypeIdRef.current) {
      toastError("Error", "No se pudo identificar la tarjeta, revisa el número ingresado");
      return;
    }

    submittingRef.current = true;
    setSubmitting(true);
    try {
      const token = await mpRef.current.fields.createCardToken({
        cardholderName,
        ...(identificationRequired ? { identificationType, identificationNumber } : {}),
      });
      await onCharge(token.id, paymentMethodIdRef.current, paymentTypeIdRef.current, 1);
    } catch {
      toastError("Error", "No se pudo procesar el pago, verifica los datos de la tarjeta");
    } finally {
      submittingRef.current = false;
      setSubmitting(false);
    }
  };

  return {
    ready,
    identificationTypes,
    identificationRequired,
    cardholderName,
    setCardholderName,
    identificationType,
    setIdentificationType,
    identificationNumber,
    setIdentificationNumber,
    submitting,
    submit,
  };
};
