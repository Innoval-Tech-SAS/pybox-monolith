import { useState } from "react";
import { Link, useNavigate } from "react-router";
import { AuthLayout } from "../components/auth-layout";
import { Input } from "@/ui/components/inputs/input";
import { Label } from "@/ui/components/inputs/label";
import { Select } from "@/ui/components/inputs/select";
import { OtpInput } from "@/ui/components/inputs/otp-input";
import { EyeCloseIcon, EyeIcon } from "@/ui/icons";
import { PageMeta } from "@/ui/pages/page-meta";
import { useToast } from "@/context/toast-context";
import { useForgotPassword, type Channel, type LookupResult } from "../hooks/use-forgot-password";
import { DOCUMENT_TYPE_GROUPS } from "@/constants/countries/doc-type-labels";

// ── Paso 1: Ingresar documento ────────────────────────────────────────────────

const Step1: React.FC<{
  onNext: (docType: string, docNumber: string, result: LookupResult) => void;
  loading: boolean;
}> = ({ onNext, loading }) => {
  const { lookup } = useForgotPassword();
  const [documentType, setDocumentType] = useState("CC");
  const [documentNumber, setDocumentNumber] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const result = await lookup(documentType, documentNumber);
    if (result) onNext(documentType, documentNumber, result);
  };

  return (
    <form onSubmit={handleSubmit}>
      <div className="space-y-5">
        <div>
          <label className="mb-1.5 block text-sm text-gray-500">
            Tipo de documento <span className="text-error-500">*</span>
          </label>
          <Select
            groups={DOCUMENT_TYPE_GROUPS}
            value={documentType}
            placeholder="Seleccionar tipo"
            onChange={setDocumentType}
          />
        </div>
        <div>
          <Label className="text-gray-500">
            Número de documento <span className="text-error-500">*</span>
          </Label>
          <Input
            type="text"
            placeholder="Número de documento"
            value={documentNumber}
            onChange={(e) => setDocumentNumber(e.target.value)}
            required
          />
        </div>
        <button
          type="submit"
          disabled={loading || !documentNumber}
          className="flex w-full items-center justify-center rounded-lg bg-brand-500 px-4 py-3 text-sm font-medium text-white transition hover:bg-brand-600 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? "Buscando..." : "Continuar"}
        </button>
      </div>
    </form>
  );
};

// ── Paso 2: Elegir canal ──────────────────────────────────────────────────────

const Step2: React.FC<{
  lookup: LookupResult;
  docType: string;
  docNumber: string;
  onNext: (channel: Channel) => void;
  loading: boolean;
}> = ({ lookup, docType, docNumber, onNext, loading }) => {
  const { sendCode } = useForgotPassword();
  const [channel, setChannel] = useState<Channel>("EMAIL");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const ok = await sendCode(docType, docNumber, channel);
    if (ok) onNext(channel);
  };

  return (
    <form onSubmit={handleSubmit}>
      <div className="space-y-5">
        <div className="rounded-lg border border-gray-100 bg-gray-50 px-4 py-3 dark:border-gray-800 dark:bg-gray-800/50">
          <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">Cuenta encontrada</p>
          {lookup.maskedEmail && (
            <p className="text-sm font-medium text-gray-700 dark:text-gray-300">{lookup.maskedEmail}</p>
          )}
          {lookup.maskedPhone && (
            <p className="text-sm font-medium text-gray-700 dark:text-gray-300">{lookup.maskedPhone}</p>
          )}
        </div>

        <div>
          <Label className="text-gray-500">¿Dónde enviamos el código?</Label>
          <div className="mt-2 flex gap-2">
            {(["EMAIL", "SMS"] as Channel[]).map((ch) => {
              const available = ch === "EMAIL" ? !!lookup.maskedEmail : !!lookup.maskedPhone;
              return (
                <button
                  key={ch}
                  type="button"
                  disabled={!available}
                  onClick={() => setChannel(ch)}
                  className={`flex-1 rounded-lg border px-4 py-2.5 text-sm font-medium transition-colors disabled:opacity-40 disabled:cursor-not-allowed ${
                    channel === ch && available
                      ? "border-brand-500 bg-brand-500 text-white"
                      : "border-gray-300 bg-white text-gray-700 hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-gray-700"
                  }`}
                >
                  {ch === "EMAIL" ? "Correo electrónico" : "SMS"}
                </button>
              );
            })}
          </div>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="flex w-full items-center justify-center rounded-lg bg-brand-500 px-4 py-3 text-sm font-medium text-white transition hover:bg-brand-600 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? "Enviando..." : "Enviar código"}
        </button>
      </div>
    </form>
  );
};

// ── Paso 3: Validar código ────────────────────────────────────────────────────

const Step3: React.FC<{
  docType: string;
  docNumber: string;
  channel: Channel;
  onNext: (code: string) => void;
  loading: boolean;
}> = ({ docType, docNumber, channel, onNext, loading }) => {
  const { verifyCode } = useForgotPassword();
  const [digits, setDigits] = useState<string[]>(Array(6).fill(""));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const code = digits.join("");
    const ok = await verifyCode(docType, docNumber, code, channel);
    if (ok) onNext(code);
  };

  return (
    <form onSubmit={handleSubmit}>
      <div className="space-y-5">
        <div>
          <Label className="text-gray-500 mb-2 block">
            Código enviado por {channel === "EMAIL" ? "correo electrónico" : "SMS"}
          </Label>
          <OtpInput value={digits} onChange={setDigits} disabled={loading} />
        </div>
        <button
          type="submit"
          disabled={loading || digits.join("").length < 6}
          className="flex w-full items-center justify-center rounded-lg bg-brand-500 px-4 py-3 text-sm font-medium text-white transition hover:bg-brand-600 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? "Verificando..." : "Verificar código"}
        </button>
      </div>
    </form>
  );
};

// ── Paso 4: Nueva contraseña ──────────────────────────────────────────────────

const Step4: React.FC<{
  docType: string;
  docNumber: string;
  code: string;
  channel: Channel;
  onSuccess: () => void;
  loading: boolean;
}> = ({ docType, docNumber, code, channel, onSuccess, loading }) => {
  const { resetPassword } = useForgotPassword();
  const { error: toastError } = useToast();
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showNew, setShowNew] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (newPassword !== confirmPassword) {
      toastError("Error", "Las contraseñas no coinciden.");
      return;
    }
    const ok = await resetPassword(docType, docNumber, code, channel, newPassword);
    if (ok) onSuccess();
  };

  return (
    <form onSubmit={handleSubmit}>
      <div className="space-y-5">
        <div>
          <Label className="text-gray-500">
            Nueva contraseña <span className="text-error-500">*</span>
          </Label>
          <div className="relative">
            <Input
              type={showNew ? "text" : "password"}
              placeholder="Nueva contraseña"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              required
            />
            <span onClick={() => setShowNew(!showNew)} className="absolute z-30 -translate-y-1/2 cursor-pointer right-4 top-1/2">
              {showNew ? <EyeIcon className="fill-gray-500 size-5" /> : <EyeCloseIcon className="fill-gray-500 size-5" />}
            </span>
          </div>
        </div>
        <div>
          <Label className="text-gray-500">
            Confirmar contraseña <span className="text-error-500">*</span>
          </Label>
          <div className="relative">
            <Input
              type={showConfirm ? "text" : "password"}
              placeholder="Confirmar contraseña"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
            />
            <span onClick={() => setShowConfirm(!showConfirm)} className="absolute z-30 -translate-y-1/2 cursor-pointer right-4 top-1/2">
              {showConfirm ? <EyeIcon className="fill-gray-500 size-5" /> : <EyeCloseIcon className="fill-gray-500 size-5" />}
            </span>
          </div>
        </div>
        <button
          type="submit"
          disabled={loading || !newPassword}
          className="flex w-full items-center justify-center rounded-lg bg-brand-500 px-4 py-3 text-sm font-medium text-white transition hover:bg-brand-600 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? "Guardando..." : "Restablecer contraseña"}
        </button>
      </div>
    </form>
  );
};

// ── Page ──────────────────────────────────────────────────────────────────────

type Step = 1 | 2 | 3 | 4;

const STEP_TITLES: Record<Step, string> = {
  1: "Recuperar contraseña",
  2: "Elige cómo recibir el código",
  3: "Verifica el código",
  4: "Nueva contraseña",
};

const STEP_SUBTITLES: Record<Step, string> = {
  1: "Ingresa tu tipo y número de documento para encontrar tu cuenta.",
  2: "Encontramos tu cuenta. Elige dónde enviamos el código.",
  3: "Ingresa el código que recibiste para verificar tu identidad.",
  4: "Código verificado. Ahora elige tu nueva contraseña.",
};

export const ForgotPasswordPage: React.FC = () => {
  const navigate = useNavigate();
  const { loading } = useForgotPassword();
  const [step, setStep] = useState<Step>(1);
  const [docType, setDocType] = useState("");
  const [docNumber, setDocNumber] = useState("");
  const [lookupResult, setLookupResult] = useState<LookupResult | null>(null);
  const [channel, setChannel] = useState<Channel>("EMAIL");
  const [verifiedCode, setVerifiedCode] = useState("");

  const handleLookup = (dt: string, dn: string, result: LookupResult) => {
    setDocType(dt);
    setDocNumber(dn);
    setLookupResult(result);
    setStep(2);
  };

  return (
    <>
      <PageMeta title="Recuperar contraseña" description="Restablece tu contraseña" />
      <AuthLayout>
        <div className="flex flex-col flex-1">
          <div className="flex flex-col justify-center flex-1 w-full max-w-md mx-auto">
            <div>
              <div className="mb-5 sm:mb-8">
                <div className="mb-3 flex items-center gap-2">
                  {step > 1 && step < 4 && (
                    <button
                      type="button"
                      onClick={() => setStep((s) => (s - 1) as Step)}
                      className="text-sm text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
                    >
                      ← Atrás
                    </button>
                  )}
                  <span className="ml-auto text-xs text-gray-400">Paso {step} de 4</span>
                </div>
                <h1 className="mb-1 font-semibold text-brand-500 text-title-sm dark:text-white/90 sm:text-title-md">
                  {STEP_TITLES[step]}
                </h1>
                <p className="text-sm text-gray-500 dark:text-gray-400">{STEP_SUBTITLES[step]}</p>
              </div>

              {step === 1 && (
                <Step1 onNext={handleLookup} loading={loading} />
              )}
              {step === 2 && lookupResult && (
                <Step2
                  lookup={lookupResult}
                  docType={docType}
                  docNumber={docNumber}
                  onNext={(ch) => { setChannel(ch); setStep(3); }}
                  loading={loading}
                />
              )}
              {step === 3 && (
                <Step3
                  docType={docType}
                  docNumber={docNumber}
                  channel={channel}
                  onNext={(code) => { setVerifiedCode(code); setStep(4); }}
                  loading={loading}
                />
              )}
              {step === 4 && (
                <Step4
                  docType={docType}
                  docNumber={docNumber}
                  code={verifiedCode}
                  channel={channel}
                  onSuccess={() => navigate("/admin/sign-in")}
                  loading={loading}
                />
              )}

              <div className="mt-6 text-center">
                <Link to="/admin/sign-in" className="text-sm text-brand-500 hover:text-brand-600 dark:text-brand-400">
                  Volver al inicio de sesión
                </Link>
              </div>
            </div>
          </div>
        </div>
      </AuthLayout>
    </>
  );
};
