import type { AuthLayoutProps } from "@/types/props/auth-layout-props";
import { ThemeToggler } from "../../ui/components/menu/theme-toggler";

export const AuthLayout: React.FC<AuthLayoutProps> = ({
  children,
  rightPanel,
}) => {
  return (
    <div className="relative p-6 bg-white z-1 dark:bg-gray-900 sm:p-0">
      <div className="relative flex flex-col justify-center w-full h-screen overflow-hidden lg:flex-row dark:bg-gray-900 sm:p-0">
        {children}
        <div className="items-center hidden w-full h-full lg:w-1/2 bg-gradient-to-br from-gray-50 via-brand-25 to-brand-50 dark:from-gray-950 dark:via-gray-900 dark:to-brand-950/70 lg:grid">
          <div className="relative flex items-center justify-center z-1 px-12">
            {rightPanel ?? (
              <div className="flex flex-col items-start max-w-sm">
                <span className="inline-flex items-center gap-2 px-3 py-1 mb-7 text-xs font-medium text-gray-500 border border-gray-200 rounded-full bg-white/80 shadow-theme-xs dark:border-white/10 dark:bg-white/5 dark:text-white/60">
                  Experiencia cuidada al detalle
                </span>
                <h2 className="mb-5 text-3xl font-bold tracking-normal text-gray-900 dark:text-white/90">
                  Bienvenido a <span className="text-brand-600 dark:text-brand-400">Pybox</span>
                </h2>
                <p className="mb-8 text-base leading-7 text-gray-600 dark:text-gray-300">
                  Administra tus finanzas con elegancia y claridad. Interfaz minimalista, productividad maxima.
                </p>
                <div className="flex gap-3">
                  <span className="h-20 w-7 rounded-lg border border-gray-200 bg-white/80 shadow-theme-xs dark:border-white/10 dark:bg-white/5" />
                  <span className="h-20 w-7 rounded-lg border border-gray-200 bg-white/80 shadow-theme-xs dark:border-white/10 dark:bg-white/5" />
                  <span className="h-20 w-7 rounded-lg border border-gray-200 bg-white/80 shadow-theme-xs dark:border-white/10 dark:bg-white/5" />
                </div>
              </div>
            )}
          </div>
        </div>
        <div className="fixed z-50 hidden bottom-6 right-6 sm:block">
          <ThemeToggler />
        </div>
      </div>
    </div>
  );
};
