import { Link, useNavigate } from "react-router";
import { Card, CardTitle } from "@/ui/components/card";
import { timeAgo } from "@/ui/utils/time-utils";
import type { AppNotification, NotifType } from "@/types/notifications/notification";
import type { NotificationDetailViewProps } from "@/notifications/types/notification-detail-view-props";
import { NotifIcon } from "./notif-icon";

const TYPE_BADGES: Record<NotifType, { label: string; className: string }> = {
  success: { label: "Completado", className: "bg-green-100 text-green-700 dark:bg-green-500/20 dark:text-green-400" },
  info: { label: "Información", className: "bg-blue-100 text-blue-700 dark:bg-blue-500/20 dark:text-blue-400" },
  warning: { label: "Advertencia", className: "bg-amber-100 text-amber-700 dark:bg-amber-500/20 dark:text-amber-400" },
  error: { label: "Error", className: "bg-red-100 text-red-700 dark:bg-red-500/20 dark:text-red-400" },
};

const DETAIL_LABELS: Record<string, string> = {
  creditos: "Créditos",
  titulares: "Titulares",
  codeudores: "Codeudores",
  clientes_unicos: "Clientes únicos",
};

const toTitleCase = (key: string): string =>
  key.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());

const formatValue = (v: unknown): string => {
  if (typeof v === "number") return v.toLocaleString("es-CO");
  if (typeof v === "boolean") return v ? "Sí" : "No";
  return String(v ?? "—");
};

export const NotificationDetailView: React.FC<NotificationDetailViewProps> = ({ notification: n }) => {
  const navigate = useNavigate();
  const badge = TYPE_BADGES[n.notifType] ?? TYPE_BADGES.info;

  const detailEntries = n.details ? Object.entries(n.details) : [];

  return (
    <div className="flex flex-col gap-5">
      {/* Header card */}
      <Card>
        <div className="flex items-start gap-4">
          <NotifIcon type={n.notifType} size="lg" />
          <div className="min-w-0 flex-1">
            <h2 className="text-xl font-semibold text-gray-800 dark:text-white/90">
              {n.title}
            </h2>
            <div className="mt-1.5 flex flex-wrap items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
              <span>{n.category}</span>
              <span className="h-1 w-1 rounded-full bg-gray-300 dark:bg-gray-600" />
              <span>{timeAgo(n.createdAt)}</span>
              <span
                className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${badge.className}`}
              >
                {badge.label}
              </span>
            </div>
          </div>
        </div>

        {/* Body */}
        <div className="mt-5">
          <p className="mb-2 text-xs font-semibold uppercase tracking-wider text-gray-400 dark:text-gray-500">
            Mensaje del servidor
          </p>
          <div className="rounded-lg bg-gray-50 px-4 py-3 dark:bg-white/3">
            <p className="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-line">
              {n.body}
            </p>
          </div>
        </div>
      </Card>

      {/* Details card */}
      {detailEntries.length > 0 && (
        <Card>
          <CardTitle>Detalles del proceso</CardTitle>
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
            {detailEntries.map(([key, value]) => (
              <div
                key={key}
                className="rounded-lg border border-gray-100 bg-gray-50 px-4 py-3 dark:border-gray-800 dark:bg-white/3"
              >
                <p className="text-xs text-gray-400 dark:text-gray-500 mb-1">
                  {DETAIL_LABELS[key] ?? toTitleCase(key)}
                </p>
                <p className="text-base font-semibold text-gray-800 dark:text-white/90">
                  {formatValue(value)}
                </p>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Actions */}
      <div className="flex items-center gap-3">
        {n.link ? (
          <Link
            to={n.link}
            className="inline-flex items-center gap-2 rounded-lg bg-gray-900 px-4 py-2 text-sm font-medium text-white hover:bg-gray-800 dark:bg-white dark:text-gray-900 dark:hover:bg-gray-100"
          >
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
              <polyline points="15 3 21 3 21 9" />
              <line x1="10" y1="14" x2="21" y2="3" />
            </svg>
            Ver
          </Link>
        ) : (
          <button
            onClick={() => navigate(-1)}
            className="inline-flex items-center gap-2 rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-white/5"
          >
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="19" y1="12" x2="5" y2="12" />
              <polyline points="12 19 5 12 12 5" />
            </svg>
            Volver
          </button>
        )}
      </div>
    </div>
  );
};
