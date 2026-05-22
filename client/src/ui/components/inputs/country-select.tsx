import React from "react";
import { useNationalities, NationalityOption } from "@/hooks/use-nationalities";
import { getFlagEmoji } from "@/utils/flag-emoji";
import { CountrySelectProps } from "@/types/props/country-select-props";

const getLabel = (n: NationalityOption, mode: CountrySelectProps["mode"]): string => {
  const flag = getFlagEmoji(n.code);
  switch (mode) {
    case "PREFIX": return `${flag} ${n.code}`;
    case "NAME":   return `${flag} ${n.name}`;
    case "PHONE":  return `${flag} ${n.phonePrefix}`;
  }
};

export const CountrySelect: React.FC<CountrySelectProps> = ({
  mode,
  value = "",
  onChange,
  nationalities: externalNationalities,
  placeholder = "Selecciona un país",
  className = "",
  disabled = false,
  required = false,
}) => {
  const { nationalities: fetched, loading } = useNationalities();
  const nationalities = externalNationalities ?? fetched;

  return (
    <select
      required={required}
      value={value}
      onChange={(e) => onChange(e.target.value)}
      disabled={disabled || loading}
      className={`h-11 w-full appearance-none rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 pr-11 text-sm shadow-theme-xs focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:focus:border-brand-800 ${
        value ? "text-gray-800 dark:text-white/90" : "text-gray-400 dark:text-gray-400"
      } ${className}`}
    >
      <option value="" disabled className="text-gray-700 dark:bg-gray-900 dark:text-gray-400">
        {loading ? "Cargando países..." : placeholder}
      </option>
      {nationalities.map((n) => (
        <option
          key={n.code}
          value={n.code}
          className="text-gray-700 dark:bg-gray-900 dark:text-gray-400"
        >
          {getLabel(n, mode)}
        </option>
      ))}
    </select>
  );
};
