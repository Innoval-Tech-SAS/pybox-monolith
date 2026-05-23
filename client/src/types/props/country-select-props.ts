import type { NationalityOption } from "@/types/countries/country-types";

export type CountrySelectMode = "PREFIX" | "NAME" | "PHONE";
export type CountrySelectValueKey = "code" | "phonePrefix";

export interface CountrySelectProps {
  mode: CountrySelectMode;
  valueKey?: CountrySelectValueKey;
  value?: string;
  onChange: (value: string) => void;
  /** Si se provee, no hace fetch interno (evita petición duplicada). */
  nationalities?: NationalityOption[];
  placeholder?: string;
  className?: string;
  disabled?: boolean;
  required?: boolean;
}

export interface FlagEmojiProps {
  code: string;
}
