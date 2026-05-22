import React, { useEffect, useId, useMemo, useRef, useState } from "react";
import { useNationalities, NationalityOption } from "@/hooks/use-nationalities";
import { CountrySelectProps } from "@/types/props/country-select-props";
import { ChevronDownIcon } from "@/ui/icons";

const getLabel = (n: NationalityOption, mode: CountrySelectProps["mode"]): string => {
  switch (mode) {
    case "PREFIX": return n.code;
    case "NAME": return n.name;
    case "PHONE": return n.phonePrefix;
  }
};

const getOptionValue = (
  n: NationalityOption,
  valueKey: NonNullable<CountrySelectProps["valueKey"]>,
): string => (valueKey === "phonePrefix" ? n.phonePrefix : n.code);

const FlagEmoji: React.FC<{ code: string }> = ({ code }) => (
  <span
    aria-hidden="true"
    className={`fi fi-${code.toLowerCase()} shrink-0 rounded-sm`}
    style={{ width: "1.5rem", height: "1rem" }}
  />
);

export const CountrySelect: React.FC<CountrySelectProps> = ({
  mode,
  valueKey = "code",
  value = "",
  onChange,
  nationalities: externalNationalities,
  placeholder = "Selecciona un país",
  className = "",
  disabled = false,
  required = false,
}) => {
  const listboxId = useId();
  const containerRef = useRef<HTMLDivElement>(null);
  const [open, setOpen] = useState(false);
  const { nationalities: fetched, loading } = useNationalities();
  const nationalities = externalNationalities ?? fetched;
  const isDisabled = disabled || loading;
  const selected = useMemo(
    () => nationalities.find((n) => getOptionValue(n, valueKey) === value),
    [nationalities, value, valueKey],
  );

  useEffect(() => {
    if (!open) return;

    const handleClickOutside = (event: MouseEvent) => {
      if (!containerRef.current?.contains(event.target as Node)) {
        setOpen(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [open]);

  const handleSelect = (country: NationalityOption) => {
    onChange(getOptionValue(country, valueKey));
    setOpen(false);
  };

  const buttonText = loading
    ? "Cargando países..."
    : selected
      ? getLabel(selected, mode)
      : placeholder;

  return (
    <div ref={containerRef} className="relative w-full">
      <button
        type="button"
        aria-haspopup="listbox"
        aria-expanded={open}
        aria-controls={listboxId}
        aria-required={required}
        disabled={isDisabled}
        onClick={() => setOpen((current) => !current)}
        onKeyDown={(event) => {
          if (event.key === "Escape") setOpen(false);
        }}
        className={`flex h-11 w-full items-center justify-between gap-3 rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 pr-3 text-left text-sm shadow-theme-xs transition focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 disabled:cursor-not-allowed disabled:opacity-50 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:focus:border-brand-800 ${
          selected ? "text-gray-800 dark:text-white/90" : "text-gray-400 dark:text-gray-400"
        } ${className}`}
      >
        <span className="flex min-w-0 items-center gap-2">
          {selected && <FlagEmoji code={selected.code} />}
          <span className="truncate">{buttonText}</span>
        </span>
        <ChevronDownIcon
          className={`h-5 w-5 shrink-0 text-gray-400 transition-transform ${
            open ? "rotate-180" : ""
          }`}
        />
      </button>

      {open && !isDisabled && (
        <div
          id={listboxId}
          role="listbox"
          className="absolute z-50 mt-1 max-h-60 w-full overflow-auto rounded-lg border border-gray-200 bg-white py-1 shadow-lg dark:border-gray-700 dark:bg-gray-900"
        >
          {nationalities.map((n) => {
            const optionValue = getOptionValue(n, valueKey);
            const isSelected = optionValue === value;
            return (
              <button
                key={`${n.code}-${optionValue}`}
                type="button"
                role="option"
                aria-selected={isSelected}
                onClick={() => handleSelect(n)}
                className={`flex h-10 w-full items-center gap-2 px-4 text-left text-sm transition hover:bg-gray-50 dark:hover:bg-gray-800 ${
                  isSelected
                    ? "bg-brand-50 text-brand-600 dark:bg-brand-500/10 dark:text-brand-300"
                    : "text-gray-700 dark:text-gray-300"
                }`}
              >
                <FlagEmoji code={n.code} />
                <span className="truncate">{getLabel(n, mode)}</span>
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
};
