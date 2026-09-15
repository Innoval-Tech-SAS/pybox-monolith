import { Input } from "@/ui/components/inputs/input";
import { Textarea } from "@/ui/components/inputs/textarea";
import type { StepBasicInfoProps } from "@/query-builder/types/step-basic-info-props";

export const StepBasicInfo: React.FC<StepBasicInfoProps> = ({ state, update, config }) => (
  <div className="space-y-5">
    <div>
      <label className="mb-1 block text-sm font-medium text-gray-700 dark:text-gray-300">
        Nombre *
      </label>
      <Input
        type="text"
        value={state.name}
        onChange={(e) => update({ name: e.target.value })}
        placeholder={config.copy.namePlaceholder}
      />
    </div>

    <div>
      <label className="mb-1 block text-sm font-medium text-gray-700 dark:text-gray-300">
        Descripción
      </label>
      <Textarea
        rows={2}
        value={state.description}
        onChange={(e) => update({ description: e.target.value })}
        placeholder={config.copy.descriptionPlaceholder}
        className="resize-none"
      />
    </div>

    <div>
      <label className="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300">
        Tabla principal *
      </label>
      <p className="mb-3 text-xs text-gray-400 dark:text-gray-500">
        Define el tipo de entidad central del {config.copy.entityNoun}. Las demás tablas se unirán a esta.
      </p>
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
        {config.mainTables.map((t) => (
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
