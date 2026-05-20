import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router";
import { jwtDecode } from "jwt-decode";
import { Input } from "../../ui/components/inputs/input";
import { Label } from "../../ui/components/inputs/label";
import { EyeCloseIcon, EyeIcon } from "../../ui/icons";
import { Modal } from "../../ui/components/modal/modal";
import { useModal } from "../../hooks/use-modal";
import { useRegister } from "../../hooks/use-register";
import { useGoogleAuth } from "../../hooks/use-google-auth";
import { useOAuthRegister } from "../../hooks/use-oauth-register";

const DOCUMENT_TYPES = [
  { value: "CÉDULA DE CIUDADANÍA", label: "Cédula de ciudadanía" },
  { value: "CÉDULA DE EXTRANJERÍA", label: "Cédula de extranjería" },
  { value: "PASAPORTE", label: "Pasaporte" },
  { value: "NIT", label: "NIT" },
  { value: "PERMISO ESPECIAL DE PERMANENCIA", label: "Permiso especial de permanencia" },
];

interface GooglePayload {
  email: string;
  given_name?: string;
  family_name?: string;
}

const MANUAL_INITIAL = {
  firstname: "",
  lastname: "",
  email: "",
  password: "",
  phone_number: "",
  document_type: "",
  document_number: "",
};

const DOC_INITIAL = { phone_number: "", document_type: "", document_number: "" };

export const SignUpForm: React.FC = () => {
  const [manualForm, setManualForm] = useState(MANUAL_INITIAL);
  const [docForm, setDocForm] = useState(DOC_INITIAL);
  const [showPassword, setShowPassword] = useState(false);
  const [googleToken, setGoogleToken] = useState<string | null>(null);
  const [googleEmail, setGoogleEmail] = useState<string | null>(null);

  const { register, loading: loadingManual, error: errorManual } = useRegister();
  const { oauthRegister, loading: loadingOAuth, error: errorOAuth } = useOAuthRegister();
  const { signIn } = useGoogleAuth();
  const navigate = useNavigate();
  const successModal = useModal();
  const errorModal = useModal();
  const [countdown, setCountdown] = useState(10);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const loading = loadingManual || loadingOAuth;
  const error = errorManual || errorOAuth;

  useEffect(() => {
    if (!successModal.isOpen) return;
    if (countdown === 0) {
      navigate("/admin/dashboard", { replace: true });
      return;
    }
    const timer = setTimeout(() => setCountdown((c) => c - 1), 1000);
    return () => clearTimeout(timer);
  }, [successModal.isOpen, countdown, navigate]);

  const handleGoogleClick = () => {
    signIn((token) => {
      const payload = jwtDecode<GooglePayload>(token);
      setGoogleToken(token);
      setGoogleEmail(payload.email);
    });
  };

  const handleManualChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setManualForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleDocChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setDocForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (googleToken) {
        await oauthRegister({ provider: "GOOGLE", token: googleToken, ...docForm });
      } else {
        await register(manualForm);
      }
      setCountdown(10);
      successModal.openModal();
    } catch (err) {
      setErrorMessage(err instanceof Error ? err.message : "Error al registrar usuario");
      errorModal.openModal();
    }
  };

  const selectClasses =
    "h-11 w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/20 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90";

  return (
    <div className="flex flex-col flex-1 overflow-y-auto">
      <div className="flex flex-col justify-center flex-1 w-full max-w-md mx-auto py-8">
        <div className="mb-5 sm:mb-8">
          <h1 className="mb-2 font-semibold text-gray-800 text-title-sm dark:text-white/90 sm:text-title-md">
            Crear cuenta
          </h1>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Completa tus datos para registrarte
          </p>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="space-y-5">
            {/* Manual fields — hidden when Google is active */}
            {!googleToken && (
              <>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label className="text-gray-500">Nombre <span className="text-error-500">*</span></Label>
                    <Input name="firstname" placeholder="Tu nombre" value={manualForm.firstname} onChange={handleManualChange} />
                  </div>
                  <div>
                    <Label className="text-gray-500">Apellido <span className="text-error-500">*</span></Label>
                    <Input name="lastname" placeholder="Tu apellido" value={manualForm.lastname} onChange={handleManualChange} />
                  </div>
                </div>
                <div>
                  <Label className="text-gray-500">Correo electrónico <span className="text-error-500">*</span></Label>
                  <Input type="email" name="email" placeholder="correo@ejemplo.com" value={manualForm.email} onChange={handleManualChange} />
                </div>
                <div>
                  <Label className="text-gray-500">Contraseña <span className="text-error-500">*</span></Label>
                  <div className="relative">
                    <Input
                      type={showPassword ? "text" : "password"}
                      name="password"
                      placeholder="Ingresa tu contraseña"
                      value={manualForm.password}
                      onChange={handleManualChange}
                    />
                    <span
                      onClick={() => setShowPassword((v) => !v)}
                      className="absolute z-30 -translate-y-1/2 cursor-pointer right-4 top-1/2"
                    >
                      {showPassword
                        ? <EyeIcon className="fill-gray-500 dark:fill-gray-400 size-5" />
                        : <EyeCloseIcon className="fill-gray-500 dark:fill-gray-400 size-5" />}
                    </span>
                  </div>
                </div>
              </>
            )}

            {/* Always required fields */}
            <div>
              <Label className="text-gray-500">Teléfono <span className="text-error-500">*</span></Label>
              {googleToken ? (
                <Input type="tel" name="phone_number" placeholder="+57 300 000 0000" value={docForm.phone_number} onChange={handleDocChange} />
              ) : (
                <Input type="tel" name="phone_number" placeholder="+57 300 000 0000" value={manualForm.phone_number} onChange={handleManualChange} />
              )}
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label className="text-gray-500">Tipo de documento <span className="text-error-500">*</span></Label>
                <select
                  name="document_type"
                  value={googleToken ? docForm.document_type : manualForm.document_type}
                  onChange={googleToken ? handleDocChange : handleManualChange}
                  className={selectClasses}
                >
                  <option value="" disabled>Selecciona</option>
                  {DOCUMENT_TYPES.map((dt) => (
                    <option key={dt.value} value={dt.value}>{dt.label}</option>
                  ))}
                </select>
              </div>
              <div>
                <Label className="text-gray-500">Número de documento <span className="text-error-500">*</span></Label>
                {googleToken ? (
                  <Input name="document_number" placeholder="1234567890" value={docForm.document_number} onChange={handleDocChange} />
                ) : (
                  <Input name="document_number" placeholder="1234567890" value={manualForm.document_number} onChange={handleManualChange} />
                )}
              </div>
            </div>

            {error && <p className="text-sm text-error-500">{error}</p>}

            <button
              type="submit"
              disabled={loading}
              className="w-full border border-gray-500 p-2 rounded-2xl hover:bg-gray-400/50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? "Registrando..." : "Crear cuenta"}
            </button>
          </div>
        </form>

        <div className="relative py-4">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-gray-200 dark:border-gray-800" />
          </div>
          <div className="relative flex justify-center text-sm">
            <span className="px-4 py-1 text-gray-400 bg-white dark:bg-gray-900">O</span>
          </div>
        </div>

        {/* Google button */}
        <button
          type="button"
          onClick={handleGoogleClick}
          className="inline-flex items-center justify-center gap-3 py-3 text-sm font-normal text-gray-700 transition-colors bg-gray-100 rounded-lg px-7 hover:bg-gray-200 dark:bg-white/5 dark:text-white/90 dark:hover:bg-white/10 w-full"
        >
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M18.7511 10.1944C18.7511 9.47495 18.6915 8.94995 18.5626 8.40552H10.1797V11.6527H15.1003C15.0011 12.4597 14.4654 13.675 13.2749 14.4916L13.2582 14.6003L15.9087 16.6126L16.0924 16.6305C17.7788 15.1041 18.7511 12.8583 18.7511 10.1944Z" fill="#4285F4"/>
            <path d="M10.1788 18.75C12.5895 18.75 14.6133 17.9722 16.0915 16.6305L13.274 14.4916C12.5201 15.0068 11.5081 15.3666 10.1788 15.3666C7.81773 15.3666 5.81379 13.8402 5.09944 11.7305L4.99473 11.7392L2.23868 13.8295L2.20264 13.9277C3.67087 16.786 6.68674 18.75 10.1788 18.75Z" fill="#34A853"/>
            <path d="M5.10014 11.7305C4.91165 11.186 4.80257 10.6027 4.80257 9.99992C4.80257 9.3971 4.91165 8.81379 5.09022 8.26935L5.08523 8.1534L2.29464 6.02954L2.20333 6.0721C1.5982 7.25823 1.25098 8.5902 1.25098 9.99992C1.25098 11.4096 1.5982 12.7415 2.20333 13.9277L5.10014 11.7305Z" fill="#FBBC05"/>
            <path d="M10.1789 4.63331C11.8554 4.63331 12.9864 5.34303 13.6312 5.93612L16.1511 3.525C14.6035 2.11528 12.5895 1.25 10.1789 1.25C6.68676 1.25 3.67088 3.21387 2.20264 6.07218L5.08953 8.26943C5.81381 6.15972 7.81776 4.63331 10.1789 4.63331Z" fill="#EB4335"/>
          </svg>
          {googleEmail ? `Conectado como ${googleEmail}` : "Registrarse con Google"}
        </button>

        <div className="mt-5">
          <p className="text-sm font-normal text-center text-gray-700 dark:text-gray-400 sm:text-start">
            ¿Ya tienes cuenta?{" "}
            <Link to="/admin/sign-in" className="text-brand-500 hover:text-brand-600 dark:text-brand-400">
              Inicia sesión
            </Link>
          </p>
        </div>
      </div>

      {/* Success Modal */}
      <Modal isOpen={successModal.isOpen} onClose={() => {}} showCloseButton={false} className="max-w-150 p-5 lg:p-10">
        <div className="text-center">
          <div className="relative flex items-center justify-center z-1 mb-7">
            <svg className="fill-success-50 dark:fill-success-500/15" width="90" height="90" viewBox="0 0 90 90" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M34.364 6.85053C38.6205 -2.28351 51.3795 -2.28351 55.636 6.85053C58.0129 11.951 63.5594 14.6722 68.9556 13.3853C78.6192 11.0807 86.5743 21.2433 82.2185 30.3287C79.7862 35.402 81.1561 41.5165 85.5082 45.0122C93.3019 51.2725 90.4628 63.9451 80.7747 66.1403C75.3648 67.3661 71.5265 72.2695 71.5572 77.9156C71.6123 88.0265 60.1169 93.6664 52.3918 87.3184C48.0781 83.7737 41.9219 83.7737 37.6082 87.3184C29.8831 93.6664 18.3877 88.0266 18.4428 77.9156C18.4735 72.2695 14.6352 67.3661 9.22531 66.1403C-0.462787 63.9451 -3.30193 51.2725 4.49185 45.0122C8.84391 41.5165 10.2138 35.402 7.78151 30.3287C3.42572 21.2433 11.3808 11.0807 21.0444 13.3853C26.4406 14.6722 31.9871 11.951 34.364 6.85053Z" fill="" fillOpacity="" />
            </svg>
            <span className="absolute -translate-x-1/2 -translate-y-1/2 left-1/2 top-1/2">
              <svg className="fill-success-600 dark:fill-success-500" width="38" height="38" viewBox="0 0 38 38" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path fillRule="evenodd" clipRule="evenodd" d="M5.9375 19.0004C5.9375 11.7854 11.7864 5.93652 19.0014 5.93652C26.2164 5.93652 32.0653 11.7854 32.0653 19.0004C32.0653 26.2154 26.2164 32.0643 19.0014 32.0643C11.7864 32.0643 5.9375 26.2154 5.9375 19.0004ZM19.0014 2.93652C10.1296 2.93652 2.9375 10.1286 2.9375 19.0004C2.9375 27.8723 10.1296 35.0643 19.0014 35.0643C27.8733 35.0643 35.0653 27.8723 35.0653 19.0004C35.0653 10.1286 27.8733 2.93652 19.0014 2.93652ZM24.7855 17.0575C25.3713 16.4717 25.3713 15.522 24.7855 14.9362C24.1997 14.3504 23.25 14.3504 22.6642 14.9362L17.7177 19.8827L15.3387 17.5037C14.7529 16.9179 13.8031 16.9179 13.2173 17.5037C12.6316 18.0894 12.6316 19.0392 13.2173 19.625L16.657 23.0647C16.9383 23.346 17.3199 23.504 17.7177 23.504C18.1155 23.504 18.4971 23.346 18.7784 23.0647L24.7855 17.0575Z" fill="" />
              </svg>
            </span>
          </div>
          <h4 className="mb-2 text-2xl font-semibold text-gray-800 dark:text-white/90 sm:text-title-sm">
            ¡Cuenta creada!
          </h4>
          <p className="text-sm leading-6 text-gray-500 dark:text-gray-400">
            Tu cuenta fue registrada exitosamente. Serás redirigido al dashboard en{" "}
            <span className="font-semibold text-success-600 dark:text-success-500">{countdown}s</span>.
          </p>
          <div className="flex items-center justify-center w-full gap-3 mt-7">
            <button
              type="button"
              onClick={() => navigate("/admin/dashboard", { replace: true })}
              className="flex justify-center w-full px-4 py-3 text-sm font-medium text-white rounded-lg bg-success-500 shadow-theme-xs hover:bg-success-600 sm:w-auto"
            >
              Ir al dashboard ahora
            </button>
          </div>
        </div>
      </Modal>

      {/* Error Modal */}
      <Modal isOpen={errorModal.isOpen} onClose={errorModal.closeModal} className="max-w-xl p-6 lg:p-12">
        <div className="text-center">
          <div className="relative flex items-center justify-center z-1 mb-7">
            <svg className="fill-error-50 dark:fill-error-500/15" width="90" height="90" viewBox="0 0 90 90" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M34.364 6.85053C38.6205 -2.28351 51.3795 -2.28351 55.636 6.85053C58.0129 11.951 63.5594 14.6722 68.9556 13.3853C78.6192 11.0807 86.5743 21.2433 82.2185 30.3287C79.7862 35.402 81.1561 41.5165 85.5082 45.0122C93.3019 51.2725 90.4628 63.9451 80.7747 66.1403C75.3648 67.3661 71.5265 72.2695 71.5572 77.9156C71.6123 88.0265 60.1169 93.6664 52.3918 87.3184C48.0781 83.7737 41.9219 83.7737 37.6082 87.3184C29.8831 93.6664 18.3877 88.0266 18.4428 77.9156C18.4735 72.2695 14.6352 67.3661 9.22531 66.1403C-0.462787 63.9451 -3.30193 51.2725 4.49185 45.0122C8.84391 41.5165 10.2138 35.402 7.78151 30.3287C3.42572 21.2433 11.3808 11.0807 21.0444 13.3853C26.4406 14.6722 31.9871 11.951 34.364 6.85053Z" fill="" fillOpacity="" />
            </svg>
            <span className="absolute -translate-x-1/2 -translate-y-1/2 left-1/2 top-1/2">
              <svg className="fill-error-600 dark:fill-error-500" width="38" height="38" viewBox="0 0 38 38" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path fillRule="evenodd" clipRule="evenodd" d="M9.62684 11.7496C9.04105 11.1638 9.04105 10.2141 9.62684 9.6283C10.2126 9.04252 11.1624 9.04252 11.7482 9.6283L18.9985 16.8786L26.2485 9.62851C26.8343 9.04273 27.7841 9.04273 28.3699 9.62851C28.9556 10.2143 28.9556 11.164 28.3699 11.7498L21.1198 18.9999L28.3699 26.25C28.9556 26.8358 28.9556 27.7855 28.3699 28.3713C27.7841 28.9571 26.8343 28.9571 26.2485 28.3713L18.9985 21.1212L11.7482 28.3715C11.1624 28.9573 10.2126 28.9573 9.62684 28.3715C9.04105 27.7857 9.04105 26.836 9.62684 26.2502L16.8771 18.9999L9.62684 11.7496Z" fill="" />
              </svg>
            </span>
          </div>
          <h4 className="mb-3 text-2xl font-semibold text-gray-800 dark:text-white/90 sm:text-title-sm">
            Error al registrar
          </h4>
          <p className="text-base leading-6 text-gray-500 dark:text-gray-400">
            {errorMessage ?? "Ocurrió un error inesperado. Intenta nuevamente."}
          </p>
          <div className="flex items-center justify-center w-full gap-3 mt-7">
            <button
              type="button"
              onClick={errorModal.closeModal}
              className="flex justify-center w-full px-4 py-3 text-sm font-medium text-white rounded-lg bg-error-500 shadow-theme-xs hover:bg-error-600 sm:w-auto"
            >
              Cerrar
            </button>
          </div>
        </div>
      </Modal>
    </div>
  );
};
