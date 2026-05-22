import { useState, useMemo } from "react";
import { useNavigate } from "react-router";
import { Input } from "../../ui/components/inputs/input";
import { Select } from "../../ui/components/inputs/select";
import { Label } from "../../ui/components/inputs/label";
import { SuccessModal } from "../../ui/components/modal/success-modal";
import { ErrorModal } from "../../ui/components/modal/error-modal";
import { useModal } from "../../hooks/use-modal";
import { useOAuthRegister } from "../../hooks/use-oauth-register";
import { useNationalities } from "../../hooks/use-nationalities";
import { getFlagEmoji } from "../../utils/flag-emoji";
import { CompleteProfileFormProps } from "../../types/props/complete-profile-form-props";

export const CompleteProfileForm: React.FC<CompleteProfileFormProps> = ({ token, email }) => {
  const [nationality, setNationality] = useState("");
  const [phoneNumber, setPhoneNumber] = useState("");
  const [phonePrefix, setPhonePrefix] = useState("");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const { oauthRegister, loading, error } = useOAuthRegister();
  const { nationalities, loading: loadingNationalities } = useNationalities();
  const navigate = useNavigate();
  const successModal = useModal();
  const errorModal = useModal();

  const nationalityOptions = useMemo(
    () => nationalities.map((n) => ({ value: n.code, label: `${getFlagEmoji(n.code)} ${n.name}` })),
    [nationalities]
  );

  const prefixOptions = useMemo(() => {
    const seen = new Set<string>();
    return nationalities
      .filter((n) => {
        if (seen.has(n.phonePrefix)) return false;
        seen.add(n.phonePrefix);
        return true;
      })
      .map((n) => ({ value: n.phonePrefix, label: `${getFlagEmoji(n.code)} ${n.phonePrefix}` }));
  }, [nationalities]);

  const handleNationalityChange = (code: string) => {
    setNationality(code);
    const nation = nationalities.find((n) => n.code === code);
    if (nation) setPhonePrefix(nation.phonePrefix);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await oauthRegister({
        provider: "GOOGLE",
        token,
        nationality,
        phone_number: phonePrefix + phoneNumber,
      });
      successModal.openModal();
    } catch (err) {
      setErrorMessage(err instanceof Error ? err.message : "Error al completar el registro");
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
            <Select
              options={nationalityOptions}
              placeholder={loadingNationalities ? "Cargando..." : "Selecciona tu nacionalidad"}
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
                <Select
                  options={prefixOptions}
                  placeholder="+"
                  value={phonePrefix}
                  onChange={setPhonePrefix}
                  className="pr-8"
                />
              </div>
              <div className="flex-1 min-w-0">
                <Input
                  type="tel"
                  name="phone_number"
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
            disabled={loading}
            className="flex items-center justify-center w-full px-4 py-3 text-sm font-medium text-white transition rounded-lg bg-brand-500 shadow-theme-xs hover:bg-brand-600 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? "Registrando..." : "Completar registro"}
          </button>
        </div>
      </form>

      <SuccessModal
        isOpen={successModal.isOpen}
        title="¡Cuenta creada!"
        description="Tu cuenta fue registrada exitosamente."
        actionLabel="Ir al dashboard"
        onAction={() => navigate("/dashboard", { replace: true })}
      />

      <ErrorModal
        isOpen={errorModal.isOpen}
        onClose={errorModal.closeModal}
        title="Error al registrar"
        message={errorMessage ?? "Ocurrió un error inesperado. Intenta nuevamente."}
      />
    </>
  );
};
