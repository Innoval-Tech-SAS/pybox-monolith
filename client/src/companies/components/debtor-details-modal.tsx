import { Modal } from "@/ui/components/modal/modal";
import { Loader } from "@/ui/components/loader/loader";
import { useDebtorRelatedContacts } from "../hooks/use-portfolio-debtors";
import type { DebtorDetailsModalProps } from "@/types/props/debtor-details-modal-props";
import type { DebtorContactMethod, DebtorAddress, DebtorDetail } from "@/types/companies/portfolio-debtor-types";

const ContactMethodGrid: React.FC<{ methods: DebtorContactMethod[] }> = ({ methods }) =>
  methods.length > 0 ? (
    <div className="grid gap-2 sm:grid-cols-2">
      {methods.map((c) => (
        <div key={c.id} className="rounded-lg bg-gray-50 p-3 dark:bg-white/5">
          <p className="mb-1 text-xs font-semibold uppercase tracking-wider text-gray-400 dark:text-gray-500">
            {c.contactType}
          </p>
          <p className="text-sm font-medium text-gray-700 dark:text-gray-300">{c.contactValue}</p>
        </div>
      ))}
    </div>
  ) : (
    <p className="text-sm text-gray-400">Sin métodos de contacto registrados.</p>
  );

const AddressGrid: React.FC<{ addresses: DebtorAddress[] }> = ({ addresses }) =>
  addresses.length > 0 ? (
    <div className="grid gap-2 sm:grid-cols-2">
      {addresses.map((a) => (
        <div key={a.id} className="rounded-lg bg-gray-50 p-3 dark:bg-white/5">
          <p className="text-sm font-medium text-gray-700 dark:text-gray-300">{a.address}</p>
          <p className="mt-1 text-xs text-gray-400">
            {a.city}, {a.state}
          </p>
        </div>
      ))}
    </div>
  ) : (
    <p className="text-sm text-gray-400">Sin direcciones registradas.</p>
  );

const SectionTitle: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <h4 className="mb-3 text-sm font-semibold text-gray-800 dark:text-white/90">{children}</h4>
);

const Divider = () => <hr className="border-gray-100 dark:border-gray-800" />;

const CodebtorCard: React.FC<{ codebtor: DebtorDetail }> = ({ codebtor }) => (
  <div className="rounded-xl border border-gray-200 bg-white p-4 dark:border-gray-800 dark:bg-white/3">
    <div className="mb-3 flex items-center justify-between gap-3">
      <div>
        <p className="text-sm font-medium text-gray-800 dark:text-white/90">{codebtor.fullName}</p>
        <p className="text-xs text-gray-400">
          {codebtor.documentType} · {codebtor.documentNumber}
        </p>
      </div>
      <span className="shrink-0 rounded-full bg-gray-100 px-2.5 py-0.5 text-xs text-gray-500 dark:bg-white/5 dark:text-gray-400">
        {codebtor.contactMethods.length} contacto{codebtor.contactMethods.length !== 1 ? "s" : ""}
      </span>
    </div>
    <ContactMethodGrid methods={codebtor.contactMethods} />
  </div>
);

export const DebtorDetailsModal: React.FC<DebtorDetailsModalProps> = ({
  debtor,
  portfolioId,
  onClose,
}) => {
  const { data, loading } = useDebtorRelatedContacts(debtor?.id ?? null, portfolioId);

  return (
    <Modal isOpen={!!debtor} onClose={onClose} className="max-w-3xl mx-4 my-8">
      <div className="flex flex-col max-h-[85vh]">
        {/* Header */}
        <div className="flex items-center gap-3 border-b border-gray-100 p-6 dark:border-gray-800">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-brand-50 dark:bg-brand-500/10">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="text-brand-600 dark:text-brand-400">
              <circle cx="11" cy="11" r="8" /><path d="m21 21-4.35-4.35" />
            </svg>
          </div>
          <div>
            <h3 className="text-base font-semibold text-gray-800 dark:text-white/90">
              {debtor?.fullName ?? "Detalle de cliente"}
            </h3>
            <p className="text-xs text-gray-500 dark:text-gray-400">
              {debtor?.debtorType} · {debtor?.documentType} {debtor?.documentNumber}
            </p>
          </div>
        </div>

        {/* Body */}
        <div className="overflow-y-auto flex-1 p-6 space-y-5">
          {loading ? (
            <div className="flex flex-col items-center gap-3 py-10">
              <Loader />
              <span className="text-sm text-gray-400">Cargando detalles del cliente...</span>
            </div>
          ) : !data ? (
            <div className="rounded-xl border border-error-200 bg-error-50 p-4 text-sm text-error-600 dark:border-error-500/20 dark:bg-error-500/10 dark:text-error-400">
              No se pudieron cargar los datos del cliente.
            </div>
          ) : (
            <>
              <section>
                <SectionTitle>Métodos de contacto</SectionTitle>
                <ContactMethodGrid methods={data.debtor.contactMethods} />
              </section>

              <Divider />

              <section>
                <SectionTitle>Direcciones</SectionTitle>
                <AddressGrid addresses={data.debtor.addresses} />
              </section>

              {data.codebtors.length > 0 && (
                <>
                  <Divider />
                  <section>
                    <SectionTitle>
                      Codeudores relacionados ({data.codebtors.length})
                    </SectionTitle>
                    <div className="space-y-3">
                      {data.codebtors.map((co) => (
                        <CodebtorCard key={co.id} codebtor={co} />
                      ))}
                    </div>
                  </section>
                </>
              )}
            </>
          )}
        </div>

        {/* Footer */}
        <div className="border-t border-gray-100 p-4 dark:border-gray-800">
          <button
            type="button"
            onClick={onClose}
            className="w-full rounded-xl border border-gray-200 bg-white py-2.5 text-sm font-medium text-gray-600 transition hover:bg-gray-50 dark:border-gray-700 dark:bg-white/5 dark:text-gray-400 dark:hover:bg-white/8"
          >
            Cerrar
          </button>
        </div>
      </div>
    </Modal>
  );
};
