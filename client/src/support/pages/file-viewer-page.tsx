import { useSearchParams } from "react-router";
import { ModuleBase } from "@/ui/components/common/module-base";

export const FileViewerPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const url = searchParams.get("url") ?? "";
  const label = searchParams.get("label") ?? "Documento";
  const ticketId = searchParams.get("ticket");

  const breadcrumbItems = ticketId
    ? [{ label: `Ticket #${ticketId}`, path: `/cs/tickets/${ticketId}` }]
    : [];

  return (
    <ModuleBase pageTitle={label} breadcrumbItems={breadcrumbItems}>
      {url ? (
        <div
          className="overflow-hidden rounded-xl border border-gray-200 dark:border-gray-700"
          style={{ height: "calc(100vh - 180px)" }}
        >
          <iframe src={url} title={label} className="h-full w-full" />
        </div>
      ) : (
        <p className="text-sm text-gray-500 dark:text-gray-400">
          URL no especificada.
        </p>
      )}
    </ModuleBase>
  );
};
