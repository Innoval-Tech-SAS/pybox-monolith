import { Modal } from "@/ui/components/modal/modal";
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
            <button
              onClick={onRetry}
              className="w-full rounded-lg bg-brand-500 px-4 py-2.5 text-sm font-medium text-white shadow-theme-xs hover:bg-brand-600"
            >
              Intentar de nuevo
            </button>
          )}
          <button
            onClick={onClose}
            className="w-full rounded-lg border border-gray-300 px-4 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50 dark:border-gray-700 dark:text-gray-300 dark:hover:bg-gray-800"
          >
            Cerrar
          </button>
        </div>
      </PaymentResultView>
    </Modal>
  );
};
