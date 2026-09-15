import { Spinner } from "@/ui/components/loader/spinner";
import type { CheckItemProps } from "@/users/types/props/check-item-props";

export const CheckItem: React.FC<CheckItemProps> = ({
  id,
  label,
  sublabel,
  checked,
  busy,
  indent,
  onChange,
}) => (
  <li className={`border-b border-gray-200 py-3 last:border-b-0 dark:border-gray-800 ${indent ? "pl-10 pr-4" : "px-4"}`}>
    <div className="flex items-center justify-between gap-3">
      <label htmlFor={id} className="flex flex-1 cursor-pointer select-none items-center gap-3">
        <div className="relative size-5 shrink-0">
          <input
            id={id}
            type="checkbox"
            checked={checked}
            disabled={busy}
            onChange={(e) => onChange(e.target.checked)}
            className="size-5 appearance-none cursor-pointer rounded-md border border-gray-300 checked:border-transparent checked:bg-brand-500 disabled:cursor-not-allowed disabled:opacity-50 dark:border-gray-700"
          />
          {checked && (
            <svg
              className="pointer-events-none absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2"
              width="14" height="14" viewBox="0 0 14 14" fill="none"
            >
              <path d="M11.6666 3.5L5.24992 9.91667L2.33325 7" stroke="white" strokeWidth="1.94" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          )}
        </div>
        <span>
          <span className="block text-sm text-gray-700 dark:text-gray-300">{label}</span>
          {sublabel && (
            <span className="block text-xs text-gray-400 dark:text-gray-500 mt-0.5">{sublabel}</span>
          )}
        </span>
      </label>
      {busy && <Spinner size="xs" tone="brand" className="shrink-0" />}
    </div>
  </li>
);
