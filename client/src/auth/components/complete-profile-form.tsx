import { useState } from "react";
import { useNavigate } from "react-router";
import { Input } from "../../ui/components/inputs/input";
import { CountrySelect } from "../../ui/components/inputs/country-select";
import { Label } from "../../ui/components/inputs/label";
import { SuccessModal } from "../../ui/components/modal/success-modal";
import { ErrorModal } from "../../ui/components/modal/error-modal";
import { Button } from "../../ui/components/button/button";
import { useModal } from "../../hooks/use-modal";
import { useOAuthRegister } from "../../hooks/use-oauth-register";
import { useCountries } from "../../hooks/use-countries";
import { CompleteProfileFormProps } from "../../types/props/complete-profile-form-props";

export const CompleteProfileForm: React.FC<CompleteProfileFormProps> = ({
  token,
}) => {
  const [nationality, setNationality] = useState("");
  const [phoneNumber, setPhoneNumber] = useState("");
  const [phonePrefix, setPhonePrefix] = useState("");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const { oauthRegister, loading, error } = useOAuthRegister();
  const { countries, loading: loadingNationalities } = useCountries();
  const navigate = useNavigate();
  const successModal = useModal();
  const errorModal = useModal();

  const handleNationalityChange = (code: string) => {
    setNationality(code);
    const nation = countries.find((n) => n.code === code);
    if (nation) setPhonePrefix(nation.phonePrefix);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await oauthRegister({
        provider: "GOOGLE",
        token,
        nationality,
        phoneNumber: phonePrefix + phoneNumber,
      });
      successModal.openModal();
    } catch (err) {
      setErrorMessage(
        err instanceof Error ? err.message : "Error al completar el registro",
      );
      errorModal.openModal();
    }
  };

  return (
    <>
      <form onSubmit={handleSubmit}>
        <div className="space-y-5">
          <div>
            <Label className="text-gray-500">
              Nacionalidad <span className="text-error-500">*</span>
            </Label>
            {/* CountrySelect no expone `id`, por lo que no puede enlazarse vía htmlFor
                sin modificar ui/components/inputs/country-select.tsx (fuera de alcance). */}
            <CountrySelect
              mode="NAME"
              required
              countries={countries}
              placeholder={
                loadingNationalities
                  ? "Cargando..."
                  : "Selecciona tu nacionalidad"
              }
              value={nationality}
              onChange={handleNationalityChange}
              disabled={loadingNationalities}
            />
          </div>

          <div>
            <Label className="text-gray-500">
              Teléfono <span className="text-error-500">*</span>
            </Label>
            <div className="flex gap-2">
              <div className="w-28 shrink-0">
                <CountrySelect
                  mode="PHONE"
                  valueKey="phonePrefix"
                  required
                  countries={countries}
                  placeholder="+"
                  value={phonePrefix}
                  onChange={setPhonePrefix}
                  className="pr-8"
                  disabled={loadingNationalities}
                />
              </div>
              <div className="flex-1 min-w-0">
                <Input
                  type="tel"
                  name="phone_number"
                  placeholder="300 000 0000"
                  value={phoneNumber}
                  onChange={(e) => setPhoneNumber(e.target.value)}
                  autoComplete="tel"
                  required
                />
              </div>
            </div>
          </div>

          {error && <p className="text-sm text-error-500">{error}</p>}

          <Button type="submit" size="sm" className="w-full" loading={loading} loadingText="Registrando...">
            Completar registro
          </Button>
        </div>
      </form>

      <SuccessModal
        isOpen={successModal.isOpen}
        title="¡Cuenta creada!"
        description="Tu cuenta fue registrada exitosamente."
        actionLabel="Ir al dashboard"
        onAction={() => navigate("/home", { replace: true })}
      />

      <ErrorModal
        isOpen={errorModal.isOpen}
        onClose={errorModal.closeModal}
        title="Error al registrar"
        message={
          errorMessage ?? "Ocurrió un error inesperado. Intenta nuevamente."
        }
      />
    </>
  );
};
