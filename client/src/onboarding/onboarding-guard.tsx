import React from "react";
import { OnboardingModal } from "./onboarding-modal";
import { useOnboardingStatus } from "@/hooks/use-onboarding-status";
import { Loader } from "@/ui/components/loader/loader";

interface Props {
  children: React.ReactNode;
}

export const OnboardingGuard: React.FC<Props> = ({ children }) => {
  const { status, loading, refetch } = useOnboardingStatus();

  if (loading) {
    return (
      <div className="flex items-center justify-center w-full h-screen">
        <Loader />
      </div>
    );
  }

  if (status && !status.isComplete) {
    return <OnboardingModal isOpen={true} status={status} onComplete={refetch} />;
  }

  return <>{children}</>;
};
