import { Mail, MapPin, Phone, X } from "lucide-react";
import { Loader } from "@/ui/components/loader/loader";
import { Modal } from "@/ui/components/modal/modal";
import { useDebtorProfile } from "../hooks/use-portfolio-debtors";
import type { PortfolioDebtor } from "@/types/companies/portfolio-debtor-types";

interface DebtorDetailsModalProps {
  debtor: PortfolioDebtor | null;
  onClose: () => void;
}

const CONTACT_ICON: Record<string, React.ReactNode> = {
  EMAIL: <Mail size={14} />,
  PHONE: <Phone size={14} />,
  MOBILE: <Phone size={14} />,
};

export const DebtorDetailsModal: React.FC<DebtorDetailsModalProps> = ({ debtor, onClose }) => {
  const { profile, loading } = useDebtorProfile(debtor?.id ?? null);

  return (
    <Modal isOpen={!!debtor} onClose={onClose} className="max-w-2xl mx-4 my-8">
      <div className="p-6 sm:p-8">
        {/* Header */}
        <div className="mb-6 pr-8">
          <h3 className="text-lg font-semibold text-gray-800 dark:text-white/90">
            {debtor?.fullName ?? "Detalle de cliente"}
          </h3>
          <p className="mt-0.5 text-sm text-gray-500 dark:text-gray-400">
            {debtor?.documentType} · {debtor?.documentNumber}
          </p>
        </div>

        {loading ? (
          <div className="py-10">
            <Loader />
          </div>
        ) : !profile ? (
          <p className="py-10 text-center text-sm text-gray-400">No hay datos disponibles.</p>
        ) : (
          <div className="space-y-6 overflow-y-auto max-h-[60vh]">
            {/* Contact methods */}
            {profile.contactMethods.length > 0 && (
              <section>
                <h4 className="mb-3 text-xs font-semibold uppercase tracking-wider text-gray-500 dark:text-gray-400">
                  Contacto
                </h4>
                <div className="flex flex-wrap gap-2">
                  {profile.contactMethods.map((c) => (
                    <span
                      key={c.id}
                      className="inline-flex items-center gap-1.5 rounded-full border border-gray-200 bg-gray-50 px-3 py-1 text-xs text-gray-700 dark:border-gray-700 dark:bg-white/5 dark:text-gray-300"
                    >
                      {CONTACT_ICON[c.contactType] ?? <Phone size={14} />}
                      {c.contactValue}
                    </span>
                  ))}
                </div>
              </section>
            )}

            {/* Addresses */}
            {profile.addresses.length > 0 && (
              <section>
                <h4 className="mb-3 text-xs font-semibold uppercase tracking-wider text-gray-500 dark:text-gray-400">
                  Direcciones
                </h4>
                <div className="space-y-2">
                  {profile.addresses.map((a) => (
                    <div
                      key={a.id}
                      className="flex items-start gap-2 rounded-lg border border-gray-100 p-3 dark:border-gray-800"
                    >
                      <MapPin size={14} className="mt-0.5 shrink-0 text-gray-400" />
                      <div className="text-sm text-gray-700 dark:text-gray-300">
                        <span className="font-medium capitalize">{a.addressType.toLowerCase()} · </span>
                        {a.address}, {a.city}, {a.state}
                      </div>
                    </div>
                  ))}
                </div>
              </section>
            )}

            {/* Credits */}
            {profile.credits.length > 0 && (
              <section>
                <h4 className="mb-3 text-xs font-semibold uppercase tracking-wider text-gray-500 dark:text-gray-400">
                  Créditos ({profile.credits.length})
                </h4>
                <div className="space-y-2">
                  {profile.credits.map((c) => (
                    <div
                      key={c.id}
                      className="flex items-center justify-between rounded-lg border border-gray-100 p-3 dark:border-gray-800"
                    >
                      <div>
                        <p className="text-sm font-medium text-gray-800 dark:text-white/90">
                          #{c.creditNumber}
                        </p>
                        <p className="text-xs text-gray-500 dark:text-gray-400">{c.creditType}</p>
                      </div>
                      <div className="text-right">
                        <p className="text-sm font-semibold text-gray-800 dark:text-white/90">
                          {c.totalCreditBalance.toLocaleString("es-CO", { style: "currency", currency: "COP", maximumFractionDigits: 0 })}
                        </p>
                        {c.daysOverdueAtCutoff > 0 && (
                          <p className="text-xs text-error-500">{c.daysOverdueAtCutoff} días mora</p>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </section>
            )}
          </div>
        )}
      </div>
    </Modal>
  );
};
