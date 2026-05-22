import React from "react";
import { OnboardingModal } from "./onboarding-modal";
import { useOnboardingStatus } from "@/hooks/use-onboarding-status";

interface Props {
  children: React.ReactNode;
}

export const OnboardingGuard: React.FC<Props> = ({ children }) => {
  const { status, loading, refetch } = useOnboardingStatus();

  const showModal = !loading && !!status && !status.isComplete;

  return (
    <>
      {children}
      {showModal && (
        <OnboardingModal isOpen={true} status={status!} onComplete={refetch} />
      )}
    </>
  );
};
