import { UserX, X } from "lucide-react";
import { Loader } from "@/ui/components/loader/loader";
import EmptyState from "@/ui/components/common/empty-state";
import { useCreditTypes } from "@/credits/hooks/use-credit-types";
import type { WhatsAppChatDetails } from "../types/whatsapp-chat-types";

interface WhatsAppChatDetailsPanelProps {
  open: boolean;
  loading: boolean;
  details: WhatsAppChatDetails | null;
  onClose: () => void;
}

const Field: React.FC<{ label: string; value: React.ReactNode }> = ({ label, value }) => (
  <div>
    <p className="text-xs text-gray-400 dark:text-gray-500">{label}</p>
    <p className="text-sm text-gray-800 dark:text-white/90">{value}</p>
  </div>
);

export const WhatsAppChatDetailsPanel: React.FC<WhatsAppChatDetailsPanelProps> = ({
  open,
  loading,
  details,
  onClose,
}) => {
  // Antes del early return: los hooks no pueden quedar detrás de un return condicional.
  const { labels: creditTypeLabels } = useCreditTypes();

  if (!open) return null;

  return (
    <>
      <div className="fixed inset-0 z-40 bg-gray-900/50" onClick={onClose} />
      <div className="fixed right-0 top-0 z-50 flex h-screen w-full max-w-sm flex-col overflow-hidden border-l border-gray-200 bg-white dark:border-gray-800 dark:bg-gray-dark">
        <div className="flex items-center justify-between border-b border-gray-200 px-5 py-4 dark:border-gray-800">
          <h3 className="text-base font-semibold text-gray-800 dark:text-white/90">Detalles</h3>
          <button
            type="button"
            onClick={onClose}
            className="text-gray-400 hover:text-gray-700 dark:hover:text-gray-300"
            title="Cerrar"
          >
            <X size={20} />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto custom-scrollbar px-5 py-4 space-y-6">
          {loading ? (
            <div className="mt-10">
              <Loader size="sm" />
            </div>
          ) : !details ? (
            <EmptyState icon={UserX} title="No se pudieron cargar los detalles" className="mt-10" />
          ) : (
            <>
              <section>
                <h4 className="mb-2 text-xs font-semibold uppercase tracking-wide text-gray-400 dark:text-gray-500">
                  Deudor
                </h4>
                {details.debtor ? (
                  <div className="space-y-2 rounded-xl border border-gray-200 p-3 dark:border-gray-800">
                    <Field label="Nombre" value={details.debtor.fullName} />
                    <Field
                      label="Documento"
                      value={`${details.debtor.documentType} ${details.debtor.documentNumber}`}
                    />
                    <Field label="Tipo" value={details.debtor.debtorType} />
                    <Field
                      label="Registrado como usuario"
                      value={
                        details.isSelfRegistered ? (
                          <span className="text-success-600 dark:text-success-500">Sí, se autogestiona</span>
                        ) : (
                          <span className="text-gray-500">No</span>
                        )
                      }
                    />
                  </div>
                ) : (
                  <p className="text-sm text-gray-400">Sin deudor asociado a este hilo.</p>
                )}
              </section>

              <section>
                <h4 className="mb-2 text-xs font-semibold uppercase tracking-wide text-gray-400 dark:text-gray-500">
                  Portafolio y campaña
                </h4>
                <div className="space-y-2 rounded-xl border border-gray-200 p-3 dark:border-gray-800">
                  <Field label="Portafolio" value={details.portfolio?.name ?? "No resuelto"} />
                  <Field
                    label="Campaña"
                    value={
                      details.campaign ? `${details.campaign.name} (${details.campaign.status})` : "No resuelta"
                    }
                  />
                </div>
              </section>

              <section>
                <h4 className="mb-2 text-xs font-semibold uppercase tracking-wide text-gray-400 dark:text-gray-500">
                  Créditos asociados
                </h4>
                {details.credits.length === 0 ? (
                  <p className="text-sm text-gray-400">Sin créditos en este portafolio.</p>
                ) : (
                  <div className="space-y-2">
                    {details.credits.map((credit) => (
                      <div key={credit.id} className="rounded-xl border border-gray-200 p-3 dark:border-gray-800">
                        <div className="flex items-center justify-between">
                          <span className="text-sm font-medium text-gray-800 dark:text-white/90">
                            {credit.creditNumber}
                          </span>
                          <span className="text-xs text-gray-400">{creditTypeLabels[credit.creditType] ?? credit.creditType}</span>
                        </div>
                        <div className="mt-2 grid grid-cols-1 gap-2 sm:grid-cols-2">
                          <Field
                            label="Saldo total"
                            value={`${credit.currencyCode} ${credit.totalCreditBalance.toLocaleString()}`}
                          />
                          <Field
                            label="Saldo en mora"
                            value={`${credit.currencyCode} ${credit.overduePrincipalBalance.toLocaleString()}`}
                          />
                          <Field label="Días de mora" value={credit.daysOverdueAtCutoff} />
                          <Field label="Cuotas en mora" value={credit.overdueInstallments} />
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </section>
            </>
          )}
        </div>
      </div>
    </>
  );
};
