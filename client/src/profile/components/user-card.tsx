import { Link } from "react-router";
import { Badge } from "@/ui/components/badge";
import { Card, CardTitle } from "@/ui/components/card";
import { Tooltip } from "@/ui/components/tooltip";
import { resolveProfilePhotoUrl } from "../utils/profile-photo-url";
import { formatShortDate } from "@/profile/utils/format-date";
import { ORG_VERIFICATION_CONFIG } from "@/profile/constants/org-verification-status";
import { IDENTITY_VERIFICATION_CONFIG } from "@/profile/constants/identity-verification-status";
import { CameraIcon } from "./profile-icons";
import { CopyToClipboardButton } from "./copy-to-clipboard-button";
import { InfoRow } from "./info-row";
import { BoolBadge } from "./bool-badge";
import { HierarchyBadge } from "./hierarchy-badge";
import { HierarchyDots } from "./hierarchy-dots";
import { RoleBadge } from "./role-badge";
import type { UserCardProps } from "@/profile/types/user-card-props";

const fmt = formatShortDate;

// ── Main component ─────────────────────────────────────────────────────────────

export const UserCard: React.FC<UserCardProps> = ({ data, isOwnProfile = false, editPath, onForceLogout }) => {
  const {
    fullName, firstname, lastname, email, phoneNumber, authProvider,
    documentType, documentNumber, profilePhotoUrl,
    role, scope, isActive, isEmailVerified, isPhoneVerified,
    mfaEnabled, identityVerificationStatus, isActiveSessions, createdAt, updatedAt,
    roles, orgs,
  } = data;

  const avatarUrl = resolveProfilePhotoUrl(profilePhotoUrl);
  const initials = fullName
    .split(" ")
    .slice(0, 2)
    .map((w) => w[0] ?? "")
    .join("")
    .toUpperCase();

  const orgEntries = orgs ? Object.entries(orgs) : [];

  return (
    <div className="flex flex-col gap-5">
      {/* ── Header ── */}
      <div className="rounded-2xl border border-gray-200 p-5 dark:border-gray-800 lg:p-6">
        <div className="flex flex-col gap-5 xl:flex-row xl:items-center xl:justify-between">
          <div className="flex flex-col items-center gap-6 xl:flex-row">
            {/* Avatar */}
            <div className="relative shrink-0">
              <div className="size-20 overflow-hidden rounded-full border border-gray-200 dark:border-gray-800">
                {avatarUrl ? (
                  <img src={avatarUrl} alt="avatar" className="size-full object-cover" />
                ) : (
                  <div className="flex size-full items-center justify-center bg-brand-500 text-xl font-semibold text-white">
                    {initials}
                  </div>
                )}
              </div>
              {isOwnProfile && (
                <Link
                  to="/profile/photo"
                  title="Cambiar foto"
                  className="absolute bottom-0 right-0 flex size-7 items-center justify-center rounded-full bg-brand-500 text-white shadow-sm hover:bg-brand-600"
                >
                  <CameraIcon size={16} />
                </Link>
              )}
            </div>

            {/* Name + badge + dots */}
            <div className="text-center xl:text-left">
              <div className="mb-1 flex flex-wrap items-center justify-center gap-2 xl:justify-start">
                <h4 className="text-lg font-semibold text-gray-800 dark:text-white/90">{fullName}</h4>
                <HierarchyBadge role={role} scope={scope} />
              </div>
              <HierarchyDots role={role} scope={scope} />
              <div className="mt-2 flex flex-wrap items-center justify-center gap-2 xl:justify-start">
                {isActive !== undefined && (
                  <Badge color={isActive ? "success" : "error"} variant="light" size="sm">
                    {isActive ? "Activo" : "Inactivo"}
                  </Badge>
                )}
                <span className="text-sm text-gray-500 dark:text-gray-400">{email}</span>
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="flex flex-wrap items-center gap-2">
            {isOwnProfile ? (
              <>
                <Tooltip content="Editar perfil">
                  <Link
                    to="/profile/edit"
                    aria-label="Editar perfil"
                    className="inline-flex size-10 items-center justify-center rounded-full border border-gray-300 bg-white text-base shadow-theme-xs hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-800 dark:hover:bg-white/5"
                  >
                    <span aria-hidden="true">✏️</span>
                  </Link>
                </Tooltip>
                <Link
                  to="/profile/change-password"
                  className="inline-flex items-center justify-center gap-2 rounded-full border border-gray-300 bg-white px-4 py-2.5 text-sm font-medium text-gray-700 shadow-theme-xs hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-white/5"
                >
                  Cambiar contraseña
                </Link>
              </>
            ) : (
              <>
                {editPath && (
                  <Tooltip content="Editar usuario">
                    <Link
                      to={editPath}
                      aria-label="Editar usuario"
                      className="inline-flex size-10 items-center justify-center rounded-lg border border-gray-300 bg-white text-base shadow-theme-xs hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-800 dark:hover:bg-white/5"
                    >
                      <span aria-hidden="true">✏️</span>
                    </Link>
                  </Tooltip>
                )}
                {onForceLogout && (
                  <Tooltip content="Cerrar todas las sesiones de este usuario">
                    <button
                      type="button"
                      onClick={onForceLogout}
                      aria-label="Cerrar sesión forzosa"
                      className="inline-flex size-10 items-center justify-center rounded-lg border border-error-300 bg-white text-base shadow-theme-xs hover:bg-error-50 dark:border-error-700 dark:bg-gray-800 dark:hover:bg-error-950"
                    >
                      <span aria-hidden="true">🔒</span>
                    </button>
                  </Tooltip>
                )}
              </>
            )}
          </div>
        </div>
      </div>

      {/* ── Info grid ── */}
      <div className="grid grid-cols-1 gap-5 lg:grid-cols-2">
        <Card>
          <CardTitle>Información personal</CardTitle>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            {firstname && <InfoRow label="Nombre" value={firstname} />}
            {lastname && <InfoRow label="Apellido" value={lastname} />}
            <InfoRow label="Email" value={email} />
            <InfoRow label="Teléfono" value={phoneNumber} />
            <InfoRow label="Tipo documento" value={documentType} />
            <InfoRow label="N° documento" value={documentNumber} />
            {authProvider && <InfoRow label="Proveedor auth" value={authProvider} />}
            <InfoRow label="Registrado" value={fmt(createdAt)} />
          </div>
        </Card>

        <Card>
          <CardTitle>Estado y seguridad</CardTitle>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            {isActive !== undefined && (
              <div>
                <p className="mb-1 text-xs text-gray-500 dark:text-gray-400">Cuenta activa</p>
                <BoolBadge value={isActive} trueLabel="Activa" falseLabel="Inactiva" />
              </div>
            )}
            {isActiveSessions !== undefined && (
              <div>
                <p className="mb-1 text-xs text-gray-500 dark:text-gray-400">Sesión activa</p>
                <BoolBadge value={isActiveSessions} trueLabel="En línea" falseLabel="Desconectado" />
              </div>
            )}
            {isEmailVerified !== undefined && (
              <div>
                <p className="mb-1 text-xs text-gray-500 dark:text-gray-400">Email verificado</p>
                <BoolBadge value={isEmailVerified} />
              </div>
            )}
            {isPhoneVerified !== undefined && (
              <div>
                <p className="mb-1 text-xs text-gray-500 dark:text-gray-400">Teléfono verificado</p>
                <BoolBadge value={isPhoneVerified} />
              </div>
            )}
            {mfaEnabled !== undefined && (
              <div>
                <p className="mb-1 text-xs text-gray-500 dark:text-gray-400">MFA habilitado</p>
                <BoolBadge value={mfaEnabled} />
              </div>
            )}
            {/* Solo aplica a titulares (scope PROPIO): gatea el acceso a su información
                crediticia, ver IdentityVerificationStatus. */}
            {scope === "PROPIO" && identityVerificationStatus && (
              <div>
                <p className="mb-1 text-xs text-gray-500 dark:text-gray-400">Identidad</p>
                {(() => {
                  const v = IDENTITY_VERIFICATION_CONFIG[identityVerificationStatus];
                  return (
                    <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${v.classes}`}>
                      {v.label}
                    </span>
                  );
                })()}
              </div>
            )}
            {updatedAt && <InfoRow label="Última actualización" value={fmt(updatedAt)} />}
          </div>
        </Card>

        {/* ── Roles ── */}
        {roles && roles.length > 0 && (
          <Card className="lg:col-span-2">
            <CardTitle>Roles y acceso</CardTitle>
            <div className="flex flex-col gap-3">
              {roles.map((r, i) => (
                <div key={i} className="flex items-center justify-between rounded-lg border border-gray-100 px-4 py-3 dark:border-gray-800">
                  <div className="flex items-center gap-3">
                    <Badge color="primary" variant="light" size="sm">{r.role}</Badge>
                    <RoleBadge role={r.role} scope={r.scope} />
                  </div>
                  {r.orgName && (
                    <span className="text-sm text-gray-500 dark:text-gray-400">{r.orgName}</span>
                  )}
                </div>
              ))}
            </div>
          </Card>
        )}

        {/* ── Orgs (propio perfil) ── */}
        {orgEntries.length > 0 && (
          <Card className="lg:col-span-2">
            <CardTitle>Mis Empresas</CardTitle>
            <div className="overflow-x-auto custom-scrollbar">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-gray-100 dark:border-gray-800">
                    {["Empresa", "Rol", "Verificación", "ID", "Registrada"].map((h) => (
                      <th key={h} className="pb-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100 dark:divide-gray-800">
                  {orgEntries.map(([orgId, entry]) => {
                    const v = ORG_VERIFICATION_CONFIG[entry.verificationStatus] ?? ORG_VERIFICATION_CONFIG.PENDIENTE;
                    return (
                      <tr key={orgId}>
                        <td className="py-3 font-medium text-gray-800 dark:text-white/90">{entry.orgName}</td>
                        <td className="py-3">
                          <span className="inline-flex items-center rounded-full bg-brand-50 px-2.5 py-0.5 text-xs font-medium text-brand-700 dark:bg-brand-500/10 dark:text-brand-400">
                            {entry.role}
                          </span>
                        </td>
                        <td className="py-3">
                          <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${v.classes}`}>{v.label}</span>
                        </td>
                        <td className="py-3">
                          <span className="inline-flex items-center font-mono text-xs text-gray-400 dark:text-gray-500">
                            {orgId}<CopyToClipboardButton text={orgId} />
                          </span>
                        </td>
                        <td className="py-3 text-xs text-gray-500 whitespace-nowrap dark:text-gray-400">
                          {fmt(entry.createdAt)}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </Card>
        )}
      </div>
    </div>
  );
};
