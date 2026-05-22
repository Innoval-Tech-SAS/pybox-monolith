import React from "react";
import { useAuthGuard } from "@/hooks/use-auth-guard";
import { OnboardingGuard } from "@/onboarding/onboarding-guard";
import { AdminLayout } from "@/ui/layouts/admin-layout";

export const ProtectedRoute: React.FC = () => {
  useAuthGuard();

  return (
    <OnboardingGuard>
      <AdminLayout />
    </OnboardingGuard>
  );
};
