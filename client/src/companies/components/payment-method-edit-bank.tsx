import { Card, CardTitle } from "@/ui/components/card";
import { Input } from "@/ui/components/input";
import type { PaymentMethodEditBankProps } from "@/companies/types/payment-method-edit-form-props";

export const PaymentMethodEditBank: React.FC<PaymentMethodEditBankProps> = ({ form, field }) => (
  <Card>
    <CardTitle>Datos bancarios / digitales</CardTitle>
    <div className="grid grid-cols-1 gap-5 sm:grid-cols-2">
      <Input
        label="Banco"
        id="bankName"
        value={form.bankName}
        onChange={field("bankName")}
        placeholder="Nombre del banco"
      />
      <Input
        label="Tipo de cuenta"
        id="accountType"
        value={form.accountType}
        onChange={field("accountType")}
        placeholder="Ahorros / Corriente"
      />
      <div className="sm:col-span-2">
        <Input
          label="Número de cuenta"
          id="accountNumber"
          value={form.accountNumber}
          onChange={field("accountNumber")}
          placeholder="Número de cuenta"
        />
      </div>
      <div className="sm:col-span-2">
        <Input
          label="Enlace de pago"
          id="paymentLink"
          value={form.paymentLink}
          onChange={field("paymentLink")}
          placeholder="https://..."
        />
      </div>
      <div className="sm:col-span-2">
        <Input
          label="URL imagen QR"
          id="qrImageUrl"
          value={form.qrImageUrl}
          onChange={field("qrImageUrl")}
          placeholder="https://..."
        />
      </div>
    </div>
  </Card>
);
