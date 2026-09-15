import { useEffect, useRef, useState } from "react";
import { useToast } from "@/context/toast-context";
import { Spinner } from "@/ui/components/loader/spinner";
import { Select } from "@/ui/components/inputs/select";
import type { MercadoPagoProviderPayload } from "@/types/billing/billing-types";
import type { IdentificationType, MercadoPagoInstance } from "@/types/billing/mercadopago-sdk-types";
import type { MercadoPagoCardFormProps } from "@/types/props/mercadopago-card-form-props";

// Docs: https://www.mercadopago.com/developers/es/docs/sdks-library/client-side/mp-js-v2
const MP_SCRIPT_SRC = "https://sdk.mercadopago.com/js/v2";

let mpScriptPromise: Promise<void> | null = null;

const loadMercadoPagoScript = (): Promise<void> => {
  if (mpScriptPromise) return mpScriptPromise;
  mpScriptPromise = new Promise((resolve, reject) => {
    if (document.querySelector(`script[src="${MP_SCRIPT_SRC}"]`)) {
      resolve();
      return;
    }
    const script = document.createElement("script");
    script.src = MP_SCRIPT_SRC;
    script.async = true;
    script.onload = () => resolve();
    script.onerror = () => reject(new Error("No se pudo cargar el SDK de Mercado Pago"));
    document.head.appendChild(script);
  });
  return mpScriptPromise;
};

export const MercadoPagoCardForm: React.FC<MercadoPagoCardFormProps> = ({ data, onCharge }) => {
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

    loadMercadoPagoScript()
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

  const handleSubmit = async (e: React.FormEvent) => {
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

  const inputClass =
    "w-full rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs focus:border-brand-300 focus:outline-none dark:border-gray-700 dark:bg-gray-800 dark:text-white/90";
  const secureFieldClass =
    "h-[42px] w-full rounded-lg border border-gray-300 bg-white px-4 py-2.5 dark:border-gray-700 dark:bg-gray-800";

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
        <div className="sm:col-span-2">
          <label className="mb-1.5 block text-xs font-medium text-gray-600 dark:text-gray-400">
            Número de tarjeta
          </label>
          <div id="mp-card-number" className={secureFieldClass} />
        </div>
        <div>
          <label className="mb-1.5 block text-xs font-medium text-gray-600 dark:text-gray-400">Vencimiento</label>
          <div id="mp-expiration-date" className={secureFieldClass} />
        </div>
        <div>
          <label className="mb-1.5 block text-xs font-medium text-gray-600 dark:text-gray-400">CVV</label>
          <div id="mp-security-code" className={secureFieldClass} />
        </div>
        <div className="sm:col-span-2">
          <label className="mb-1.5 block text-xs font-medium text-gray-600 dark:text-gray-400">
            Nombre del titular
          </label>
          <input
            type="text"
            value={cardholderName}
            onChange={(e) => setCardholderName(e.target.value)}
            className={inputClass}
            placeholder="Como aparece en la tarjeta"
          />
        </div>
        {identificationRequired && (
          <>
            <div>
              <label className="block text-xs font-medium text-gray-600 dark:text-gray-400">
                <span className="mb-1.5 block">Tipo de documento</span>
                <Select
                  options={identificationTypes.map((t) => ({ value: t.id, label: t.name }))}
                  value={identificationType}
                  onChange={setIdentificationType}
                />
              </label>
            </div>
            <div>
              <label className="mb-1.5 block text-xs font-medium text-gray-600 dark:text-gray-400">
                Número de documento
              </label>
              <input
                type="text"
                value={identificationNumber}
                onChange={(e) => setIdentificationNumber(e.target.value)}
                className={inputClass}
              />
            </div>
          </>
        )}
      </div>

      <button
        type="submit"
        disabled={!ready || submitting}
        className="inline-flex items-center gap-2 rounded-lg bg-brand-500 px-4 py-2.5 text-sm font-medium text-white shadow-theme-xs hover:bg-brand-600 disabled:opacity-50"
      >
        {submitting && <Spinner size="xs" tone="white" />}
        {submitting ? "Procesando pago..." : "Pagar con tarjeta"}
      </button>
    </form>
  );
};
