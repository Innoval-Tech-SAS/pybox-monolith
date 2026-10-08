import type { NationalityOption } from "@/types/countries/country-types";
import type {
  CountrySelectMode,
  CountrySelectValueKey,
} from "@/types/props/country-select-props";

export const getCountrySelectLabel = (
  nationality: NationalityOption,
  mode: CountrySelectMode,
): string => {
  switch (mode) {
    case "PREFIX":
      return nationality.code;
    case "NAME":
      return nationality.name;
    case "PHONE":
      return nationality.phonePrefix;
  }
};

export const getCountrySelectOptionValue = (
  nationality: NationalityOption,
  valueKey: CountrySelectValueKey,
): string => (valueKey === "phonePrefix" ? nationality.phonePrefix : nationality.code);
