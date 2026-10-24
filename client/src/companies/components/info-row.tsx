import { useState } from "react";
import { Check, Copy } from "lucide-react";
import type { InfoRowProps } from "@/companies/types/info-row-props";

export const InfoRow: React.FC<InfoRowProps> = ({ label, value, copyable = false }) => {
  const [copied, setCopied] = useState(false);
  return (
    <div>
      <p className="mb-1 text-xs text-gray-500 dark:text-gray-400">{label}</p>
      <p className="flex items-center gap-1 text-sm font-medium text-gray-800 dark:text-white/90">
        <span className={copyable ? "font-mono text-xs" : ""}>{value || "—"}</span>
        {copyable && value && (
          <button
            type="button"
            onClick={() => { navigator.clipboard.writeText(value); setCopied(true); setTimeout(() => setCopied(false), 2000); }}
            className="ml-0.5 inline-flex items-center rounded p-0.5 text-gray-400 hover:bg-gray-100 hover:text-gray-600 dark:hover:bg-gray-700 dark:hover:text-gray-300"
          >
            {copied ? <Check size={12} /> : <Copy size={12} />}
          </button>
        )}
      </p>
    </div>
  );
};
