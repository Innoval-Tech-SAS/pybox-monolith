import { MAIN_TABLES } from "@/reports/constants/report.constants";
import type { StepBasicInfoProps } from "@/reports/types/step-basic-info-props";

export const StepBasicInfo: React.FC<StepBasicInfoProps> = ({ state, update }) => (
  <div className="space-y-5">
    <div>
      <label className="mb-1 block text-sm font-medium text-gray-700 dark:text-gray-300">
        Nombre *
      </label>
      <input
        type="text"
        value={state.name}
        onChange={(e) => update({ name: e.target.value })}
        placeholder="Ej. Deudores con métodos de contacto activos"
        className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2.5 text-sm text-gray-700 outline-none transition focus:border-brand-500 focus:ring-1 focus:ring-brand-500 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-300 dark:placeholder-gray-500"
      />
    </div>

    <div>
      <label className="mb-1 block text-sm font-medium text-gray-700 dark:text-gray-300">
        Descripción
      </label>
      <textarea
        rows={2}
        value={state.description}
        onChange={(e) => update({ description: e.target.value })}
        placeholder="Descripción opcional del reporte"
        className="w-full resize-none rounded-lg border border-gray-300 bg-white px-3 py-2.5 text-sm text-gray-700 outline-none transition focus:border-brand-500 focus:ring-1 focus:ring-brand-500 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-300 dark:placeholder-gray-500"
      />
    </div>

    <div>
      <label className="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300">
        Tabla principal *
      </label>
      <p className="mb-3 text-xs text-gray-400 dark:text-gray-500">
        Define el tipo de entidad central del reporte. Las demás tablas se unirán a esta.
      </p>
      <div className="grid grid-cols-2 gap-3">
        {MAIN_TABLES.map((t) => (
          <button
            key={t.name}
            type="button"
            onClick={() =>
              update({
                mainTable: t.name,
                mainTableColumns: [],
                mainTableFilters: [],
                additionalTables: [],
                joins: [],
              })
            }
            className={`rounded-xl border-2 py-4 text-sm font-medium transition-colors ${
              state.mainTable === t.name
                ? "border-brand-500 bg-brand-50 text-brand-700 dark:bg-brand-500/10 dark:text-brand-400"
                : "border-gray-200 bg-white text-gray-600 hover:border-gray-300 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-400"
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>
    </div>
  </div>
);
