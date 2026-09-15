import type { TooltipProps } from "@/types/props/tooltip-props";

export const Tooltip: React.FC<TooltipProps> = ({ content, children, position = "top" }) => {
  const isTop = position === "top";

  return (
    <div className="group relative inline-block">
      {children}
      <div
        className={`invisible absolute left-1/2 z-10 -translate-x-1/2 opacity-0 transition-opacity duration-300 group-hover:visible group-hover:opacity-100 ${
          isTop ? "bottom-full mb-2.5" : "top-full mt-2.5"
        }`}
      >
        <div className="relative">
          <div className="drop-shadow-4xl rounded-lg bg-white px-3 py-2 text-xs font-medium whitespace-nowrap text-gray-700 dark:bg-[#1E2634] dark:text-white">
            {content}
          </div>
          <div
            className={`absolute left-1/2 h-3 w-4 -translate-x-1/2 rotate-45 bg-white dark:bg-[#1E2634] ${
              isTop ? "-bottom-1" : "-top-1"
            }`}
          />
        </div>
      </div>
    </div>
  );
};
