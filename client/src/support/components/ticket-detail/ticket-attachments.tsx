import { Image, FileText, Download } from "lucide-react";
import { API_URL } from "@/hooks/use-api-client";
import { useTicketAttachments } from "@/support/hooks/use-ticket-attachments";

const IMAGE_EXTS = new Set([".jpg", ".jpeg", ".png"]);

const formatSize = (bytes: number): string => {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
};

const FileIcon: React.FC<{ name: string }> = ({ name }) => {
  const ext = name.slice(name.lastIndexOf(".")).toLowerCase();
  return IMAGE_EXTS.has(ext) ? (
    <Image size={16} className="text-brand-500" />
  ) : (
    <FileText size={16} className="text-gray-500 dark:text-gray-400" />
  );
};

interface TicketAttachmentsProps {
  ticketNumber: number;
  refreshTrigger?: number;
}

export const TicketAttachments: React.FC<TicketAttachmentsProps> = ({ ticketNumber, refreshTrigger }) => {
  const { attachments, loading } = useTicketAttachments(ticketNumber, refreshTrigger);

  if (loading) {
    return (
      <div className="mt-6">
        <p className="mb-3 text-xs font-semibold uppercase tracking-wide text-gray-400 dark:text-gray-500">
          Adjuntos
        </p>
        <div className="h-10 animate-pulse rounded-lg bg-gray-100 dark:bg-white/5" />
      </div>
    );
  }

  if (!attachments.length) {
    return (
      <div className="mt-6">
        <p className="mb-3 text-xs font-semibold uppercase tracking-wide text-gray-400 dark:text-gray-500">
          Adjuntos
        </p>
        <p className="text-sm text-gray-400 dark:text-gray-500">Sin adjuntos.</p>
      </div>
    );
  }

  return (
    <div className="mt-6">
      <p className="mb-3 text-xs font-semibold uppercase tracking-wide text-gray-400 dark:text-gray-500">
        Adjuntos
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
