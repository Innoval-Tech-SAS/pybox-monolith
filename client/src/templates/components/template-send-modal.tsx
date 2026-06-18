import { useState } from "react";
import { Mail } from "lucide-react";
import { Modal } from "@/ui/components/modal/modal";
import { Input } from "@/ui/components/inputs/input";
import { Label } from "@/ui/components/inputs/label";
import { extractVariables } from "@/templates/utils/template-variables";
import type { TemplateSendModalProps } from "@/templates/types/template-send-modal-props";

export const TemplateSendModal: React.FC<TemplateSendModalProps> = ({
  isOpen,
  template,
  saving,
  onClose,
  onSend,
}) => {
  const variables = template
    ? extractVariables((template.body ?? "") + " " + (template.subject ?? ""))
    : [];
  const [to, setTo] = useState("");
  const [subject, setSubject] = useState("");
  const [sub, setSub] = useState<Record<string, string>>({});

  const handleClose = () => {
    setTo(""); setSubject(""); setSub({});
    onClose();
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!template) return;
    await onSend(template.id, to, subject, sub);
    handleClose();
  };

  return (
    <Modal isOpen={isOpen} onClose={handleClose} className="max-w-lg mx-4 p-6 sm:p-8">
      <h2 className="mb-4 text-lg font-semibold text-gray-800 dark:text-white/90">
        Enviar email — {template?.name}
      </h2>
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <div>
          <Label htmlFor="send-to">Destinatario</Label>
          <Input id="send-to" type="email" value={to} onChange={(e) => setTo(e.target.value)} placeholder="destinatario@email.com" required />
        </div>
        <div>
          <Label htmlFor="send-subject">
            Asunto personalizado{" "}
            <span className="text-xs font-normal text-gray-400">(opcional)</span>
          </Label>
          <Input id="send-subject" value={subject} onChange={(e) => setSubject(e.target.value)} placeholder={template?.subject ?? ""} />
        </div>

        {variables.length > 0 && (
          <div>
            <p className="mb-2 text-xs font-medium uppercase tracking-wide text-gray-500 dark:text-gray-400">
              Variables
            </p>
            <div className="flex flex-col gap-3">
              {variables.map((v) => (
                <div key={v}>
                  <Label htmlFor={`send-${v}`}>{`{ ${v} }`}</Label>
                  <Input
                    id={`send-${v}`}
                    value={sub[v] ?? ""}
                    placeholder={`Valor para ${v}`}
                    onChange={(e) => setSub((prev) => ({ ...prev, [v]: e.target.value }))}
                    required
                  />
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="flex justify-end gap-3 pt-2">
          <button type="button" onClick={handleClose} className="rounded-lg border border-gray-300 px-4 py-2.5 text-sm font-medium text-gray-600 hover:bg-gray-50 dark:border-gray-700 dark:text-gray-400 dark:hover:bg-gray-800">
            Cancelar
          </button>
          <button type="submit" disabled={saving} className="inline-flex items-center gap-2 rounded-lg bg-brand-500 px-4 py-2.5 text-sm font-medium text-white hover:bg-brand-600 disabled:opacity-50">
            <Mail size={14} />
            {saving ? "Enviando…" : "Enviar"}
          </button>
        </div>
      </form>
    </Modal>
  );
};
