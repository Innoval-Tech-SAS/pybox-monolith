import { Modal } from "@/ui/components/modal/modal";
import { Button } from "@/ui/components/button/button";
import { PaymentResultView } from "./payment-result-view";
import type { PaymentResultModalProps } from "@/billing/types/props/payment-result-modal-props";

/**
 * Modal de resultado para Mercado Pago (cobro inline, sin redirect). Reusa la misma vista
 * que la página de resultado de Bold.
 */
export const PaymentResultModal: React.FC<PaymentResultModalProps> = ({
  isOpen,
  status,
  reference,
  onClose,
  onRetry,
}) => {
  const canRetry = (status === "DECLINED" || status === "ERROR") && !!onRetry;

  return (
    <Modal isOpen={isOpen} onClose={onClose} showCloseButton={false} className="max-w-md p-6 sm:p-8">
      <PaymentResultView status={status} reference={reference}>
        <div className="mt-2 flex flex-col gap-2">
          {canRetry && (
            <Button type="button" size="sm" className="w-full" onClick={onRetry}>
              Intentar de nuevo
            </Button>
          )}
          <Button type="button" size="sm" variant="outline" className="w-full" onClick={onClose}>
            Cerrar
          </Button>
        </div>
      </PaymentResultView>
    </Modal>
  );
};
