import { Button } from "@/ui/components/button/button";
import { BoldPaymentButton } from "./bold-payment-button";
import { MercadoPagoCardForm } from "./mercadopago-card-form";
import type { InvoicePaymentSectionProps } from "../types/props/invoice-payment-section-props";

export const InvoicePaymentSection: React.FC<InvoicePaymentSectionProps> = ({
  paymentLink,
  paying,
  onPay,
  onMercadoPagoCharge,
}) => (
  <div className="mt-5 border-t border-gray-100 pt-5 dark:border-gray-800">
    {!paymentLink ? (
      <Button type="button" size="sm" onClick={onPay} loading={paying} loadingText="Generando enlace de pago...">
        Pagar factura
      </Button>
    ) : paymentLink.provider === "MERCADO_PAGO" ? (
      <MercadoPagoCardForm data={paymentLink} onCharge={onMercadoPagoCharge} />
    ) : (
      <BoldPaymentButton data={paymentLink} />
    )}
  </div>
);
