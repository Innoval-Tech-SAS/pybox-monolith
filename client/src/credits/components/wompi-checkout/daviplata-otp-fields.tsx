import { Button } from "@/ui/components/button/button";
import { Input } from "@/ui/components/inputs/input";

interface DaviplataOtpFieldsProps {
  otp: string;
  onChangeOtp: (otp: string) => void;
  onConfirm: () => void;
  confirming: boolean;
}

/**
 * Daviplata (ePayco) no se resuelve ni por redirección ni por notificación push
 * esperada en silencio -- el deudor recibe un OTP en su app y lo debe transcribir
 * aquí (ver `OtpChallenge`) para que `confirmDaviplataOtp` cierre el cobro.
 */
export const DaviplataOtpFields: React.FC<DaviplataOtpFieldsProps> = ({
  otp,
  onChangeOtp,
  onConfirm,
  confirming,
}) => (
  <div className="flex flex-col items-center gap-4 text-center">
    <p className="text-sm text-gray-600 dark:text-gray-400">
      Revisa tu app Daviplata: te enviamos un código de confirmación. Escríbelo aquí
      para completar el pago.
    </p>
    <Input
      label="Código OTP"
      id="daviplata-otp"
      maxLength={6}
      value={otp}
      onChange={(e) => onChangeOtp(e.target.value.replace(/\D/g, ""))}
      placeholder="123456"
    />
    <Button
      type="button"
      size="sm"
      className="w-full"
      onClick={onConfirm}
      loading={confirming}
      loadingText="Confirmando..."
      disabled={!otp}
    >
      Confirmar pago
    </Button>
  </div>
);
