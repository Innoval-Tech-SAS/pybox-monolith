import React, { useCallback } from "react";
import { OnboardingModal } from "./onboarding-modal";
import { useOnboardingStatus } from "@/hooks/use-onboarding-status";
import { useSession } from "@/auth/hooks/use-session";
import { Loader } from "@/ui/components/loader/loader";
import { Alert } from "@/ui/components/alert/alert";
import { Button } from "@/ui/components/button/button";
import type { OnboardingGuardProps } from "@/types/props/onboarding-props";

export const OnboardingGuard: React.FC<OnboardingGuardProps> = ({ children }) => {
  const { status, loading, error, refetch } = useOnboardingStatus();
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

  // Fail-closed: si no se pudo confirmar el estado de onboarding, no se asume
  // "completo" solo porque `status` quedó en null — se bloquea el acceso y se
  // ofrece reintentar en vez de dejar pasar (ver use-onboarding-status.ts).
  if (error) {
    return (
      <div className="flex items-center justify-center w-full h-full p-4">
        <div className="w-full max-w-sm space-y-4">
          <Alert
            variant="error"
            title="No se pudo verificar tu perfil"
            message="Ocurrió un error al confirmar el estado de tu registro. Reintenta para continuar."
          />
          <Button className="w-full" onClick={() => refetch()}>
            Reintentar
          </Button>
        </div>
      </div>
    );
  }

  if (status && !status.isComplete) {
    return <OnboardingModal isOpen={true} status={status} onComplete={handleComplete} />;
  }

  return <>{children}</>;
};
