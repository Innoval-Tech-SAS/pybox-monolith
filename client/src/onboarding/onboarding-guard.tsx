import React, { useCallback } from "react";
import { OnboardingModal } from "./onboarding-modal";
import { useOnboardingStatus } from "@/hooks/use-onboarding-status";
import { useSession } from "@/auth/hooks/use-session";
import { Loader } from "@/ui/components/loader/loader";
import type { OnboardingGuardProps } from "@/types/props/onboarding-props";

export const OnboardingGuard: React.FC<OnboardingGuardProps> = ({ children }) => {
  const { status, loading, refetch } = useOnboardingStatus();
  const { refetch: refetchSession } = useSession();

  const handleComplete = useCallback(async () => {
    await refetchSession();
    await refetch();
  }, [refetchSession, refetch]);

  if (loading) {
    return (
      <div className="flex items-center justify-center w-full h-full">
        <Loader />
      </div>
    );
  }

  if (status && !status.isComplete) {
    return <OnboardingModal isOpen={true} status={status} onComplete={handleComplete} />;
  }

  return <>{children}</>;
};
