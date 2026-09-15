import { Download, Paperclip } from "lucide-react";
import EmptyState from "@/ui/components/common/empty-state";
import { API_URL } from "@/hooks/use-api-client";
import { useClosureAttachments } from "@/support/hooks/use-closure-attachments";
import type { TicketClosureAttachmentsProps } from "@/support/types/ticket-closure-attachments-props";
import { formatAttachmentSize as formatSize } from "@/support/utils/format-attachment-size";
import { FileIcon } from "./file-icon";

export const TicketClosureAttachments: React.FC<TicketClosureAttachmentsProps> = ({
  ticketNumber,
  refreshTrigger,
}) => {
  const { attachments, loading } = useClosureAttachments(ticketNumber, refreshTrigger);

  if (loading) {
    return (
      <div className="mt-4">
        <p className="mb-3 text-xs font-semibold uppercase tracking-wide text-gray-400 dark:text-gray-500">
          Evidencias de cierre
        </p>
        <div className="h-10 animate-pulse rounded-lg bg-gray-100 dark:bg-white/5" />
      </div>
    );
  }

  if (!attachments.length) {
    return (
      <div className="mt-4">
        <p className="mb-3 text-xs font-semibold uppercase tracking-wide text-gray-400 dark:text-gray-500">
          Evidencias de cierre
        </p>
        <EmptyState icon={Paperclip} title="Sin evidencias de cierre" />
      </div>
    );
  }

  return (
    <div className="mt-4">
      <p className="mb-3 text-xs font-semibold uppercase tracking-wide text-gray-400 dark:text-gray-500">
        Evidencias de cierre
        <span className="ml-2 normal-case font-normal text-gray-500">({attachments.length})</span>
      </p>
      <div className="flex flex-col gap-2">
        {attachments.map((a) => (
          <a
            key={a.name}
            href={`${API_URL}${a.url}`}
            target="_blank"
            rel="noopener noreferrer"
            download={a.name}
            className="flex items-center gap-3 rounded-lg border border-gray-100 bg-gray-50 px-3 py-2.5 hover:border-brand-200 hover:bg-brand-50 dark:border-gray-800 dark:bg-white/3 dark:hover:border-brand-500/30 dark:hover:bg-brand-500/10"
          >
            <FileIcon name={a.name} />
            <span className="min-w-0 flex-1 truncate text-sm text-gray-700 dark:text-gray-300">
              {a.name}
            </span>
            <span className="shrink-0 text-xs text-gray-400">{formatSize(a.size)}</span>
            <Download size={13} className="shrink-0 text-gray-400" />
          </a>
        ))}
      </div>
    </div>
  );
};
