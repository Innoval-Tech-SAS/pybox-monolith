import { useState } from "react";
import { Paperclip, X } from "lucide-react";
import { Modal } from "@/ui/components/modal/modal";
import { useJudicialPriorities } from "@/credits/hooks/use-judicial-priorities";
import { useUploadJudicialAttachments } from "@/credits/hooks/use-upload-judicial-attachments";
import type { JudicialNotification, JudicialNotificationCreatePayload } from "@/credits/types/judicial-types";

const INPUT_CLASS =
  "w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/20 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:placeholder:text-white/30 dark:focus:border-brand-800";

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
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            maxLength={255}
            required
            className={INPUT_CLASS}
            placeholder="Ej. Embargo de cuenta bancaria"
          />
        </div>

        <div>
          <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">Detalle</label>
          <textarea
            value={body}
            onChange={(e) => setBody(e.target.value)}
            maxLength={1000}
            required
            rows={4}
            className={INPUT_CLASS}
            placeholder="Describe el hecho judicial"
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">Prioridad</label>
            <select
              value={priority}
              onChange={(e) => setPriority(e.target.value)}
              required
              disabled={loadingPriorities}
              className={INPUT_CLASS}
            >
              <option value="" disabled>
                Selecciona...
              </option>
              {priorities.map((p) => (
                <option key={p.value} value={p.value}>
                  {p.label}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
              Fecha del hecho
            </label>
            <input
              type="date"
              value={notifiedAt}
              onChange={(e) => setNotifiedAt(e.target.value)}
              className={INPUT_CLASS}
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
          <button
            type="button"
            onClick={handleClose}
            className="rounded-lg border border-gray-300 px-4 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50 dark:border-gray-700 dark:text-gray-300 dark:hover:bg-white/5"
          >
            Cancelar
          </button>
          <button
            type="submit"
            disabled={submitting || uploading}
            className="rounded-lg bg-brand-500 px-4 py-2.5 text-sm font-medium text-white shadow-theme-xs hover:bg-brand-600 disabled:opacity-60"
          >
            {submitting || uploading ? "Emitiendo..." : "Emitir notificación"}
          </button>
        </div>
      </form>
    </Modal>
  );
};
