import React, { useEffect } from "react";
import { useNavigate } from "react-router";
import { AdminLayout } from "@/ui/layouts/admin-layout";
import { isJwtExpired } from "@/utils/token-utils";

export const ProtectedRoute: React.FC = () => {
  const navigate = useNavigate();
  const token = sessionStorage.getItem("accessToken");
  const userLogged = sessionStorage.getItem("user");
  const isValid = !!token && token.startsWith("eyJ") && !!userLogged && !isJwtExpired(token);

  useEffect(() => {
    if (!isValid) {
      sessionStorage.clear();
      navigate("/admin/sign-in", { replace: true });
    }
  }, [isValid, navigate]);

  if (!isValid) return null;

  return <AdminLayout />;
};
