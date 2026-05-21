import React from "react";
import { OnboardingModal } from "./onboarding-modal";
import { useOnboardingStatus } from "@/hooks/use-onboarding-status";

interface Props {
  children: React.ReactNode;
}

export const OnboardingGuard: React.FC<Props> = ({ children }) => {
  const { status, loading, refetch } = useOnboardingStatus();

  if (loading || !status) return null;

  if (!status.isComplete) {
    return (
      <>
        {children}
        <OnboardingModal
          isOpen={true}
          status={status}
          onComplete={refetch}
        />
      </>
    );
  }

  return <>{children}</>;
};
