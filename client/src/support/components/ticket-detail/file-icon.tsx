import { Image, FileText } from "lucide-react";

const IMAGE_EXTS = new Set([".jpg", ".jpeg", ".png"]);

export const FileIcon: React.FC<{ name: string }> = ({ name }) => {
  const ext = name.slice(name.lastIndexOf(".")).toLowerCase();
  return IMAGE_EXTS.has(ext) ? (
    <Image size={16} className="text-brand-500" />
  ) : (
    <FileText size={16} className="text-gray-500 dark:text-gray-400" />
  );
};
