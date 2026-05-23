import type {
  OnboardingStatus,
  OnboardingStep,
} from "@/types/onboarding/onboarding-types";

export const buildOnboardingSteps = (
  status: OnboardingStatus,
): OnboardingStep[] => {
  const steps: OnboardingStep[] = [];
  if (!status.emailVerified) steps.push("email");
  if (!status.phoneVerified) steps.push("phone");
  if (!status.documentComplete) steps.push("profile");
  if (status.orgComplete === false) steps.push("organization");
  return steps;
};
