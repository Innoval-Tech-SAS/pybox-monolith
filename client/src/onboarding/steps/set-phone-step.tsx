import React, { useState } from "react";
import { Input } from "@/ui/components/inputs/input";
import { Label } from "@/ui/components/inputs/label";
import { CountrySelect } from "@/ui/components/inputs/country-select";
import { useCountries } from "@/hooks/use-countries";
import { useSetPhone } from "@/hooks/use-set-phone";
import type { SetPhoneStepProps } from "@/onboarding/types/set-phone-step-props";

export const SetPhoneStep: React.FC<SetPhoneStepProps> = ({ onDone }) => {
  const [phoneNumber, setPhoneNumber] = useState("");
  const [phonePrefix, setPhonePrefix] = useState("");
  const { countries, loading: loadingCountries } = useCountries();
  const { setPhone, loading, error } = useSetPhone();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await setPhone(phonePrefix + phoneNumber);
      onDone();
    } catch {
      // error handled by hook
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      <div>
        <h2 className="text-lg font-semibold text-gray-800 dark:text-white/90">
          Registra tu número de teléfono
        </h2>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Necesitamos un número para verificar tu identidad.
        </p>
      </div>

      <div>
        <Label className="text-gray-500">Teléfono</Label>
        <div className="flex gap-2">
          <div className="w-28 shrink-0">
            <CountrySelect
              mode="PHONE"
              valueKey="phonePrefix"
              countries={countries}
              placeholder="+"
              value={phonePrefix}
              onChange={setPhonePrefix}
              className="pr-8"
              disabled={loadingCountries}
            />
          </div>
          <div className="flex-1 min-w-0">
            <Input
              type="tel"
              placeholder="300 000 0000"
              value={phoneNumber}
              onChange={(e) => setPhoneNumber(e.target.value)}
            />
          </div>
        </div>
      </div>

      {error && <p className="text-sm text-error-500">{error}</p>}

      <button
        type="submit"
        disabled={loading || !phoneNumber || !phonePrefix}
        className="flex w-full items-center justify-center rounded-lg bg-brand-500 px-4 py-3 text-sm font-medium text-white transition hover:bg-brand-600 disabled:opacity-50"
      >
        {loading ? "Guardando..." : "Continuar"}
      </button>
    </form>
  );
};
