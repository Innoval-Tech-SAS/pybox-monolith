import { useState } from "react";
import { Check, Copy } from "lucide-react";
import type { CopyToClipboardButtonProps } from "@/types/props/copy-to-clipboard-button-props";

export const CopyToClipboardButton: React.FC<CopyToClipboardButtonProps> = ({ text, title = "Copiar" }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <button
      onClick={handleCopy}
      title={title}
      className="ml-1.5 inline-flex items-center rounded p-0.5 text-gray-400 transition hover:bg-gray-100 hover:text-gray-600 dark:hover:bg-gray-700 dark:hover:text-gray-300"
    >
      {copied ? <Check size={13} /> : <Copy size={13} />}
    </button>
  );
};
