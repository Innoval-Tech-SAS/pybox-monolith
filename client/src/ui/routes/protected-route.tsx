import React, { useEffect } from "react";
import { useNavigate } from "react-router";
import { OnboardingGuard } from "@/onboarding/onboarding-guard";
import { AdminLayout } from "@/ui/layouts/admin-layout";

export const ProtectedRoute: React.FC = () => {
  const navigate = useNavigate();
  const token = sessionStorage.getItem("accessToken");
  const userLogged = sessionStorage.getItem("user");
  const isValid = !!token && token.startsWith("eyJ") && !!userLogged;

  useEffect(() => {
    if (!isValid) {
      sessionStorage.clear();
      navigate("/admin/sign-in", { replace: true });
    }
  }, [isValid, navigate]);

  if (!isValid) return null;

  return (
    <OnboardingGuard>
      <AdminLayout />
    </OnboardingGuard>
  );
};
