import { useState } from "react";
import { Link, useNavigate } from "react-router";
import { AuthLayout } from "../components/auth-layout";
import { PageMeta } from "@/ui/pages/page-meta";
import { useForgotPassword, type Channel, type LookupResult } from "../hooks/use-forgot-password";
import { ForgotPasswordStep1 } from "../components/forgot-password-step-1";
import { ForgotPasswordStep2 } from "../components/forgot-password-step-2";
import { ForgotPasswordStep3 } from "../components/forgot-password-step-3";
import { ForgotPasswordStep4 } from "../components/forgot-password-step-4";
import type { ForgotPasswordStep as Step } from "../constants/forgot-password-steps";
import { FORGOT_PASSWORD_STEP_TITLES as STEP_TITLES, FORGOT_PASSWORD_STEP_SUBTITLES as STEP_SUBTITLES } from "../constants/forgot-password-steps";

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
                <ForgotPasswordStep1 onNext={handleLookup} loading={loading} />
              )}
              {step === 2 && lookupResult && (
                <ForgotPasswordStep2
                  lookup={lookupResult}
                  docType={docType}
                  docNumber={docNumber}
                  onNext={(ch) => { setChannel(ch); setStep(3); }}
                  loading={loading}
                />
              )}
              {step === 3 && (
                <ForgotPasswordStep3
                  docType={docType}
                  docNumber={docNumber}
                  channel={channel}
                  onNext={(code) => { setVerifiedCode(code); setStep(4); }}
                  loading={loading}
                />
              )}
              {step === 4 && (
                <ForgotPasswordStep4
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
