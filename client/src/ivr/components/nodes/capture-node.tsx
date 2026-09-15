import { type NodeProps } from "@xyflow/react";
import { Keyboard } from "lucide-react";
import { Switch } from "@/ui/components/switch";
import { Input } from "@/ui/components/inputs/input";
import { Select } from "@/ui/components/inputs/select";
import { useIvrEditor } from "@/ivr/hooks/use-ivr-editor";
import { HANDLE_IDS } from "@/ivr/utils/ivr-utils";
import type { CaptureNode as CaptureNodeType, DigitKey } from "@/ivr/types/ivr-node-types";
import { IvrNodeShell, type SourceHandleDef } from "./ivr-node-shell";
import { AudioPickerField } from "./audio-picker-field";
import { ActionSelector } from "../action-selector";

const FINISH_KEYS: DigitKey[] = ["#", "*", "0"];

/**
 * Nodo "Captura" (→ collect de Helena): reproduce un audio y captura N dígitos
 * hasta una tecla de fin o timeout, guardándolos en una variable de sesión.
 * "Captura completa" (→ on_complete) no ofrece "Repetir".
 */
export const CaptureNode: React.FC<NodeProps<CaptureNodeType>> = ({ id, data, selected }) => {
  const { updateNodeData, takeSnapshot, entryNodeId, setEntryNode } = useIvrEditor();

  const sourceHandles: SourceHandleDef[] = [
    ...(data.onTimeout.kind === "goto" ? [{ id: HANDLE_IDS.onTimeout, label: "Timeout" }] : []),
    ...(data.onCompleted.kind === "goto" ? [{ id: HANDLE_IDS.onCompleted, label: "Completada" }] : []),
  ];

  return (
    <IvrNodeShell
      icon={<Keyboard size={16} />}
      title="Captura"
      accent="bg-success-50 text-success-700 dark:bg-success-500/10 dark:text-success-300"
      selected={!!selected}
      sourceHandles={sourceHandles}
      isEntry={entryNodeId === id}
      onMarkEntry={() => setEntryNode(id)}
    >
      <AudioPickerField nodeId={id} audioLabel={data.audioLabel} />

      <Switch
        checked={data.interruptible}
        onChange={(v) => {
          takeSnapshot();
          updateNodeData(id, { interruptible: v });
        }}
        label="Interrumpible"
      />

      <label className="flex flex-col gap-1">
        <span className="font-medium text-gray-600 dark:text-gray-300">Variable de sesión</span>
        <Input
          value={data.variable}
          onChange={(e) => updateNodeData(id, { variable: e.target.value })}
          placeholder="ej. cedula"
          className="h-9! py-1.5!"
        />
      </label>

      <div className="grid grid-cols-3 gap-2">
        <label className="flex flex-col gap-1">
          <span className="font-medium text-gray-600 dark:text-gray-300"># dígitos</span>
          <Input
            type="number"
            min="1"
            value={String(data.numDigits)}
            onChange={(e) =>
              updateNodeData(id, { numDigits: Math.max(1, Number(e.target.value) || 1) })
            }
            className="h-9! py-1.5!"
          />
        </label>
        <label className="flex flex-col gap-1">
          <span className="font-medium text-gray-600 dark:text-gray-300">Tecla fin</span>
          <Select
            options={FINISH_KEYS.map((k) => ({ value: k, label: k }))}
            value={data.finishKey}
            onChange={(v) => updateNodeData(id, { finishKey: v as DigitKey })}
            className="h-9! py-1.5!"
          />
        </label>
        <label className="flex flex-col gap-1">
          <span className="font-medium text-gray-600 dark:text-gray-300">Timeout (s)</span>
          <Input
            type="number"
            min="1"
            value={String(data.timeoutSeconds)}
            onChange={(e) =>
              updateNodeData(id, { timeoutSeconds: Math.max(1, Number(e.target.value) || 1) })
            }
            className="h-9! py-1.5!"
          />
        </label>
      </div>

      <ActionSelector
        nodeId={id}
        label="Si no responde (timeout)"
        handleId={HANDLE_IDS.onTimeout}
        value={data.onTimeout}
        allowRepeat
        onChange={(action) => updateNodeData(id, { onTimeout: action })}
      />

      <ActionSelector
        nodeId={id}
        label="Captura completa"
        handleId={HANDLE_IDS.onCompleted}
        value={data.onCompleted}
        onChange={(action) => updateNodeData(id, { onCompleted: action })}
      />
    </IvrNodeShell>
  );
};
