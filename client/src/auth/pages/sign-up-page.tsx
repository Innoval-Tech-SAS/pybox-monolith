import { useState } from "react";
import { AuthLayout } from "../components/auth-layout";
import { SignUpForm } from "../components/sign-up-form";
import { PageMeta } from "../../ui/pages/page-meta";
import { RegisterMode, REGISTER_PANEL } from "../../types/auth/register-mode";

export const SignUpPage: React.FC = () => {
  const [mode, setMode] = useState<RegisterMode>("user");
  const panel = REGISTER_PANEL[mode];

  const rightPanel = (
    <div className="flex flex-col items-start max-w-sm px-8">
      <span className="inline-flex items-center gap-2 px-3 py-1 mb-7 text-xs font-medium text-gray-500 border border-gray-200 rounded-full bg-white/80 shadow-theme-xs dark:border-white/10 dark:bg-white/5 dark:text-white/60">
        {panel.badge}
      </span>
      <h2 className="mb-5 text-3xl font-bold leading-tight tracking-normal text-gray-900 dark:text-white/90">
        {panel.title}{" "}
        <span className="text-brand-600 dark:text-brand-400">{panel.highlight}</span>
      </h2>
      <p className="mb-8 text-base leading-7 text-gray-600 dark:text-gray-300">
        {panel.description}
      </p>
      <div className="flex gap-3">
        <span className="h-20 w-7 rounded-lg border border-gray-200 bg-white/80 shadow-theme-xs dark:border-white/10 dark:bg-white/5" />
        <span className="h-20 w-7 rounded-lg border border-gray-200 bg-white/80 shadow-theme-xs dark:border-white/10 dark:bg-white/5" />
        <span className="h-20 w-7 rounded-lg border border-gray-200 bg-white/80 shadow-theme-xs dark:border-white/10 dark:bg-white/5" />
      </div>
    </div>
  );

  return (
    <>
      <PageMeta title="Crear cuenta" description="Regístrate para acceder" />
      <AuthLayout rightPanel={rightPanel}>
        <SignUpForm mode={mode} onModeChange={setMode} />
      </AuthLayout>
    </>
  );
};
