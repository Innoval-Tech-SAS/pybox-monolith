import { EditIcon } from "./profile-icons";
import { CopyToClipboardButton } from "./copy-to-clipboard-button";
import { ORG_VERIFICATION_CONFIG } from "@/profile/constants/org-verification-status";
import { formatLongDate } from "@/profile/utils/format-date";
import type { ProfileInfoCardProps } from "@/types/props/profile-info-card-props";

export const ProfileInfoCard: React.FC<ProfileInfoCardProps> = ({
  email,
  documentType,
  documentNumber,
  orgs,
}) => {
  const orgEntries = orgs ? Object.entries(orgs) : [];

  return (
    <div className="space-y-5">
      {/* Información personal */}
      <div className="p-5 border border-gray-200 rounded-2xl dark:border-gray-800 lg:p-6">
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1">
            <h4 className="mb-4 text-lg font-semibold text-gray-800 dark:text-white/90 lg:mb-6">
              Información personal
            </h4>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:gap-6">
              <div>
                <p className="mb-1 text-xs text-gray-500 dark:text-gray-400">Correo electrónico</p>
                <p className="text-sm font-medium text-gray-800 dark:text-white/90">{email}</p>
              </div>
              {documentType && (
                <div>
                  <p className="mb-1 text-xs text-gray-500 dark:text-gray-400">Tipo de documento</p>
                  <p className="text-sm font-medium text-gray-800 dark:text-white/90">{documentType}</p>
                </div>
              )}
              {documentNumber && (
                <div>
                  <p className="mb-1 text-xs text-gray-500 dark:text-gray-400">Número de documento</p>
                  <p className="text-sm font-medium text-gray-800 dark:text-white/90">{documentNumber}</p>
                </div>
              )}
            </div>
          </div>
          <button className="shrink-0 flex items-center gap-2 rounded-full border border-gray-300 bg-white px-4 py-3 text-sm font-medium text-gray-700 shadow-theme-xs hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-400 dark:hover:bg-white/3">
            <EditIcon />
            Editar
          </button>
        </div>
      </div>

      {/* Empresas */}
      {orgEntries.length > 0 && (
        <div className="p-5 border border-gray-200 rounded-2xl dark:border-gray-800 lg:p-6">
          <h4 className="mb-4 text-lg font-semibold text-gray-800 dark:text-white/90 lg:mb-6">
            Mis Empresas
          </h4>
          <div className="overflow-x-auto custom-scrollbar">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-100 dark:border-gray-800">
                  <th className="pb-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400">Empresa</th>
                  <th className="pb-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400">Rol</th>
                  <th className="pb-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400">Verificación</th>
                  <th className="pb-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400">ID</th>
                  <th className="pb-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400">Registrada</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100 dark:divide-gray-800">
                {orgEntries.map(([orgId, entry]) => {
                  const verification = ORG_VERIFICATION_CONFIG[entry.verificationStatus] ?? ORG_VERIFICATION_CONFIG.PENDIENTE;
                  return (
                    <tr key={orgId}>
                      <td className="py-3 font-medium text-gray-800 dark:text-white/90">{entry.orgName}</td>
                      <td className="py-3">
                        <span className="inline-flex items-center rounded-full bg-brand-50 px-2.5 py-0.5 text-xs font-medium text-brand-700 dark:bg-brand-500/10 dark:text-brand-400">
                          {entry.role}
                        </span>
                      </td>
                      <td className="py-3">
                        <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${verification.classes}`}>
                          {verification.label}
                        </span>
                      </td>
                      <td className="py-3">
                        <span className="inline-flex items-center font-mono text-xs text-gray-400 dark:text-gray-500">
                          {orgId}
                          <CopyToClipboardButton text={orgId} title="Copiar ID" />
                        </span>
                      </td>
                      <td className="py-3 text-xs text-gray-500 dark:text-gray-400 whitespace-nowrap">
                        {formatLongDate(entry.createdAt)}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
