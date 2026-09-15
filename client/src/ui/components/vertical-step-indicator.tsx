import type { VerticalStepIndicatorProps } from "@/types/props/vertical-step-indicator-props";

export const VerticalStepIndicator: React.FC<VerticalStepIndicatorProps> = ({ steps, current }) => (
  <ol className="flex shrink-0 flex-row gap-3 overflow-x-auto lg:w-56 lg:flex-col lg:gap-0 lg:overflow-visible">
    {steps.map((step, i) => (
      <li key={step.title} className="flex flex-1 flex-col gap-2 lg:flex-row lg:gap-3">
        <div className="flex items-center gap-2 lg:flex-col lg:items-center lg:gap-0">
          <div
            className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-xs font-semibold transition-colors ${
              i < current
                ? "bg-brand-500 text-white"
                : i === current
                  ? "border-2 border-brand-500 bg-white text-brand-600 dark:bg-gray-900 dark:text-brand-400"
                  : "border-2 border-gray-200 bg-white text-gray-400 dark:border-gray-700 dark:bg-gray-900"
            }`}
          >
            {i < current ? (
              <svg className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                <path
                  fillRule="evenodd"
                  d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                  clipRule="evenodd"
                />
              </svg>
            ) : (
              i + 1
            )}
          </div>
          {i < steps.length - 1 && (
            <div
              className={`hidden lg:block lg:w-px lg:flex-1 lg:my-1 ${
                i < current ? "bg-brand-500" : "bg-gray-200 dark:bg-gray-700"
              }`}
            />
          )}
        </div>
        <div className="lg:pb-3">
          <p
            className={`text-sm font-semibold ${
              i <= current ? "text-gray-800 dark:text-white/90" : "text-gray-400 dark:text-gray-500"
            }`}
          >
            {step.title}
          </p>
          <p className="hidden text-xs text-gray-400 dark:text-gray-500 lg:block">{step.description}</p>
        </div>
      </li>
    ))}
  </ol>
);
