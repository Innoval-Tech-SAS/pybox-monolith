import React, { useState } from "react";
import { Link } from "react-router";
import { Check, Copy } from "lucide-react";
import { Badge } from "@/ui/components/badge";
import { Card, CardTitle } from "@/ui/components/card";
import { getRoleHierarchy } from "@/constants/profile/role-hierarchy";
import { resolveProfilePhotoUrl } from "../utils/profile-photo-url";
import type { OrgVerificationStatus } from "@/types/auth/user";
import type { UserCardData, UserCardProps } from "@/profile/types/user-card-props";

// ── Helpers ───────────────────────────────────────────────────────────────────

const fmt = (iso: string | null | undefined) =>
  iso
    ? new Date(iso).toLocaleDateString("es-CO", { day: "2-digit", month: "short", year: "numeric" })
    : "—";

const InfoRow = ({ label, value }: { label: string; value?: React.ReactNode }) => (
  <div>
    <p className="mb-1 text-xs text-gray-500 dark:text-gray-400">{label}</p>
    <p className="text-sm font-medium text-gray-800 dark:text-white/90">{value || "—"}</p>
  </div>
);

const BoolBadge = ({
  value,
  trueLabel = "Sí",
  falseLabel = "No",
}: {
  value?: boolean;
  trueLabel?: string;
  falseLabel?: string;
}) => (
  <Badge size="sm" color={value ? "success" : "light"} variant="light">
    {value ? trueLabel : falseLabel}
  </Badge>
);

const VERIFICATION_CONFIG: Record<OrgVerificationStatus, { label: string; classes: string }> = {
  approved: { label: "Verificada", classes: "bg-success-50 text-success-700 dark:bg-success-500/10 dark:text-success-400" },
  pending:  { label: "Pendiente",  classes: "bg-warning-50 text-warning-700 dark:bg-warning-500/10 dark:text-warning-400" },
  denied:   { label: "Rechazada",  classes: "bg-error-50 text-error-700 dark:bg-error-500/10 dark:text-error-400" },
};

const CopyButton: React.FC<{ text: string }> = ({ text }) => {
  const [copied, setCopied] = useState(false);
  return (
    <button
      onClick={() => { navigator.clipboard.writeText(text); setCopied(true); setTimeout(() => setCopied(false), 2000); }}
      className="ml-1.5 inline-flex items-center rounded p-0.5 text-gray-400 hover:bg-gray-100 hover:text-gray-600 dark:hover:bg-gray-700 dark:hover:text-gray-300"
    >
      {copied ? <Check size={13} /> : <Copy size={13} />}
    </button>
  );
};

const EditIcon = () => (
  <svg className="fill-current" width="16" height="16" viewBox="0 0 18 18" fill="none">
    <path fillRule="evenodd" clipRule="evenodd" d="M15.0911 2.78206C14.2125 1.90338 12.7878 1.90338 11.9092 2.78206L4.57524 10.116C4.26682 10.4244 4.0547 10.8158 3.96468 11.2426L3.31231 14.3352C3.25997 14.5833 3.33653 14.841 3.51583 15.0203C3.69512 15.1996 3.95286 15.2761 4.20096 15.2238L7.29355 14.5714C7.72031 14.4814 8.11172 14.2693 8.42013 13.9609L15.7541 6.62695C16.6327 5.74827 16.6327 4.32365 15.7541 3.44497L15.0911 2.78206ZM12.9698 3.84272C13.2627 3.54982 13.7376 3.54982 14.0305 3.84272L14.6934 4.50563C14.9863 4.79852 14.9863 5.2734 14.6934 5.56629L14.044 6.21573L12.3204 4.49215L12.9698 3.84272ZM11.2597 5.55281L5.6359 11.1766C5.53309 11.2794 5.46238 11.4099 5.43238 11.5522L5.01758 13.5185L6.98394 13.1037C7.1262 13.0737 7.25666 13.003 7.35947 12.9002L12.9833 7.27639L11.2597 5.55281Z" fill="" />
  </svg>
);

const CameraIcon = () => (
  <svg className="fill-current" width="16" height="16" viewBox="0 0 20 20" fill="none">
    <path fillRule="evenodd" clipRule="evenodd" d="M7.75 2.5C7.41848 2.5 7.10054 2.6317 6.86612 2.86612L5.73223 4H3.5C2.67157 4 2 4.67157 2 5.5V15.5C2 16.3284 2.67157 17 3.5 17H16.5C17.3284 17 18 16.3284 18 15.5V5.5C18 4.67157 17.3284 4 16.5 4H14.2678L13.1339 2.86612C12.8995 2.6317 12.5815 2.5 12.25 2.5H7.75ZM10 7.5C8.61929 7.5 7.5 8.61929 7.5 10C7.5 11.3807 8.61929 12.5 10 12.5C11.3807 12.5 12.5 11.3807 12.5 10C12.5 8.61929 11.3807 7.5 10 7.5ZM6 10C6 7.79086 7.79086 6 10 6C12.2091 6 14 7.79086 14 10C14 12.2091 12.2091 14 10 14C7.79086 14 6 12.2091 6 10Z" fill="" />
  </svg>
);

// ── HierarchyBadge ─────────────────────────────────────────────────────────────

const HierarchyBadge: React.FC<{ role?: string; scope?: string }> = ({ role, scope }) => {
  const h = getRoleHierarchy(role, scope);
  if (!h) return null;
  return (
    <span
      title={`Nivel ${h.tier} de 6`}
      className={`inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-semibold ${h.containerClass}`}
    >
      <span className={h.iconClass}>{h.icon}</span>
      <span className={h.textClass}>{h.label}</span>
    </span>
  );
};

const HierarchyDots: React.FC<{ role?: string; scope?: string }> = ({ role, scope }) => {
  const h = getRoleHierarchy(role, scope);
  if (!h) return null;
  return (
    <div className="flex items-center gap-1.5">
      {Array.from({ length: 6 }, (_, i) => (
        <span
          key={i}
          className={`h-1.5 w-4 rounded-full transition-colors ${
            i < 7 - h.tier ? h.dotClass : "bg-gray-200 dark:bg-gray-700"
          }`}
        />
      ))}
    </div>
  );
};

// ── RoleBadge (styled for roles table) ────────────────────────────────────────

const RoleBadge: React.FC<{ role: string; scope: string }> = ({ role, scope }) => {
  const h = getRoleHierarchy(role, scope);
  if (!h) {
    return <Badge color="light" variant="light" size="sm">{scope}</Badge>;
  }
  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-semibold ${h.containerClass}`}
    >
      <span className={h.iconClass}>{h.icon}</span>
      <span className={h.textClass}>{h.label}</span>
    </span>
  );
};

// ── Main component ─────────────────────────────────────────────────────────────

export const UserCard: React.FC<UserCardProps> = ({ data, isOwnProfile = false, editPath, onForceLogout }) => {
  const {
    fullName, firstname, lastname, email, phoneNumber, authProvider,
    documentType, documentNumber, profilePhotoUrl,
    role, scope, isActive, isEmailVerified, isPhoneVerified,
    mfaEnabled, isActiveSessions, createdAt, updatedAt,
    roles, orgs, userId,
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
                  <CameraIcon />
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
                <Link
                  to="/profile/edit"
                  className="inline-flex items-center justify-center gap-2 rounded-full border border-gray-300 bg-white px-4 py-2.5 text-sm font-medium text-gray-700 shadow-theme-xs hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-white/5"
                >
                  <EditIcon />
                  Editar
                </Link>
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
                  <Link
                    to={editPath}
                    className="inline-flex items-center justify-center gap-2 rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-theme-xs hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-white/5"
                  >
                    <EditIcon />
                    Editar
                  </Link>
                )}
                {onForceLogout && (
                  <button
                    type="button"
                    onClick={onForceLogout}
                    className="inline-flex items-center justify-center rounded-lg border border-error-300 bg-white px-4 py-2 text-sm font-medium text-error-600 shadow-theme-xs hover:bg-error-50 dark:border-error-700 dark:bg-gray-800 dark:text-error-400 dark:hover:bg-error-950"
                  >
                    Cerrar sesión forzosa
                  </button>
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
                    const v = VERIFICATION_CONFIG[entry.verificationStatus] ?? VERIFICATION_CONFIG.pending;
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
                            {orgId}<CopyButton text={orgId} />
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
