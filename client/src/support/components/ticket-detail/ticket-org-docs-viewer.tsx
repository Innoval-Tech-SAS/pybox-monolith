import { useState } from "react";
import { FileText, ExternalLink, CheckCircle, XCircle } from "lucide-react";
import { resolveProfilePhotoUrl } from "@/profile/utils/profile-photo-url";
import { useTicketOrgDocs } from "@/support/hooks/use-ticket-org-docs";
import { useResolveTicket } from "@/support/hooks/use-resolve-ticket";
import type { SupportTicket } from "@/types/support/support-types";

interface TicketOrgDocsViewerProps {
  ticket: SupportTicket;
  onResolved: (updated: SupportTicket) => void;
}

export const TicketOrgDocsViewer: React.FC<TicketOrgDocsViewerProps> = ({
  ticket,
  onResolved,
}) => {
  const { orgDocs, loading } = useTicketOrgDocs(ticket.id, true);
  const { resolveTicket, loading: resolving } = useResolveTicket();
  const [notes, setNotes] = useState("");
  const [showNotesInput, setShowNotesInput] = useState(false);
  const [pendingApproval, setPendingApproval] = useState<boolean | null>(null);

  const isResolved = ticket.status === "resolved";

  const handleDecision = (approved: boolean) => {
    setPendingApproval(approved);
    setShowNotesInput(true);
  };

  const handleConfirm = async () => {
    if (pendingApproval === null) return;
    const updated = await resolveTicket(ticket.id, { approved: pendingApproval, notes: notes || undefined });
    if (updated) {
      onResolved(updated);
      setShowNotesInput(false);
      setNotes("");
    }
  };

  if (loading) {
    return (
      <div className="mt-6 rounded-xl border border-gray-100 bg-gray-50 p-4 dark:border-gray-800 dark:bg-white/[0.03]">
        <p className="text-xs font-semibold uppercase tracking-wide text-gray-400 dark:text-gray-500">
          Documentos de verificación
        </p>
        <p className="mt-2 text-sm text-gray-400">Cargando documentos...</p>
      </div>
    );
  }

  return (
    <div className="mt-6">
      <p className="mb-3 text-xs font-semibold uppercase tracking-wide text-gray-400 dark:text-gray-500">
        Documentos de verificación
        {orgDocs && (
          <span className="ml-2 normal-case font-normal text-gray-500 dark:text-gray-400">
            — {orgDocs.orgName}
          </span>
        )}
      </p>

      <div className="overflow-hidden rounded-xl border border-gray-100 dark:border-gray-800">
        <table className="w-full border-collapse table-auto">
          <thead>
            <tr className="bg-gray-50 dark:bg-white/[0.02]">
              <th className="px-4 py-2.5 text-left text-xs font-medium text-gray-500 dark:text-gray-400">
                Documento
              </th>
              <th className="px-4 py-2.5 text-center text-xs font-medium text-gray-500 dark:text-gray-400 w-24">
                Acción
              </th>
            </tr>
          </thead>
          <tbody>
            {orgDocs ? (
              orgDocs.documents.map((doc, i) => {
                const url = resolveProfilePhotoUrl(doc.url);
                return (
                  <tr
                    key={i}
                    className="border-t border-gray-100 dark:border-gray-800"
                  >
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-3">
                        <div className="flex size-9 shrink-0 items-center justify-center rounded-lg bg-brand-50 text-brand-500 dark:bg-brand-500/10 dark:text-brand-400">
                          <FileText size={16} />
                        </div>
                        <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                          {doc.label}
                        </span>
                      </div>
                    </td>
                    <td className="px-4 py-3 text-center">
                      {url ? (
                        <a
                          href={url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center gap-1.5 rounded-lg bg-gray-100 px-3 py-1.5 text-xs font-medium text-gray-600 hover:bg-brand-50 hover:text-brand-600 dark:bg-white/[0.05] dark:text-gray-400 dark:hover:bg-brand-500/10 dark:hover:text-brand-400"
                        >
                          <ExternalLink size={12} />
                          Ver
                        </a>
                      ) : (
                        <span className="text-xs text-gray-400 dark:text-gray-500">
                          Sin archivo
                        </span>
                      )}
                    </td>
                  </tr>
                );
              })
            ) : (
              <tr>
                <td colSpan={2} className="px-4 py-6 text-center text-sm text-gray-400">
                  No se pudieron cargar los documentos.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {!isResolved && orgDocs && (
        <div className="mt-4">
          {!showNotesInput ? (
            <div className="flex gap-3">
              <button
                onClick={() => handleDecision(true)}
                className="inline-flex items-center gap-2 rounded-lg bg-success-50 px-4 py-2 text-sm font-medium text-success-700 hover:bg-success-100 dark:bg-success-500/10 dark:text-success-400 dark:hover:bg-success-500/20"
              >
                <CheckCircle size={15} />
                Aprobar
              </button>
              <button
                onClick={() => handleDecision(false)}
                className="inline-flex items-center gap-2 rounded-lg bg-error-50 px-4 py-2 text-sm font-medium text-error-700 hover:bg-error-100 dark:bg-error-500/10 dark:text-error-400 dark:hover:bg-error-500/20"
              >
                <XCircle size={15} />
                Rechazar
              </button>
            </div>
          ) : (
            <div className="rounded-xl border border-gray-100 bg-gray-50 p-4 dark:border-gray-800 dark:bg-white/[0.03]">
              <p className="mb-2 text-sm font-medium text-gray-700 dark:text-gray-300">
                {pendingApproval ? "Aprobando verificación" : "Rechazando verificación"}
                <span
                  className={`ml-2 inline-flex items-center rounded-full px-2 py-0.5 text-xs font-semibold ${
                    pendingApproval
                      ? "bg-success-50 text-success-700 dark:bg-success-500/10 dark:text-success-400"
                      : "bg-error-50 text-error-700 dark:bg-error-500/10 dark:text-error-400"
                  }`}
                >
                  {pendingApproval ? "Aprobar" : "Rechazar"}
                </span>
              </p>
              <textarea
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="Notas opcionales para el equipo o la empresa..."
                rows={3}
                className="w-full resize-none rounded-lg border border-gray-200 bg-white px-3 py-2 text-sm text-gray-700 placeholder-gray-400 focus:border-brand-300 focus:outline-none dark:border-gray-700 dark:bg-gray-900 dark:text-gray-300 dark:placeholder-gray-600 dark:focus:border-brand-500"
              />
              <div className="mt-3 flex gap-2">
                <button
                  onClick={handleConfirm}
                  disabled={resolving}
                  className={`inline-flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-medium text-white disabled:opacity-60 ${
                    pendingApproval
                      ? "bg-success-500 hover:bg-success-600"
                      : "bg-error-500 hover:bg-error-600"
                  }`}
                >
                  {resolving ? "Procesando..." : "Confirmar"}
                </button>
                <button
                  onClick={() => { setShowNotesInput(false); setPendingApproval(null); setNotes(""); }}
                  className="rounded-lg border border-gray-200 px-4 py-2 text-sm font-medium text-gray-600 hover:bg-gray-50 dark:border-gray-700 dark:text-gray-400 dark:hover:bg-white/5"
                >
                  Cancelar
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {isResolved && (
        <p className="mt-3 flex items-center gap-1.5 text-sm text-success-600 dark:text-success-400">
          <CheckCircle size={14} />
          Ticket resuelto
        </p>
      )}
    </div>
  );
};
