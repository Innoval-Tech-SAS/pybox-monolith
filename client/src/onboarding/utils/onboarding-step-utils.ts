import type {
  OnboardingStatus,
  OnboardingStep,
} from "@/types/onboarding/onboarding-types";

export const buildOnboardingSteps = (
  status: OnboardingStatus,
): OnboardingStep[] => {
  const steps: OnboardingStep[] = [];
  if (status.mustChangePassword) steps.push("set_password");
  if (!status.emailVerified) steps.push("email");
  if (!status.phoneSet) steps.push("set_phone");
  if (!status.phoneVerified) steps.push("phone");
  if (!status.documentComplete) steps.push("profile");
  if (status.orgComplete === false) steps.push("organization");
  if (status.identityVerificationStatus === "NO_ENVIADO") steps.push("identity");
  return steps;
};
