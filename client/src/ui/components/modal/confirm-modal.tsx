import { AlertTriangle } from "lucide-react";
import { Modal } from "./modal";
import { Loader } from "@/ui/components/loader/loader";
import { ConfirmModalProps } from "@/types/props/confirm-modal-props";

export const ConfirmModal: React.FC<ConfirmModalProps> = ({
  isOpen,
  onClose,
  onConfirm,
  title,
  message,
  confirmLabel = "Eliminar",
  cancelLabel = "Cancelar",
  variant = "danger",
  loading = false,
}) => {
  const confirmClasses =
    variant === "danger"
      ? "bg-error-500 hover:bg-error-600"
      : "bg-brand-500 hover:bg-brand-600";

  return (
    <Modal isOpen={isOpen} onClose={onClose} className="max-w-md p-6 sm:p-8" showCloseButton={false}>
      <div className="text-center">
        <div
          className={`mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-full ${
            variant === "danger"
              ? "bg-error-50 text-error-500 dark:bg-error-500/15"
              : "bg-brand-50 text-brand-500 dark:bg-brand-500/15"
          }`}
        >
          <AlertTriangle size={26} />
        </div>
        <h4 className="mb-2 text-lg font-semibold text-gray-800 dark:text-white/90">{title}</h4>
        <p className="text-sm leading-6 text-gray-500 dark:text-gray-400">{message}</p>

        <div className="mt-6 flex items-center justify-center gap-3">
          <button
            type="button"
            onClick={onClose}
            disabled={loading}
            className="flex-1 rounded-lg border border-gray-300 px-4 py-2.5 text-sm font-medium text-gray-700 transition hover:bg-gray-50 disabled:opacity-50 dark:border-gray-700 dark:text-gray-300 dark:hover:bg-white/5"
          >
            {cancelLabel}
          </button>
          <button
            type="button"
            onClick={onConfirm}
            disabled={loading}
            className={`flex flex-1 items-center justify-center gap-2 rounded-lg px-4 py-2.5 text-sm font-medium text-white transition disabled:opacity-50 ${confirmClasses}`}
          >
            {loading ? <Loader /> : confirmLabel}
          </button>
        </div>
      </div>
    </Modal>
  );
};
