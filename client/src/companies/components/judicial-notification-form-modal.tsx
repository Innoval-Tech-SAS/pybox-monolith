import { useState } from "react";
import { Paperclip, X } from "lucide-react";
import { Modal } from "@/ui/components/modal/modal";
import { Input } from "@/ui/components/inputs/input";
import { Select } from "@/ui/components/inputs/select";
import { Textarea } from "@/ui/components/inputs/textarea";
import { Button } from "@/ui/components/button/button";
import { useJudicialPriorities } from "@/credits/hooks/use-judicial-priorities";
import { useUploadJudicialAttachments } from "@/credits/hooks/use-upload-judicial-attachments";
import type { JudicialNotification, JudicialNotificationCreatePayload } from "@/credits/types/judicial-types";

interface JudicialNotificationFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  creditId: string;
  /** Crea la notificación (POST /judicial-notifications); lo hace la página para que
   * la lista que ella mantiene se actualice en un solo lugar. */
  onSubmit: (payload: JudicialNotificationCreatePayload) => Promise<JudicialNotification | null>;
  submitting: boolean;
  onCreated: (notification: JudicialNotification) => void;
}

/** Formulario para que la entidad emita una notificación judicial sobre un crédito,
 * con soporte documental opcional (flujo en 2 pasos: crea y luego adjunta). */
export const JudicialNotificationFormModal: React.FC<JudicialNotificationFormModalProps> = ({
  isOpen,
  onClose,
  creditId,
  onSubmit,
  submitting,
  onCreated,
}) => {
  const { priorities, loading: loadingPriorities } = useJudicialPriorities();
  const { uploadAttachments, loading: uploading } = useUploadJudicialAttachments();

  const [title, setTitle] = useState("");
  const [body, setBody] = useState("");
  const [priority, setPriority] = useState("");
  const [notifiedAt, setNotifiedAt] = useState("");
  const [files, setFiles] = useState<File[]>([]);

  const reset = () => {
    setTitle("");
    setBody("");
    setPriority("");
    setNotifiedAt("");
    setFiles([]);
  };

  const handleClose = () => {
    reset();
    onClose();
  };

  const addFiles = (list: FileList | null) => {
    if (!list) return;
    setFiles((prev) => {
      const existing = new Set(prev.map((f) => f.name));
      return [...prev, ...Array.from(list).filter((f) => !existing.has(f.name))];
    });
  };

  const removeFile = (name: string) => setFiles((prev) => prev.filter((f) => f.name !== name));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim() || !body.trim() || !priority) return;

    const created = await onSubmit({
      creditId,
      title: title.trim(),
      body: body.trim(),
      priority,
      notifiedAt: notifiedAt ? new Date(notifiedAt).toISOString() : undefined,
    });
    if (!created) return;

    const withAttachments = files.length > 0 ? await uploadAttachments(created.id, files) : created;
    onCreated(withAttachments ?? created);
    handleClose();
  };

  return (
    <Modal isOpen={isOpen} onClose={handleClose} className="max-w-lg p-6 lg:p-8">
      <h3 className="mb-5 text-lg font-semibold text-gray-800 dark:text-white/90">Nueva notificación judicial</h3>
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <div>
          <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">Título</label>
          <Input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            maxLength={255}
            required
            placeholder="Ej. Embargo de cuenta bancaria"
          />
        </div>

        <div>
          <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">Detalle</label>
          <Textarea
            value={body}
            onChange={(e) => setBody(e.target.value)}
            maxLength={1000}
            required
            rows={4}
            placeholder="Describe el hecho judicial"
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">Prioridad</label>
            <Select
              options={priorities}
              value={priority}
              onChange={setPriority}
              required
              disabled={loadingPriorities}
              placeholder="Selecciona..."
            />
          </div>
          <div>
            <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
              Fecha del hecho
            </label>
            <Input
              type="date"
              value={notifiedAt}
              onChange={(e) => setNotifiedAt(e.target.value)}
            />
          </div>
        </div>

        <div>
          <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
            Adjuntos (PDF, PNG, JPG o WebP)
          </label>
          <label className="flex cursor-pointer items-center justify-center gap-2 rounded-lg border border-dashed border-gray-300 px-4 py-3 text-sm text-gray-500 hover:border-brand-300 hover:text-brand-600 dark:border-gray-700 dark:text-gray-400">
            <Paperclip size={14} />
            Adjuntar archivos
            <input
              type="file"
              multiple
              accept=".pdf,.png,.jpg,.jpeg,.webp"
              className="hidden"
              onChange={(e) => addFiles(e.target.files)}
            />
          </label>
          {files.length > 0 && (
            <ul className="mt-2 flex flex-col gap-1.5">
              {files.map((file) => (
                <li
                  key={file.name}
                  className="flex items-center justify-between gap-2 rounded-lg bg-gray-50 px-3 py-1.5 text-xs text-gray-600 dark:bg-white/5 dark:text-gray-300"
                >
                  <span className="min-w-0 truncate">{file.name}</span>
                  <button
                    type="button"
                    onClick={() => removeFile(file.name)}
                    className="shrink-0 text-gray-400 hover:text-error-500"
                  >
                    <X size={14} />
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="mt-2 flex justify-end gap-3">
          <Button type="button" size="sm" variant="outline" onClick={handleClose}>
            Cancelar
          </Button>
          <Button type="submit" size="sm" loading={submitting || uploading} loadingText="Emitiendo...">
            Emitir notificación
          </Button>
        </div>
      </form>
    </Modal>
  );
};
