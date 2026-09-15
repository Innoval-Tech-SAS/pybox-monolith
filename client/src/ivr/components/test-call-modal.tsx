import { useState } from "react";
import { Phone, AlertTriangle } from "lucide-react";
import { Modal } from "@/ui/components/modal/modal";
import { Input } from "@/ui/components/inputs/input";
import { Button } from "@/ui/components/button/button";

export type TestCallFormData = {
  phone: string;
  customerName: string;
  customerDocument: string;
};

type TestCallModalProps = {
  isOpen: boolean;
  onClose: () => void;
  /** Devuelve errores de validación/compilación del flujo (vacío = enviado). */
  onCall: (data: TestCallFormData) => Promise<{ ok: boolean; errors: string[] }>;
  sending: boolean;
};

const EMPTY: TestCallFormData = { phone: "", customerName: "", customerDocument: "" };

/**
 * Modal de llamada de prueba: pide un número (y datos opcionales) y dispara una
 * llamada única con el flujo actual. Muestra los errores de compilación del
 * flujo si los hay.
 */
export const TestCallModal: React.FC<TestCallModalProps> = ({
  isOpen,
  onClose,
  onCall,
  sending,
}) => {
  const [form, setForm] = useState<TestCallFormData>(EMPTY);
  const [errors, setErrors] = useState<string[]>([]);

  const isValid = form.phone.trim() !== "";

  const handleClose = () => {
    setForm(EMPTY);
    setErrors([]);
    onClose();
  };

  const handleCall = async () => {
    if (!isValid || sending) return;
    const res = await onCall(form);
    if (res.ok) {
      handleClose();
    } else {
      setErrors(res.errors);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={handleClose} className="m-4 max-w-md p-6">
      <div className="mb-5 flex items-center gap-3">
        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-success-50 dark:bg-success-500/10">
          <Phone size={18} className="text-success-600 dark:text-success-400" />
        </div>
        <div>
          <h4 className="text-base font-semibold text-gray-800 dark:text-white/90">
            Probar flujo
          </h4>
          <p className="text-xs text-gray-500 dark:text-gray-400">
            Envía una llamada de prueba con el flujo actual.
          </p>
        </div>
      </div>

      {errors.length > 0 && (
        <div className="mb-4 rounded-lg bg-error-50 px-3 py-2 text-xs text-error-700 dark:bg-error-500/10 dark:text-error-300">
          <div className="mb-1 flex items-center gap-2 font-medium">
            <AlertTriangle size={14} /> El flujo tiene errores:
          </div>
          <ul className="ml-6 list-disc space-y-0.5">
            {errors.map((err, i) => (
              <li key={i}>{err}</li>
            ))}
          </ul>
        </div>
      )}

      <div className="flex flex-col gap-4">
        <label className="flex flex-col gap-1 text-sm">
          <span className="font-medium text-gray-700 dark:text-gray-300">Teléfono *</span>
          <Input
            value={form.phone}
            onChange={(e) =>
              setForm((f) => ({ ...f, phone: e.target.value.replace(/\D/g, "") }))
            }
            placeholder="573001234567"
          />
        </label>
        <div className="grid grid-cols-2 gap-3">
          <label className="flex flex-col gap-1 text-sm">
            <span className="font-medium text-gray-700 dark:text-gray-300">Nombre</span>
            <Input
              value={form.customerName}
              onChange={(e) => setForm((f) => ({ ...f, customerName: e.target.value }))}
              placeholder="Juan Pérez"
            />
          </label>
          <label className="flex flex-col gap-1 text-sm">
            <span className="font-medium text-gray-700 dark:text-gray-300">Documento</span>
            <Input
              value={form.customerDocument}
              onChange={(e) =>
                setForm((f) => ({ ...f, customerDocument: e.target.value.replace(/\D/g, "") }))
              }
              placeholder="123456789"
            />
          </label>
        </div>

        <div className="flex gap-3 pt-1">
          <Button
            variant="outline"
            onClick={handleClose}
            disabled={sending}
            className="flex-1"
          >
            Cancelar
          </Button>
          <Button
            variant="primary"
            onClick={handleCall}
            disabled={!isValid || sending}
            startIcon={<Phone size={15} />}
            className="flex-1"
          >
            {sending ? "Llamando…" : "Llamar ahora"}
          </Button>
        </div>
      </div>
    </Modal>
  );
};
