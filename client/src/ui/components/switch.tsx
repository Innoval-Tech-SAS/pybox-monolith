import type { SwitchProps } from "@/types/props/switch-props";

export const Switch: React.FC<SwitchProps> = ({ checked, onChange, label, disabled = false }) => (
  <label
    className={`flex cursor-pointer select-none items-center gap-3 text-sm font-medium ${
      disabled ? "text-gray-400 pointer-events-none" : "text-gray-700 dark:text-gray-400"
    }`}
  >
    <div className="relative">
      <div
        className={`block h-6 w-11 rounded-full transition duration-150 ease-linear ${
          disabled
            ? "bg-gray-100 dark:bg-gray-800"
            : checked
            ? "bg-brand-500"
            : "bg-gray-200 dark:bg-white/10"
        }`}
        onClick={() => !disabled && onChange(!checked)}
      />
      <div
        className={`absolute left-0.5 top-0.5 h-5 w-5 rounded-full bg-white shadow-theme-sm transition-transform duration-150 ease-linear ${
          checked ? "translate-x-full" : "translate-x-0"
        }`}
      />
    </div>
    {label && <span>{label}</span>}
  </label>
);
