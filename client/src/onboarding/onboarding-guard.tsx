import React, { useCallback } from "react";
import { OnboardingModal } from "./onboarding-modal";
import { useOnboardingStatus } from "@/hooks/use-onboarding-status";
import { useAuth } from "@/hooks/use-auth";
import { setSessionUser } from "@/auth/utils/auth-session-utils";
import { Loader } from "@/ui/components/loader/loader";
import type { OnboardingGuardProps } from "@/types/props/onboarding-props";

export const OnboardingGuard: React.FC<OnboardingGuardProps> = ({ children }) => {
  const { status, loading, refetch } = useOnboardingStatus();
  const { fetchMe } = useAuth();

  const handleComplete = useCallback(async () => {
    const me = await fetchMe().catch(() => null);
    if (me) setSessionUser(me);
    await refetch();
  }, [fetchMe, refetch]);

  if (loading) {
    return (
      <div className="flex items-center justify-center w-full h-screen">
        <Loader />
      </div>
    );
  }

  if (status && !status.isComplete) {
    return <OnboardingModal isOpen={true} status={status} onComplete={handleComplete} />;
  }

  return <>{children}</>;
};
