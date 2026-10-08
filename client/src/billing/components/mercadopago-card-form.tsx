import { Select } from "@/ui/components/inputs/select";
import { Input } from "@/ui/components/inputs/input";
import { Button } from "@/ui/components/button/button";
import { useMercadoPagoCardForm } from "../hooks/use-mercadopago-card-form";
import type { MercadoPagoCardFormProps } from "../types/props/mercadopago-card-form-props";

const secureFieldClass =
  "h-[42px] w-full rounded-lg border border-gray-300 bg-white px-4 py-2.5 dark:border-gray-700 dark:bg-gray-800";

export const MercadoPagoCardForm: React.FC<MercadoPagoCardFormProps> = ({ data, onCharge }) => {
  const {
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
  } = useMercadoPagoCardForm(data, onCharge);

  return (
    <form onSubmit={submit} className="space-y-4">
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
          <Input
            type="text"
            value={cardholderName}
            onChange={(e) => setCardholderName(e.target.value)}
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
              <Input
                type="text"
                value={identificationNumber}
                onChange={(e) => setIdentificationNumber(e.target.value)}
              />
            </div>
          </>
        )}
      </div>

      <Button
        type="submit"
        size="sm"
        disabled={!ready}
        loading={submitting}
        loadingText="Procesando pago..."
      >
        Pagar con tarjeta
      </Button>
    </form>
  );
};
