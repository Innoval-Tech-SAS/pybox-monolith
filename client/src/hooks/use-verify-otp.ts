import { useState } from "react";
import { useApiClient } from "./use-api-client";
import { VerificationChannel } from "@/types/onboarding/onboarding-types";

export const useVerifyOtp = () => {
  const { apiClient } = useApiClient();
  const [loading, setLoading] = useState(false);

  const requestOtp = async (channel: VerificationChannel) => {
    setLoading(true);
    try {
      await apiClient("/onboarding/request-otp", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ channel }),
      });
    } finally {
      setLoading(false);
    }
  };

  const verifyOtp = async (channel: VerificationChannel, code: string) => {
    setLoading(true);
    try {
      await apiClient("/onboarding/verify-otp", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ channel, code }),
      });
    } finally {
      setLoading(false);
    }
  };

  return { requestOtp, verifyOtp, loading };
};
