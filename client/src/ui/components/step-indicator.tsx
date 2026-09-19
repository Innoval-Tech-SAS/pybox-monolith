import React from "react";
import type { StepIndicatorProps } from "@/types/props/step-indicator-props";

export const StepIndicator: React.FC<StepIndicatorProps> = ({ current, total }) => (
  <div className="flex items-center justify-center mb-6">
    {Array.from({ length: total }).map((_, i) => (
      <React.Fragment key={i}>
        <div
          className={`flex h-8 w-8 items-center justify-center rounded-full text-xs font-semibold transition-colors ${
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
        {i < total - 1 && (
          <div
            className={`h-px w-12 transition-colors ${
              i < current ? "bg-brand-500" : "bg-gray-200 dark:bg-gray-700"
            }`}
          />
        )}
      </React.Fragment>
    ))}
  </div>
);
