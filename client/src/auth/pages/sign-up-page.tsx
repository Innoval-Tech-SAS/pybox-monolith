import { AuthLayout } from "../components/auth-layout";
import { SignUpForm } from "../components/sign-up-form";
import { PageMeta } from "../../ui/pages/page-meta";

export const SignUpPage: React.FC = () => {
  return (
    <>
      <PageMeta title="Crear cuenta" description="Regístrate para acceder" />
      <AuthLayout>
        <SignUpForm />
      </AuthLayout>
    </>
  );
};
