import { useState, useEffect } from "react";
import { useNavigate } from "react-router";

import { AuthForm } from "../components/auth-form";
import { AuthLayout } from "../components/auth-layout";
import { PageMeta } from "../../ui/pages/page-meta";
import { Loader } from "@/ui/components/loader/loader";

export const AuthPage: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const userLogged = sessionStorage.getItem("user");
    if (userLogged) {
      navigate("/home", { replace: true });
    } else {
      setLoading(false);
    }
  }, [navigate]);

  return (
    <>
      <PageMeta
        title="Iniciar sesión"
        description="Inicia sesión en tu cuenta"
      />
      {loading ? (
        <div className="flex items-center justify-center w-full h-screen">
          <Loader />
        </div>
      ) : (
        <AuthLayout>
          <AuthForm />
        </AuthLayout>
      )}
    </>
  );
};
