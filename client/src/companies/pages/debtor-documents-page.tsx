import { useMemo } from "react";
import { useSearchParams } from "react-router";
import { Download, FileText, File as FileIcon, FolderOpen, Image as ImageIcon } from "lucide-react";
import EmptyState from "@/ui/components/common/empty-state";
import { PageMeta } from "@/ui/pages/page-meta";
import { ModuleBase } from "@/ui/components/common/module-base";
import { Loader } from "@/ui/components/loader/loader";
import { Badge } from "@/ui/components/badge";
import { API_URL } from "@/hooks/use-api-client";
import { useOrgModule } from "../hooks/use-org-module";
import { useBreadcrumb } from "../hooks/use-breadcrumb";
import { usePortfolios } from "../hooks/use-portfolios";
import { useDebtorDocuments } from "../hooks/use-debtor-documents";
import { useDocumentCategories } from "../hooks/use-document-categories";
import { DOCUMENT_CATEGORY_COLOR } from "@/constants/companies/document-category";
import type { DebtorDocument } from "@/types/companies/portfolio-debtor-types";

const formatBytes = (bytes: number | null) => {
  if (!bytes) return null;
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
};

const fileIconFor = (contentType: string) => {
  if (contentType === "application/pdf") {
    return { Icon: FileText, className: "bg-error-50 text-error-600 dark:bg-error-500/10 dark:text-error-400" };
  }
  if (contentType.startsWith("image/")) {
    return { Icon: ImageIcon, className: "bg-brand-50 text-brand-600 dark:bg-brand-500/10 dark:text-brand-400" };
  }
  return { Icon: FileIcon, className: "bg-gray-100 text-gray-500 dark:bg-white/5 dark:text-gray-400" };
};

const dayLabel = (iso: string) =>
  new Intl.DateTimeFormat("es-CO", { day: "numeric", month: "long", year: "numeric" }).format(new Date(iso));

const timeLabel = (iso: string) =>
  new Intl.DateTimeFormat("es-CO", { hour: "numeric", minute: "2-digit" }).format(new Date(iso));

interface DayGroup {
  key: string;
  label: string;
  items: DebtorDocument[];
}

const groupByDay = (items: DebtorDocument[]): DayGroup[] => {
  const groups = new Map<string, DebtorDocument[]>();
  for (const item of items) {
    const key = item.createdAt.slice(0, 10);
    const bucket = groups.get(key);
    if (bucket) bucket.push(item);
    else groups.set(key, [item]);
  }
  return Array.from(groups.entries()).map(([key, docs]) => ({
    key,
    label: dayLabel(docs[0].createdAt),
    items: docs,
  }));
};

export const DebtorDocumentsPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const debtorId = searchParams.get("clientId");
  const portfolioId = searchParams.get("portfolio") ?? "";
  const { orgId } = useOrgModule();
  const { debtor } = useBreadcrumb();
  const { portfolios } = usePortfolios(orgId);
  const portfolioName = portfolios.find((p) => p.id === portfolioId)?.name ?? "Portafolio";

  const { items, loading, error } = useDebtorDocuments(debtorId, portfolioId);
  const { labels: categoryLabels } = useDocumentCategories();
  const days = useMemo(() => groupByDay(items), [items]);

  return (
    <>
      <PageMeta title="Archivos del cliente" description="Línea de tiempo de documentos del cliente" />
      <ModuleBase
        pageTitle="Archivos"
        pageIcon={FolderOpen}
        breadcrumbItems={debtor({ portfolioId, portfolioName, debtorId, includeDetail: true })}
      >
        {loading ? (
          <div className="py-20">
            <Loader />
          </div>
        ) : error ? (
          <div className="rounded-xl border border-error-200 bg-error-50 p-5 text-sm text-error-600 dark:border-error-500/20 dark:bg-error-500/10 dark:text-error-400">
            {error}
          </div>
        ) : days.length === 0 ? (
          <EmptyState icon={FolderOpen} title="Este cliente no tiene archivos cargados" className="py-20" />
        ) : (
          <ol className="relative space-y-8 border-l border-gray-200 pl-6 dark:border-gray-800">
            {days.map((day) => (
              <li key={day.key} className="relative">
                <span className="absolute top-0.5 -left-[29px] flex h-3.5 w-3.5 rounded-full border-2 border-white bg-brand-500 dark:border-gray-900" />
                <p className="mb-3 text-xs font-semibold tracking-wider text-gray-500 uppercase dark:text-gray-400">
                  {day.label}
                </p>
                <div className="space-y-3">
                  {day.items.map((doc) => {
                    const { Icon, className } = fileIconFor(doc.contentType);
                    const size = formatBytes(doc.sizeBytes);
                    return (
                      <a
                        key={doc.id}
                        href={`${API_URL}/debtors/${debtorId}/documents/${doc.id}/content?portfolioId=${portfolioId}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-3 rounded-xl border border-gray-100 p-4 transition hover:border-brand-200 hover:bg-brand-50/40 dark:border-gray-800 dark:hover:border-brand-500/30 dark:hover:bg-brand-500/5"
                      >
                        <div className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-lg ${className}`}>
                          <Icon size={18} />
                        </div>
                        <div className="min-w-0 flex-1">
                          <p className="truncate text-sm font-medium text-gray-700 dark:text-gray-300">
                            {doc.originalName}
                          </p>
                          <div className="mt-1 flex flex-wrap items-center gap-2">
                            <Badge variant="light" color={DOCUMENT_CATEGORY_COLOR[doc.category] ?? "light"} size="sm">
                              {categoryLabels[doc.category] ?? doc.category}
                            </Badge>
                            <span className="text-xs text-gray-400">{timeLabel(doc.createdAt)}</span>
                            {size && <span className="text-xs text-gray-400">· {size}</span>}
                          </div>
                        </div>
                        <Download size={14} className="shrink-0 text-gray-300 dark:text-gray-600" />
                      </a>
                    );
                  })}
                </div>
              </li>
            ))}
          </ol>
        )}
      </ModuleBase>
    </>
  );
};
