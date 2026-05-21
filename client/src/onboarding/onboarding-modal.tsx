import React, { useState } from "react";
import { Modal } from "@/ui/components/modal/modal";
import { VerifyChannelStep } from "./steps/verify-channel-step";
import { UpdateProfileStep } from "./steps/update-profile-step";
import { OrganizationStep } from "./steps/organization-step";
import { useVerifyOtp } from "@/hooks/use-verify-otp";
import { OnboardingStatus } from "@/types/onboarding/onboarding-types";

interface Props {
  isOpen: boolean;
  status: OnboardingStatus;
  onComplete: () => void;
}

type Step = "email" | "phone" | "profile" | "organization";

function buildSteps(status: OnboardingStatus): Step[] {
  const steps: Step[] = [];
  if (!status.emailVerified) steps.push("email");
  if (!status.phoneVerified) steps.push("phone");
  if (!status.documentComplete) steps.push("profile");
  if (status.orgComplete === false) steps.push("organization");
  return steps;
}

const STEP_LABELS: Record<Step, string> = {
  email: "Verificar email",
  phone: "Verificar teléfono",
  profile: "Documento",
  organization: "Organización",
};

export const OnboardingModal: React.FC<Props> = ({ isOpen, status, onComplete }) => {
  const steps = buildSteps(status);
  const [stepIndex, setStepIndex] = useState(0);
  const { requestOtp, verifyOtp, loading, error, clearError } = useVerifyOtp();

  const currentStep = steps[stepIndex];
  const progress = Math.round((stepIndex / steps.length) * 100);

  const next = () => {
    if (stepIndex + 1 >= steps.length) {
      onComplete();
    } else {
      setStepIndex((i) => i + 1);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={() => {}} showCloseButton={false} className="max-w-md w-full p-8">
      {/* Progress */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs font-medium text-gray-500 dark:text-gray-400">
            Paso {stepIndex + 1} de {steps.length}
          </span>
          <span className="text-xs text-gray-400">{progress}%</span>
        </div>
        <div className="h-1.5 w-full rounded-full bg-gray-200 dark:bg-gray-700">
          <div
            className="h-1.5 rounded-full bg-brand-500 transition-all duration-300"
            style={{ width: `${progress}%` }}
          />
        </div>
        <div className="mt-3 flex gap-2">
          {steps.map((step, i) => (
            <span
              key={step}
              className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                i < stepIndex
                  ? "bg-success-100 text-success-700 dark:bg-success-900/30 dark:text-success-400"
                  : i === stepIndex
                    ? "bg-brand-100 text-brand-700 dark:bg-brand-900/30 dark:text-brand-400"
                    : "bg-gray-100 text-gray-500 dark:bg-gray-800 dark:text-gray-400"
              }`}
            >
              {STEP_LABELS[step]}
            </span>
          ))}
        </div>
      </div>

      {/* Step content */}
      {currentStep === "email" && (
        <VerifyChannelStep
          title="Verifica tu correo electrónico"
          description="Necesitamos confirmar que tienes acceso a tu correo."
          defaultChannel="EMAIL"
          onDone={next}
          requestOtp={requestOtp}
          verifyOtp={verifyOtp}
          loading={loading}
          error={error}
          clearError={clearError}
        />
      )}

      {currentStep === "phone" && (
        <VerifyChannelStep
          title="Verifica tu número de teléfono"
          description="Confirma que tienes acceso a tu número registrado."
          defaultChannel="SMS"
          onDone={next}
          requestOtp={requestOtp}
          verifyOtp={verifyOtp}
          loading={loading}
          error={error}
          clearError={clearError}
        />
      )}

      {currentStep === "profile" && <UpdateProfileStep onDone={next} />}

      {currentStep === "organization" && <OrganizationStep onDone={next} />}
    </Modal>
  );
};
