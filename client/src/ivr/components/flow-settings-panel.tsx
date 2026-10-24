import { Modal } from "@/ui/components/modal/modal";
import { useContactPolicies } from "@/ivr/hooks/use-contact-policies";
import { Input } from "@/ui/components/inputs/input";
import { Select } from "@/ui/components/inputs/select";
import { Switch } from "@/ui/components/switch";
import type { IvrDefaults, IvrPacing, IvrRedial } from "@/ivr/types/ivr-node-types";
import {
  AMD_FIELDS,
  AMD_PRESET_OPTIONS,
  type AmdPreset,
  type AmdVariables,
} from "@/ivr/constants/amd-presets";

type FlowSettingsPanelProps = {
  isOpen: boolean;
  onClose: () => void;
  defaults: IvrDefaults;
  redial: IvrRedial;
  pacing: IvrPacing;
  amdPreset: AmdPreset;
  amd: AmdVariables;
  onDefaultsChange: (next: IvrDefaults) => void;
  onRedialChange: (next: IvrRedial) => void;
  onPacingChange: (next: IvrPacing) => void;
  onAmdPresetChange: (preset: AmdPreset) => void;
  onAmdVariableChange: (key: keyof AmdVariables, value: string) => void;
};

/** `""` en el input se guarda como `null` (usa el default de Helena). */
const parseOptionalInt = (raw: string): number | null => {
  const trimmed = raw.trim();
  if (!trimmed) return null;
  const n = Number(trimmed);
  return Number.isFinite(n) && n > 0 ? Math.floor(n) : null;
};

/**
 * Ajustes a nivel de flujo: valores por defecto de captura DTMF (compilan a
 * `defaults` de Helena) y remarcado automático (compila a `redialConfig`).
 */
export const FlowSettingsPanel: React.FC<FlowSettingsPanelProps> = ({
  isOpen,
  onClose,
  defaults,
  redial,
  pacing,
  amdPreset,
  amd,
  onDefaultsChange,
  onRedialChange,
  onPacingChange,
  onAmdPresetChange,
  onAmdVariableChange,
}) => {
  const { policies, loading: loadingPolicies } = useContactPolicies();

  return (
  <Modal isOpen={isOpen} onClose={onClose} className="m-4 max-h-[85vh] max-w-md overflow-y-auto custom-scrollbar p-6">
    <h4 className="mb-1 text-lg font-semibold text-gray-800 dark:text-white/90">
      Ajustes del flujo
    </h4>
    <p className="mb-5 text-sm text-gray-500 dark:text-gray-400">
      Valores por defecto de los nodos, remarcado y detección de contestadora (AMD).
    </p>

    <div className="flex flex-col gap-4 text-sm">
      <div className="grid grid-cols-2 gap-3">
        <label className="flex flex-col gap-1">
          <span className="font-medium text-gray-600 dark:text-gray-300">Timeout DTMF (ms)</span>
          <Input
            type="number"
            min="1000"
            step={500}
            value={String(defaults.dtmfTimeoutMs)}
            onChange={(e) =>
              onDefaultsChange({
                ...defaults,
                dtmfTimeoutMs: Math.max(1000, Number(e.target.value) || 1000),
              })
            }
          />
        </label>
        <label className="flex flex-col gap-1">
          <span className="font-medium text-gray-600 dark:text-gray-300">Máx. reintentos</span>
          <Input
            type="number"
            min="0"
            value={String(defaults.maxRetries)}
            onChange={(e) =>
              onDefaultsChange({
                ...defaults,
                maxRetries: Math.max(0, Number(e.target.value) || 0),
              })
            }
          />
        </label>
      </div>

      <Switch
        checked={defaults.interruptible}
        onChange={(v) => onDefaultsChange({ ...defaults, interruptible: v })}
        label="Audios interrumpibles por defecto"
      />

      <div className="border-t border-gray-100 pt-4 dark:border-gray-800">
        <p className="mb-3 font-medium text-gray-700 dark:text-gray-200">Remarcado automático</p>
        <div className="grid grid-cols-2 gap-3">
          <label className="flex flex-col gap-1">
            <span className="font-medium text-gray-600 dark:text-gray-300">Intentos (1 = sin redial)</span>
            <Input
              type="number"
              min="1"
              value={String(redial.maxAttempts)}
              onChange={(e) =>
                onRedialChange({ ...redial, maxAttempts: Math.max(1, Number(e.target.value) || 1) })
              }
            />
          </label>
          <label className="flex flex-col gap-1">
            <span className="font-medium text-gray-600 dark:text-gray-300">Espera entre intentos (s)</span>
            <Input
              type="number"
              min="0"
              value={String(redial.retryDelaySeconds)}
              onChange={(e) =>
                onRedialChange({
                  ...redial,
                  retryDelaySeconds: Math.max(0, Number(e.target.value) || 0),
                })
              }
            />
          </label>
        </div>
      </div>

      <div className="border-t border-gray-100 pt-4 dark:border-gray-800">
        <p className="mb-3 font-medium text-gray-700 dark:text-gray-200">Ritmo de marcación</p>
        <div className="grid grid-cols-2 gap-3">
          <label className="flex flex-col gap-1">
            <span className="font-medium text-gray-600 dark:text-gray-300">Llamadas / seg</span>
            <Input
              type="number"
              min="1"
              placeholder="Default de Helena"
              value={pacing.callsPerSecond === null ? "" : String(pacing.callsPerSecond)}
              onChange={(e) =>
                onPacingChange({ ...pacing, callsPerSecond: parseOptionalInt(e.target.value) })
              }
            />
          </label>
          <label className="flex flex-col gap-1">
            <span className="font-medium text-gray-600 dark:text-gray-300">Máx. simultáneas</span>
            <Input
              type="number"
              min="1"
              placeholder="Default de Helena"
              value={pacing.maxConcurrent === null ? "" : String(pacing.maxConcurrent)}
              onChange={(e) =>
                onPacingChange({ ...pacing, maxConcurrent: parseOptionalInt(e.target.value) })
              }
            />
          </label>
        </div>
        <label className="mt-3 flex flex-col gap-1">
          <span className="font-medium text-gray-600 dark:text-gray-300">Caller ID</span>
          <Input
            placeholder="Opcional"
            value={pacing.callerId}
            onChange={(e) => onPacingChange({ ...pacing, callerId: e.target.value })}
          />
        </label>
        <label className="mt-3 flex flex-col gap-1">
          <span className="font-medium text-gray-600 dark:text-gray-300">
            Política de contacto
          </span>
          <Select
            options={[
              { value: "", label: loadingPolicies ? "Cargando…" : "Sin restricción horaria" },
              ...policies.map((p) => ({
                value: p.id,
                label: p.country ? `${p.name} (${p.country})` : p.name,
              })),
            ]}
            value={pacing.contactPolicyId}
            onChange={(v) => onPacingChange({ ...pacing, contactPolicyId: v })}
          />
          <span className="text-[10px] leading-snug text-gray-400 dark:text-gray-500">
            Restringe las franjas horarias en que Helena puede marcar. Las llamadas
            bloqueadas por la política se reportan como fuera de horario.
          </span>
        </label>

        <p className="mt-2 text-[11px] text-gray-400 dark:text-gray-500">
          Vacío = Helena usa su propio ritmo/caller ID por defecto. El cambio aplica al
          próximo bulk despachado; no afecta a los que ya están en curso.
        </p>
      </div>

      <div className="border-t border-gray-100 pt-4 dark:border-gray-800">
        <p className="mb-3 font-medium text-gray-700 dark:text-gray-200">
          Detección de contestadora (AMD)
        </p>
        <label className="mb-3 flex flex-col gap-1">
          <span className="font-medium text-gray-600 dark:text-gray-300">Preset</span>
          <Select
            options={AMD_PRESET_OPTIONS.map((p) => ({ value: p, label: p }))}
            value={amdPreset}
            onChange={(v) => onAmdPresetChange(v as AmdPreset)}
          />
        </label>
        <div className="grid grid-cols-2 gap-2">
          {AMD_FIELDS.map(([key, label]) => (
            <label key={key} className="flex flex-col gap-1">
              <span className="text-[11px] leading-tight text-gray-500 dark:text-gray-400">
                {label}
              </span>
              <Input
                type="number"
                min="0"
                value={amd[key] ?? ""}
                onChange={(e) => onAmdVariableChange(key, e.target.value)}
              />
            </label>
          ))}
        </div>
        <p className="mt-2 text-[11px] text-gray-400 dark:text-gray-500">
          Estos valores se envían a Helena en <code>variables</code> para calibrar la detección
          de humano/contestadora.
        </p>
      </div>
    </div>
  </Modal>
  );
};
