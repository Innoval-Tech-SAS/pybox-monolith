import { Card, CardTitle } from "@/ui/components/card";
import { ArrowUpCircle } from "lucide-react";
import { resolveProfilePhotoUrl } from "@/profile/utils/profile-photo-url";
import { useTicketCreator } from "@/support/hooks/use-ticket-creator";
import { useTicketAssignee } from "@/support/hooks/use-ticket-assignee";
import { useEscalateTicket } from "@/support/hooks/use-escalate-ticket";
import { TicketOrgDocsViewer } from "./ticket-org-docs-viewer";
import {
  formatTicketDetailDate,
  getStatusBadgeStyles,
  getTicketDisplayId,
  TICKET_CASE_TYPE_LABELS,
  TICKET_STATUS_LABELS,
  TICKET_TYPE_LABELS,
} from "@/support/utils/ticket-kanban-utils";
import { getSession } from "@/auth/utils/auth-session-utils";
import { Role, Scope } from "@/types/auth/role";
import type { TicketDetailViewProps } from "@/types/props/ticket-detail-view-props";

const UserAvatar: React.FC<{ name: string; photoUrl?: string | null; size?: "sm" | "md" }> = ({
  name,
  photoUrl,
  size = "md",
}) => {
  const url = resolveProfilePhotoUrl(photoUrl);
  const initials = name
    .split(" ")
    .slice(0, 2)
    .map((w) => w[0] ?? "")
    .join("")
    .toUpperCase();
  const dim = size === "sm" ? "size-7 text-xs" : "size-9 text-sm";

  return (
    <div className={`shrink-0 overflow-hidden rounded-full border border-gray-200 dark:border-gray-700 ${dim}`}>
      {url ? (
        <img src={url} alt={name} className="size-full object-cover" />
      ) : (
        <div className={`flex size-full items-center justify-center bg-brand-500 font-semibold text-white ${dim}`}>
          {initials}
        </div>
      )}
    </div>
  );
};

const DetailRow: React.FC<{ label: string; children: React.ReactNode }> = ({ label, children }) => (
  <div className="rounded-lg border border-gray-100 bg-gray-50 px-4 py-3 dark:border-gray-800 dark:bg-white/3">
    <p className="text-xs text-gray-400 dark:text-gray-500">{label}</p>
    <div className="mt-1 text-sm font-medium text-gray-800 dark:text-white/90">{children}</div>
  </div>
);

const _session = getSession();
const _orgRoles = Object.values(_session?.orgs ?? {}).map((o) => o.role);
const canEscalate =
  _session?.scope === Scope.GLOBAL ||
  (_session?.scope === Scope.ORG && _orgRoles.includes(Role.CS));

export const TicketDetailView: React.FC<TicketDetailViewProps> = ({ ticket, onTicketResolved, onTicketEscalated }) => {
  const { creator } = useTicketCreator(ticket.createdBy);
  const { assignee } = useTicketAssignee(ticket.assignedTo ?? undefined);
  const { escalateTicket, loading: escalating } = useEscalateTicket();
  const isOrgVerification = ticket.caseType === "requirement";
  const displayId = getTicketDisplayId(ticket.ticketNumber, ticket.caseType);
  const isResolved = ticket.status === "resolved";

  const handleEscalate = async () => {
    const updated = await escalateTicket(ticket.ticketNumber);
    if (updated) onTicketEscalated?.(updated);
  };

  return (
    <div className="grid gap-5 xl:grid-cols-[minmax(0,1fr)_320px]">
      {/* ── Main panel ── */}
      <Card>
        {/* Header */}
        <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <div className="mb-2 flex items-center gap-2">
              <span className="inline-flex items-center rounded-md bg-brand-50 px-2.5 py-1 text-xs font-bold tracking-widest text-brand-600 dark:bg-brand-500/10 dark:text-brand-400">
                {displayId}
              </span>
              <span className="text-xs font-medium text-gray-400 dark:text-gray-500">
                {TICKET_TYPE_LABELS[ticket.caseType]}
              </span>
            </div>
            <h2 className="text-title-sm font-semibold text-gray-800 dark:text-white/90">
              {ticket.title ?? TICKET_CASE_TYPE_LABELS[ticket.caseType]}
            </h2>
          </div>
          <span
            className={`inline-flex w-fit shrink-0 rounded-full px-2.5 py-1 text-theme-xs font-medium ${getStatusBadgeStyles(ticket.status)}`}
          >
            {TICKET_STATUS_LABELS[ticket.status]}
          </span>
        </div>

        {/* Notes */}
        <div className="mt-6 rounded-xl border border-gray-100 bg-gray-50 p-4 dark:border-gray-800 dark:bg-white/3">
          <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-gray-400 dark:text-gray-500">
            Notas
          </p>
          <p className="whitespace-pre-line text-sm text-gray-700 dark:text-gray-300">
            {ticket.notes ?? "Este ticket todavía no tiene notas registradas."}
          </p>
        </div>

        {/* Org verification documents + resolve actions */}
        {isOrgVerification && (
          <TicketOrgDocsViewer
            ticket={ticket}
            onResolved={onTicketResolved ?? (() => {})}
          />
        )}
      </Card>

      {/* ── Sidebar ── */}
      <Card>
        <CardTitle>Detalle del ticket</CardTitle>
        <div className="mt-5 flex flex-col gap-3">
          {/* Creator */}
          <DetailRow label="Creado por">
            {creator ? (
              <div className="flex items-center gap-2.5">
                <UserAvatar name={creator.fullName} photoUrl={creator.profilePhotoUrl} size="sm" />
                <span>{creator.fullName}</span>
              </div>
            ) : (
              <span className="text-gray-500">Usuario #{ticket.createdBy}</span>
            )}
          </DetailRow>

          {/* Assigned to */}
          <DetailRow label="Asignado a">
            {ticket.assignedTo ? (
              assignee ? (
                <div className="flex items-center gap-2.5">
                  <UserAvatar name={assignee.fullName} photoUrl={assignee.profilePhotoUrl} size="sm" />
                  <span>{assignee.fullName}</span>
                </div>
              ) : (
                <span className="text-gray-500">Usuario #{ticket.assignedTo}</span>
              )
            ) : (
              <span className="text-gray-400 dark:text-gray-500">Sin asignar</span>
            )}
          </DetailRow>

          {/* Entity */}
          <DetailRow label="Entidad">
            <span>{ticket.organizationName || ticket.organizationId}</span>
          </DetailRow>

          {/* Dates */}
          <DetailRow label="Creado">
            {formatTicketDetailDate(ticket.createdAt)}
          </DetailRow>

          <DetailRow label="Resuelto">
            <span className={ticket.resolvedAt ? "" : "text-gray-400 dark:text-gray-500"}>
              {formatTicketDetailDate(ticket.resolvedAt)}
            </span>
          </DetailRow>

          {/* Type badge */}
          <div className="rounded-lg border border-gray-100 bg-gray-50 px-4 py-3 dark:border-gray-800 dark:bg-white/3">
            <p className="mb-1.5 text-xs text-gray-400 dark:text-gray-500">Tipo</p>
            <span
              className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold ${
                isOrgVerification
                  ? "bg-brand-50 text-brand-700 dark:bg-brand-500/10 dark:text-brand-400"
                  : "bg-error-50 text-error-700 dark:bg-error-500/10 dark:text-error-400"
              }`}
            >
              {displayId.split("-")[0]} · {TICKET_TYPE_LABELS[ticket.caseType]}
            </span>
          </div>

          {canEscalate && !isResolved && (
            <button
              onClick={handleEscalate}
              disabled={escalating}
              className="mt-1 inline-flex w-full items-center justify-center gap-2 rounded-lg border border-warning-200 bg-warning-50 px-4 py-2.5 text-sm font-medium text-warning-700 hover:bg-warning-100 disabled:opacity-60 dark:border-warning-500/30 dark:bg-warning-500/10 dark:text-warning-400 dark:hover:bg-warning-500/20"
            >
              <ArrowUpCircle size={15} />
              {escalating ? "Escalando..." : "Escalar a CS Global"}
            </button>
          )}
        </div>
      </Card>
    </div>
  );
};
