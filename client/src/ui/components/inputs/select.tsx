import { useState } from "react";
import type { SelectProps } from "@/types/props/select-props";

export const Select: React.FC<SelectProps> = ({
  options,
  placeholder = "Selecciona una opción",
  onChange,
  className = "",
  value,
  defaultValue = "",
  disabled = false,
}) => {
  const [internalValue, setInternalValue] = useState(defaultValue);
  const current = value !== undefined ? value : internalValue;

  const handleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const v = e.target.value;
    if (value === undefined) setInternalValue(v);
    onChange(v);
  };

  return (
    <select
      className={`h-11 w-full appearance-none rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 pr-11 text-sm shadow-theme-xs focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:focus:border-brand-800 ${
        current ? "text-gray-800 dark:text-white/90" : "text-gray-400 dark:text-gray-400"
      } ${className}`}
      value={current}
      onChange={handleChange}
      disabled={disabled}
    >
      <option value="" disabled className="text-gray-700 dark:bg-gray-900 dark:text-gray-400">
        {placeholder}
      </option>
      {options.map((opt) => (
        <option key={opt.value} value={opt.value} className="text-gray-700 dark:bg-gray-900 dark:text-gray-400">
          {opt.label}
        </option>
      ))}
    </select>
  );
};
