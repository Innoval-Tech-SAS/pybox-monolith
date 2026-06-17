import { useEffect, useState } from "react";
import { useSearchParams } from "react-router";
import { ExternalLink, FileX, RefreshCw } from "lucide-react";
import { ModuleBase } from "@/ui/components/common/module-base";

type FileStatus = "checking" | "available" | "unavailable";

const VIEWER_HEIGHT = "calc(100vh - 180px)";

const isJsonResponse = (response: Response): boolean =>
  response.headers.get("content-type")?.includes("application/json") ?? false;

const checkFileAvailability = async (url: string): Promise<boolean> => {
  try {
    const headResponse = await fetch(url, {
      method: "HEAD",
      cache: "no-store",
    });

    if (headResponse.status === 405 || headResponse.status === 501) {
      const controller = new AbortController();
      const getResponse = await fetch(url, {
        cache: "no-store",
        headers: { Range: "bytes=0-0" },
        signal: controller.signal,
      });
      controller.abort();

      return getResponse.ok && !isJsonResponse(getResponse);
    }

    return headResponse.ok && !isJsonResponse(headResponse);
  } catch {
    return true;
  }
};

export const FileViewerPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const url = searchParams.get("url") ?? "";
  const label = searchParams.get("label") ?? "Documento";
  const ticketId = searchParams.get("ticket");
  const [fileStatus, setFileStatus] = useState<FileStatus>(
    url ? "checking" : "unavailable",
  );

  const breadcrumbItems = ticketId
    ? [{ label: `Ticket #${ticketId}`, path: `/cs/tickets/${ticketId}` }]
    : [];

  useEffect(() => {
    let cancelled = false;

    if (!url) {
      setFileStatus("unavailable");
      return;
    }

    setFileStatus("checking");
    checkFileAvailability(url).then((available) => {
      if (!cancelled) {
        setFileStatus(available ? "available" : "unavailable");
      }
    });

    return () => {
      cancelled = true;
    };
  }, [url]);

  const retry = () => {
    if (!url) return;
    setFileStatus("checking");
    checkFileAvailability(url).then((available) => {
      setFileStatus(available ? "available" : "unavailable");
    });
  };

  return (
    <ModuleBase pageTitle={label} breadcrumbItems={breadcrumbItems}>
      {fileStatus === "checking" ? (
        <div
          className="flex items-center justify-center rounded-xl border border-gray-200 bg-gray-50 dark:border-gray-700 dark:bg-white/3"
          style={{ height: VIEWER_HEIGHT }}
        >
          <div className="flex flex-col items-center gap-3 text-center">
            <RefreshCw size={28} className="animate-spin text-brand-500" />
            <div>
              <p className="text-sm font-medium text-gray-700 dark:text-gray-200">
                Preparando vista del documento
              </p>
              <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                Estamos verificando que el archivo esté disponible.
              </p>
            </div>
          </div>
        </div>
      ) : fileStatus === "available" ? (
        <div
          className="overflow-hidden rounded-xl border border-gray-200 dark:border-gray-700"
          style={{ height: VIEWER_HEIGHT }}
        >
          <iframe src={url} title={label} className="h-full w-full" />
        </div>
      ) : (
        <div
          className="flex items-center justify-center rounded-xl border border-dashed border-gray-200 bg-gray-50 px-6 text-center dark:border-gray-700 dark:bg-white/3"
          style={{ height: VIEWER_HEIGHT }}
        >
          <div className="w-full max-w-md">
            <div className="mx-auto flex size-16 items-center justify-center rounded-full bg-error-50 text-error-500 dark:bg-error-500/10 dark:text-error-400">
              <FileX size={30} strokeWidth={1.7} />
            </div>
            <h2 className="mt-5 text-base font-semibold text-gray-800 dark:text-white/90">
              Documento no disponible
            </h2>
            <p className="mt-2 text-sm leading-6 text-gray-500 dark:text-gray-400">
              No pudimos mostrar {label.toLowerCase()}. Es posible que el archivo haya
              sido movido, eliminado o que el enlace ya no sea válido.
            </p>

            <div className="mt-6 flex flex-wrap items-center justify-center gap-3">
              {url && (
                <>
                  <button
                    type="button"
                    onClick={retry}
                    className="inline-flex items-center gap-2 rounded-lg bg-brand-500 px-4 py-2.5 text-sm font-medium text-white hover:bg-brand-600"
                  >
                    <RefreshCw size={15} />
                    Reintentar
                  </button>
                  <a
                    href={url}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex items-center gap-2 rounded-lg border border-gray-200 bg-white px-4 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-300 dark:hover:bg-white/5"
                  >
                    <ExternalLink size={15} />
                    Abrir enlace
                  </a>
                </>
              )}
            </div>
          </div>
        </div>
      )}
    </ModuleBase>
  );
};
