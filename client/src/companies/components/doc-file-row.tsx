import { useRef } from "react";
import { CheckCircle2, ExternalLink, Upload } from "lucide-react";
import type { DocFileRowProps } from "@/companies/types/doc-file-row-props";
import { resolveFileUrl } from "@/companies/utils/resolve-doc-file-url";

export const DocFileRow: React.FC<DocFileRowProps> = ({ label, fileUrl, docType, saving, onUpload }) => {
  const inputRef = useRef<HTMLInputElement>(null);
  const resolved = resolveFileUrl(fileUrl);

  return (
    <div className="flex items-center justify-between gap-4 rounded-xl border border-gray-200 p-4 dark:border-gray-800">
      <div className="min-w-0">
        <p className="mb-0.5 text-xs text-gray-500 dark:text-gray-400">{label}</p>
        {resolved ? (
          // El nombre real del archivo no se guarda (se sube y almacena siempre con
          // nombre uuid7, ver generate_uuid7_filename en la API): no hay nada legible
          // que mostrar aquí más allá de confirmar que el documento está cargado.
          <p className="flex items-center gap-1.5 text-sm font-medium text-gray-800 dark:text-white/90">
            <CheckCircle2 size={14} className="shrink-0 text-success-500" />
            Documento cargado
          </p>
        ) : (
          <p className="text-sm text-gray-400 dark:text-gray-500">Sin documento</p>
        )}
      </div>
      <div className="flex shrink-0 items-center gap-2">
        {resolved && (
          <a
            href={resolved}
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center gap-1.5 rounded-lg border border-gray-300 bg-white px-3 py-1.5 text-xs font-medium text-gray-700 hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-300"
          >
            <ExternalLink size={12} />
            Ver
          </a>
        )}
        <input
          ref={inputRef}
          type="file"
          accept=".pdf,.jpg,.jpeg,.png"
          className="hidden"
          onChange={(e) => {
            const file = e.target.files?.[0];
            if (file) { onUpload(docType, file); e.target.value = ""; }
          }}
        />
        <button
          type="button"
          onClick={() => inputRef.current?.click()}
          disabled={saving}
          className="inline-flex items-center gap-1.5 rounded-lg border border-gray-300 bg-white px-3 py-1.5 text-xs font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-300"
        >
          <Upload size={12} />
          {resolved ? "Reemplazar" : "Subir"}
        </button>
      </div>
    </div>
  );
};
