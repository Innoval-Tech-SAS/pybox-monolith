import { Info } from "lucide-react";
import type { CalendarLegendProps } from "@/types/props/calendar-legend-props";
import { getCreditTypeStyle } from "@/constants/credits/financial-calendar";

/** Leyenda de colores del calendario, un punto por tipo de obligación. */
export const CalendarLegend: React.FC<CalendarLegendProps> = ({ creditTypes }) => {
  if (creditTypes.length === 0) return null;

  return (
    <div className="border-t border-gray-200 px-4 py-3 dark:border-gray-800">
      <ul className="flex flex-wrap items-center gap-x-5 gap-y-2">
        {creditTypes.map((type) => (
          <li key={type.value} className="flex items-center gap-2">
            <span className={`size-2 shrink-0 rounded-full ${getCreditTypeStyle(type.value).dotClass}`} />
            <span className="text-xs text-gray-600 dark:text-gray-400">{type.label}</span>
          </li>
        ))}
      </ul>
      <p className="mt-2.5 flex items-center gap-1.5 text-xs text-gray-400 dark:text-gray-500">
        <Info size={13} className="shrink-0" />
        Tus obligaciones están distribuidas en diferentes entidades.
      </p>
    </div>
  );
};
