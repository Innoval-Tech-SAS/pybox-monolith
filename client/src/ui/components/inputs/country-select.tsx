import React, { useId, useMemo, useState } from "react";
import { createPortal } from "react-dom";
import { useCountries } from "@/hooks/use-countries";
import { usePortalDropdown } from "@/hooks/use-portal-dropdown";
import type { NationalityOption } from "@/types/countries/country-types";
import type {
  CountrySelectProps,
  FlagEmojiProps,
} from "@/types/props/country-select-props";
import {
  getCountrySelectLabel,
  getCountrySelectOptionValue,
} from "@/ui/utils/country-select-utils";
import { ChevronDownIcon } from "@/ui/icons";

const FlagEmoji: React.FC<FlagEmojiProps> = ({ code }) => (
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
  countries: externalCountries,
  placeholder = "Selecciona un país",
  className = "",
  disabled = false,
  required = false,
}) => {
  const listboxId = useId();
  const [open, setOpen] = useState(false);
  const { countries: fetched, loading } = useCountries();
  const countries = externalCountries ?? fetched;
  const isDisabled = disabled || loading;
  const selected = useMemo(
    () => countries.find((n) => getCountrySelectOptionValue(n, valueKey) === value),
    [countries, value, valueKey],
  );

  // El dropdown se renderiza en un portal (position: fixed) para no quedar recortado
  // por ancestros con overflow (p. ej. el modal de onboarding, que es overflow-y-auto).
  const { triggerRef, dropdownRef, dropdownStyle } = usePortalDropdown<
    HTMLButtonElement,
    HTMLDivElement
  >({ open, onClose: () => setOpen(false) });

  const handleSelect = (country: NationalityOption) => {
    onChange(getCountrySelectOptionValue(country, valueKey));
    setOpen(false);
  };

  const buttonText = loading
    ? "Cargando países..."
    : selected
      ? getCountrySelectLabel(selected, mode)
      : placeholder;

  return (
    <div className="relative w-full">
      <button
        ref={triggerRef}
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

      {open && !isDisabled && dropdownStyle &&
        createPortal(
          <div
            ref={dropdownRef}
            id={listboxId}
            role="listbox"
            style={dropdownStyle}
            className="max-h-60 overflow-auto rounded-lg border border-gray-200 bg-white py-1 shadow-lg dark:border-gray-700 dark:bg-gray-900"
          >
            {countries.map((n) => {
              const optionValue = getCountrySelectOptionValue(n, valueKey);
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
                  <span className="truncate">{getCountrySelectLabel(n, mode)}</span>
                </button>
              );
            })}
          </div>,
          document.body,
        )}
    </div>
  );
};
