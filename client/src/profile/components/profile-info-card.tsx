import React, { useState } from "react";
import { Check, Copy } from "lucide-react";
import type { OrgVerificationStatus } from "@/types/auth/user";
import type { ProfileInfoCardProps } from "@/types/props/profile-info-card-props";

const VERIFICATION_CONFIG: Record<OrgVerificationStatus, { label: string; classes: string }> = {
  approved: { label: "Verificada", classes: "bg-success-50 text-success-700 dark:bg-success-500/10 dark:text-success-400" },
  pending:  { label: "Pendiente",  classes: "bg-warning-50 text-warning-700 dark:bg-warning-500/10 dark:text-warning-400" },
  denied:   { label: "Rechazada",  classes: "bg-error-50 text-error-700 dark:bg-error-500/10 dark:text-error-400" },
};

const EditIcon: React.FC = () => (
  <svg className="fill-current" width="18" height="18" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path fillRule="evenodd" clipRule="evenodd" d="M15.0911 2.78206C14.2125 1.90338 12.7878 1.90338 11.9092 2.78206L4.57524 10.116C4.26682 10.4244 4.0547 10.8158 3.96468 11.2426L3.31231 14.3352C3.25997 14.5833 3.33653 14.841 3.51583 15.0203C3.69512 15.1996 3.95286 15.2761 4.20096 15.2238L7.29355 14.5714C7.72031 14.4814 8.11172 14.2693 8.42013 13.9609L15.7541 6.62695C16.6327 5.74827 16.6327 4.32365 15.7541 3.44497L15.0911 2.78206ZM12.9698 3.84272C13.2627 3.54982 13.7376 3.54982 14.0305 3.84272L14.6934 4.50563C14.9863 4.79852 14.9863 5.2734 14.6934 5.56629L14.044 6.21573L12.3204 4.49215L12.9698 3.84272ZM11.2597 5.55281L5.6359 11.1766C5.53309 11.2794 5.46238 11.4099 5.43238 11.5522L5.01758 13.5185L6.98394 13.1037C7.1262 13.0737 7.25666 13.003 7.35947 12.9002L12.9833 7.27639L11.2597 5.55281Z" fill="" />
  </svg>
);

const formatDate = (iso: string | null | undefined): string => {
  if (!iso) return "—";
  return new Date(iso).toLocaleDateString("es-CO", { year: "numeric", month: "long", day: "numeric" });
};

const CopyIdButton: React.FC<{ id: string }> = ({ id }) => {
  const [copied, setCopied] = useState(false);
  const handleCopy = () => {
    navigator.clipboard.writeText(id);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };
  return (
    <button
      onClick={handleCopy}
      title="Copiar ID"
      className="ml-1.5 inline-flex items-center rounded p-0.5 text-gray-400 transition hover:bg-gray-100 hover:text-gray-600 dark:hover:bg-gray-700 dark:hover:text-gray-300"
    >
      {copied ? <Check size={13} /> : <Copy size={13} />}
    </button>
  );
};

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
                  const verification = VERIFICATION_CONFIG[entry.verification_status] ?? VERIFICATION_CONFIG.pending;
                  return (
                    <tr key={orgId}>
                      <td className="py-3 font-medium text-gray-800 dark:text-white/90">{entry.org_name}</td>
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
                          <CopyIdButton id={orgId} />
                        </span>
                      </td>
                      <td className="py-3 text-xs text-gray-500 dark:text-gray-400 whitespace-nowrap">
                        {formatDate(entry.created_at)}
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
