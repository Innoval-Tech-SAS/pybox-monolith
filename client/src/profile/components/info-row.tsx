export const InfoRow = ({ label, value }: { label: string; value?: React.ReactNode }) => (
  <div className="min-w-0">
    <p className="mb-1 text-xs text-gray-500 dark:text-gray-400">{label}</p>
    <p className="break-words text-sm font-medium text-gray-800 dark:text-white/90">{value || "—"}</p>
  </div>
);
