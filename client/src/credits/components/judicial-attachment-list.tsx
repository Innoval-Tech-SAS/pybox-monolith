import { Download, FileText, Image as ImageIcon, Paperclip } from "lucide-react";
import EmptyState from "@/ui/components/common/empty-state";
import { API_URL } from "@/hooks/use-api-client";
import type { JudicialNotificationAttachment } from "@/credits/types/judicial-types";

const IMAGE_EXTS = new Set([".jpg", ".jpeg", ".png", ".webp"]);

const fileIconFor = (name: string) => {
  const ext = name.slice(name.lastIndexOf(".")).toLowerCase();
  return IMAGE_EXTS.has(ext) ? ImageIcon : FileText;
};

const formatSize = (bytes: number): string => {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
};

/** Adjuntos de una notificación judicial: soporte documental subido por la entidad. */
export const JudicialAttachmentList: React.FC<{ attachments: JudicialNotificationAttachment[] }> = ({
  attachments,
}) => {
  if (attachments.length === 0) {
    return <EmptyState icon={Paperclip} title="Sin adjuntos" className="py-4" />;
  }

  return (
    <div className="flex flex-col gap-2">
      {attachments.map((attachment) => {
        const Icon = fileIconFor(attachment.name);
        return (
          <a
            key={attachment.id}
            href={`${API_URL}${attachment.url}`}
            target="_blank"
            rel="noopener noreferrer"
            download={attachment.name}
            className="flex items-center gap-3 rounded-lg border border-gray-100 bg-gray-50 px-3 py-2.5 hover:border-brand-200 hover:bg-brand-50 dark:border-gray-800 dark:bg-white/3 dark:hover:border-brand-500/30 dark:hover:bg-brand-500/10"
          >
            <Icon size={16} className="shrink-0 text-gray-500 dark:text-gray-400" />
            <span className="min-w-0 flex-1 truncate text-sm text-gray-700 dark:text-gray-300">
              {attachment.name}
            </span>
            <span className="shrink-0 text-xs text-gray-400">{formatSize(attachment.size)}</span>
            <Download size={13} className="shrink-0 text-gray-400" />
          </a>
        );
      })}
    </div>
  );
};
