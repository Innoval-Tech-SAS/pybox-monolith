import { useRef } from "react";
import { Building2, Upload } from "lucide-react";
import type { LogoUploadCardProps } from "@/companies/types/logo-upload-card-props";
import { resolveFileUrl } from "@/companies/utils/resolve-doc-file-url";

export const LogoUploadCard: React.FC<LogoUploadCardProps> = ({ logoUrl, saving, onUpload }) => {
  const inputRef = useRef<HTMLInputElement>(null);
  const resolved = resolveFileUrl(logoUrl);

  return (
    <div className="flex items-center gap-4 rounded-xl border border-gray-200 p-4 dark:border-gray-800">
      <div className="flex size-16 shrink-0 items-center justify-center overflow-hidden rounded-lg border border-gray-200 bg-gray-50 dark:border-gray-800 dark:bg-gray-900">
        {resolved ? (
          <img src={resolved} alt="Logo de la empresa" className="size-full object-contain" />
        ) : (
          <Building2 size={24} className="text-gray-300 dark:text-gray-600" />
        )}
      </div>
      <div className="min-w-0 flex-1">
        <p className="text-sm font-medium text-gray-800 dark:text-white/90">Logo de la empresa</p>
        <p className="text-xs text-gray-400 dark:text-gray-500">PNG, JPG o WebP · máx. 10 MB</p>
      </div>
      <input
        ref={inputRef}
        type="file"
        accept=".png,.jpg,.jpeg,.webp"
        className="hidden"
        onChange={(e) => {
          const file = e.target.files?.[0];
          if (file) { onUpload(file); e.target.value = ""; }
        }}
      />
      <button
        type="button"
        onClick={() => inputRef.current?.click()}
        disabled={saving}
        className="inline-flex shrink-0 items-center gap-1.5 rounded-lg border border-gray-300 bg-white px-3 py-1.5 text-xs font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-300"
      >
        <Upload size={12} />
        {resolved ? "Reemplazar" : "Subir"}
      </button>
    </div>
  );
};
