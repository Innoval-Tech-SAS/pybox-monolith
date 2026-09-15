import { getSession } from "@/auth/utils/auth-session-utils";
import { formatTodayLong, PORTFOLIO_DASHBOARD_SUBTITLE } from "../utils/greeting-utils";
import { getFirstName } from "../utils/home-session-utils";
import { OrgPortfoliosSection } from "./org-portfolios-section";

export const OrganizationUserHome: React.FC = () => {
  const session = getSession();
  const orgs = Object.entries(session?.orgs ?? {});
  const firstName = getFirstName(session);

  return (
    <section className="flex flex-1 min-h-0 flex-col overflow-y-auto custom-scrollbar rounded-2xl bg-gray-50 px-4 py-6 dark:bg-gray-950 sm:px-6 lg:px-8">
      <div className="mx-auto flex w-full max-w-7xl flex-col gap-6">
        <header className="rounded-lg border border-gray-200 bg-white p-5 shadow-theme-xs dark:border-gray-800 dark:bg-gray-900">
          <p className="mb-2 text-theme-xs font-semibold uppercase text-brand-500 dark:text-brand-400">
            {formatTodayLong()}
          </p>
          <h1 className="text-title-sm font-semibold text-gray-800 dark:text-white/90">
            {firstName ? `Hola, ${firstName}` : "Hola"}
          </h1>
          <p className="mt-2 max-w-2xl text-sm text-gray-500 dark:text-gray-400">
            {PORTFOLIO_DASHBOARD_SUBTITLE}
          </p>
        </header>

        {orgs.length === 0 ? (
          <p className="py-12 text-center text-sm text-gray-400 dark:text-gray-500">
            No tienes acceso a ninguna organización todavía.
          </p>
        ) : (
          orgs.map(([organizationId]) => (
            <OrgPortfoliosSection key={organizationId} organizationId={organizationId} />
          ))
        )}
      </div>
    </section>
  );
};
