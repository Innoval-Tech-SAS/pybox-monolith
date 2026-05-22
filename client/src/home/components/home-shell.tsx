import { homeToneClasses } from "../constants/home-tone-classes";
import type { HomeShellProps } from "@/types/props/home-props";

export const HomeShell: React.FC<HomeShellProps> = ({
  eyebrow,
  title,
  description,
  metrics,
  actions,
}) => {
  return (
    <main className="bg-gray-50 px-4 py-6 dark:bg-gray-950 sm:px-6 lg:px-8">
      <div className="mx-auto flex w-full max-w-7xl flex-col gap-6">
        <header className="flex flex-col gap-5 rounded-lg border border-gray-200 bg-white p-5 shadow-theme-xs dark:border-gray-800 dark:bg-gray-900 lg:flex-row lg:items-end lg:justify-between">
          <div className="max-w-3xl">
            <p className="mb-2 text-theme-xs font-semibold uppercase text-brand-500 dark:text-brand-400">
              {eyebrow}
            </p>
            <h1 className="text-title-sm font-semibold text-gray-800 dark:text-white/90">
              {title}
            </h1>
            <p className="mt-2 max-w-2xl text-sm text-gray-500 dark:text-gray-400">
              {description}
            </p>
          </div>
        </header>

        <section className="grid gap-4 md:grid-cols-3">
          {metrics.map((metric) => (
            <article
              key={metric.label}
              className="rounded-lg border border-gray-200 bg-white p-5 shadow-theme-xs dark:border-gray-800 dark:bg-gray-900"
            >
              <span
                className={`inline-flex rounded-full px-2.5 py-1 text-theme-xs font-medium ${homeToneClasses[metric.tone]}`}
              >
                {metric.label}
              </span>
              <p className="mt-4 text-title-sm font-semibold text-gray-800 dark:text-white/90">
                {metric.value}
              </p>
              <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                {metric.helper}
              </p>
            </article>
          ))}
        </section>

        <section className="grid gap-4 lg:grid-cols-2">
          {actions.map((action) => (
            <article
              key={action.title}
              className="flex gap-4 rounded-lg border border-gray-200 bg-white p-5 shadow-theme-xs dark:border-gray-800 dark:bg-gray-900"
            >
              <div
                className={`flex size-11 shrink-0 items-center justify-center rounded-lg ${homeToneClasses[action.tone]}`}
              >
                {action.icon}
              </div>
              <div>
                <h2 className="text-base font-semibold text-gray-800 dark:text-white/90">
                  {action.title}
                </h2>
                <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                  {action.description}
                </p>
              </div>
            </article>
          ))}
        </section>
      </div>
    </main>
  );
};
