import { useState } from "react";
import { Modal } from "@/ui/components/modal/modal";
import { useCreateTicket } from "@/support/hooks/use-create-ticket";
import { useTicketOrgs } from "@/support/hooks/use-ticket-orgs";
import type { CreateTicketModalProps } from "@/types/props/create-ticket-modal-props";

export const CreateTicketModal: React.FC<CreateTicketModalProps> = ({ isOpen, onClose, onCreated }) => {
  const { createTicket, loading } = useCreateTicket();
  const { orgs, loading: loadingOrgs } = useTicketOrgs();

  const [organizationId, setOrganizationId] = useState("");
  const [title, setTitle] = useState("");
  const [notes, setNotes] = useState("");

  const handleClose = () => {
    setOrganizationId("");
    setTitle("");
    setNotes("");
    onClose();
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!organizationId || !title.trim()) return;
    const ticket = await createTicket({ organizationId, title: title.trim(), notes: notes.trim() || undefined });
    if (ticket) {
      onCreated(ticket);
      handleClose();
    }
  };

  const inputClass =
    "w-full rounded-lg border border-gray-200 bg-white px-3 py-2 text-sm text-gray-700 placeholder-gray-400 focus:border-brand-300 focus:outline-none dark:border-gray-700 dark:bg-gray-900 dark:text-gray-300 dark:placeholder-gray-600 dark:focus:border-brand-500";

  return (
    <Modal isOpen={isOpen} onClose={handleClose} className="max-w-lg p-6 sm:p-8">
      <h2 className="mb-5 text-lg font-semibold text-gray-800 dark:text-white/90">Nuevo ticket</h2>
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <div>
          <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
            Entidad
          </label>
          {loadingOrgs ? (
            <div className="h-9 animate-pulse rounded-lg bg-gray-100 dark:bg-gray-800" />
          ) : (
            <select
              value={organizationId}
              onChange={(e) => setOrganizationId(e.target.value)}
              required
              className={inputClass}
            >
              <option value="">Seleccionar entidad...</option>
              {orgs.map((org) => (
                <option key={org.id} value={org.id}>
                  {org.name}
                </option>
              ))}
            </select>
          )}
        </div>

        <div>
          <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
            Título
          </label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Describe brevemente el problema..."
            required
            className={inputClass}
          />
        </div>

        <div>
          <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
            Notas <span className="font-normal text-gray-400">(opcional)</span>
          </label>
          <textarea
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="Información adicional..."
            rows={3}
            className={`${inputClass} resize-none`}
          />
        </div>

        <div className="flex justify-end gap-3 pt-1">
          <button
            type="button"
            onClick={handleClose}
            className="rounded-lg border border-gray-200 px-4 py-2 text-sm font-medium text-gray-600 hover:bg-gray-50 dark:border-gray-700 dark:text-gray-400 dark:hover:bg-white/5"
          >
            Cancelar
          </button>
          <button
            type="submit"
            disabled={loading || !organizationId || !title.trim()}
            className="rounded-lg bg-brand-500 px-4 py-2 text-sm font-medium text-white hover:bg-brand-600 disabled:opacity-60"
          >
            {loading ? "Creando..." : "Crear ticket"}
          </button>
        </div>
      </form>
    </Modal>
  );
};
