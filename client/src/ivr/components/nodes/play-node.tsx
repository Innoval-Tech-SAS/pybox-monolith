import { type NodeProps } from "@xyflow/react";
import { Play } from "lucide-react";
import { Switch } from "@/ui/components/switch";
import { useIvrEditor } from "@/ivr/hooks/use-ivr-editor";
import { HANDLE_IDS } from "@/ivr/utils/ivr-utils";
import type { PlayNode as PlayNodeType } from "@/ivr/types/ivr-node-types";
import { IvrNodeShell, type SourceHandleDef } from "./ivr-node-shell";
import { AudioPickerField } from "./audio-picker-field";
import { ActionSelector } from "../action-selector";

/**
 * Nodo "Reproducir" (→ playback de Helena): reproduce un audio y, al terminar,
 * cuelga o salta a otro nodo. No ofrece "Repetir" (evitaría un loop sin salida).
 */
export const PlayNode: React.FC<NodeProps<PlayNodeType>> = ({ id, data, selected }) => {
  const { updateNodeData, takeSnapshot, entryNodeId, setEntryNode } = useIvrEditor();

  const sourceHandles: SourceHandleDef[] =
    data.onFinish.kind === "goto" ? [{ id: HANDLE_IDS.onFinish, label: "Siguiente" }] : [];

  return (
    <IvrNodeShell
      icon={<Play size={16} />}
      title="Reproducir"
      accent="bg-brand-50 text-brand-700 dark:bg-brand-500/10 dark:text-brand-300"
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

      <ActionSelector
        nodeId={id}
        label="Al finalizar el audio"
        handleId={HANDLE_IDS.onFinish}
        value={data.onFinish}
        onChange={(action) => updateNodeData(id, { onFinish: action })}
      />
    </IvrNodeShell>
  );
};
