import type { EmptyStateProps } from "@/types/props/empty-state-props";

export default function EmptyState({ title, icon: Icon, className }: EmptyStateProps) {
  return (
    <div className={`flex flex-col items-center justify-center gap-3 text-gray-400 dark:text-gray-500 ${className ?? ""}`}>
      {Icon && <Icon size={48} strokeWidth={1.5} />}
      <p className="text-sm">{title}</p>
    </div>
  );
}
