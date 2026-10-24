import { CheckCircle } from "lucide-react";
import type { CreateUserStepDef } from "@/users/types/create-user-step-def";

export const CreateUserStepSidebar: React.FC<{ steps: CreateUserStepDef[]; current: number }> = ({ steps, current }) => (
  <div className="flex flex-col gap-0">
    {steps.map((s, i) => {
      const n = i + 1;
      const done = n < current;
      const active = n === current;
      return (
        <div key={n} className="flex gap-4">
          <div className="flex flex-col items-center">
            <div
              className={`flex size-9 shrink-0 items-center justify-center rounded-full border-2 text-sm font-semibold transition-all ${
                done
                  ? "border-brand-500 bg-brand-500 text-white"
                  : active
                    ? "border-brand-500 bg-white text-brand-600 dark:bg-gray-900"
                    : "border-gray-200 bg-white text-gray-400 dark:border-gray-700 dark:bg-gray-900"
              }`}
            >
              {done ? <CheckCircle size={16} /> : s.icon}
            </div>
            {i < steps.length - 1 && (
              <div
                className={`w-px flex-1 min-h-10 my-1 transition-colors ${
                  done ? "bg-brand-500" : "bg-gray-200 dark:bg-gray-700"
                }`}
              />
            )}
          </div>
          <div className="pb-8">
            <p
              className={`text-sm font-semibold leading-9 ${
                active
                  ? "text-gray-800 dark:text-white/90"
                  : done
                    ? "text-brand-600 dark:text-brand-400"
                    : "text-gray-400 dark:text-gray-600"
              }`}
            >
              {s.label}
            </p>
            <p
              className={`text-xs -mt-1 ${
                active || done ? "text-gray-500 dark:text-gray-400" : "text-gray-300 dark:text-gray-700"
              }`}
            >
              {s.description}
            </p>
          </div>
        </div>
      );
    })}
  </div>
);
