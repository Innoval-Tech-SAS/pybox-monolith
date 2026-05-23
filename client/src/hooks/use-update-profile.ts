import { useState } from "react";
import { useApiClient } from "./use-api-client";
import { UpdateProfileRequest } from "@/types/onboarding/onboarding-types";

export const useUpdateProfile = () => {
  const { apiClient } = useApiClient();
  const [loading, setLoading] = useState(false);

  const updateProfile = async (data: UpdateProfileRequest) => {
    setLoading(true);
    try {
      await apiClient("/onboarding/profile", {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });
    } finally {
      setLoading(false);
    }
  };

  return { updateProfile, loading };
};
