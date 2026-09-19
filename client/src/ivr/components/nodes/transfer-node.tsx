import { type NodeProps } from "@xyflow/react";
import { PhoneForwarded } from "lucide-react";
import { Input } from "@/ui/components/inputs/input";
import { useIvrEditor } from "@/ivr/hooks/use-ivr-editor";
import { HANDLE_IDS, isValidEndpoint } from "@/ivr/utils/ivr-utils";
import type { TransferNode as TransferNodeType } from "@/ivr/types/ivr-node-types";
import { IvrNodeShell, type SourceHandleDef } from "./ivr-node-shell";
import { ActionSelector } from "../action-selector";

/**
 * Nodo "Transferir": transfiere a un endpoint SIP `protocolo/servidor/extension`.
 * "Transferencia completada" (→ on_finish) no ofrece "Repetir".
 */
export const TransferNode: React.FC<NodeProps<TransferNodeType>> = ({ id, data, selected }) => {
  const { updateNodeData, entryNodeId, setEntryNode } = useIvrEditor();

  const endpointError = data.endpoint.trim() !== "" && !isValidEndpoint(data.endpoint);

  const sourceHandles: SourceHandleDef[] = [
    ...(data.onNoAnswer.kind === "goto" ? [{ id: HANDLE_IDS.onNoAnswer, label: "No contesta" }] : []),
    ...(data.onCompleted.kind === "goto" ? [{ id: HANDLE_IDS.onCompleted, label: "Completada" }] : []),
  ];

  return (
    <IvrNodeShell
      icon={<PhoneForwarded size={16} />}
      title="Transferir"
      accent="bg-warning-50 text-warning-700 dark:bg-warning-500/10 dark:text-warning-300"
      selected={!!selected}
      sourceHandles={sourceHandles}
      isEntry={entryNodeId === id}
      onMarkEntry={() => setEntryNode(id)}
    >
      <label className="flex flex-col gap-1">
        <span className="font-medium text-gray-600 dark:text-gray-300">Endpoint SIP</span>
        <Input
          value={data.endpoint}
          onChange={(e) => updateNodeData(id, { endpoint: e.target.value })}
          placeholder="SIP/SERVIDOR/6428"
          error={endpointError}
          className="h-9! py-1.5!"
        />
        <span
          className={`text-[10px] ${endpointError ? "text-error-500" : "text-gray-400 dark:text-gray-500"}`}
        >
          Formato: protocolo/servidor/extension
        </span>
      </label>

      <label className="flex flex-col gap-1">
        <span className="font-medium text-gray-600 dark:text-gray-300">Tiempo de ring (ms)</span>
        <Input
          type="number"
          min="1000"
          step={1000}
          value={String(data.timeoutMs)}
          onChange={(e) =>
            updateNodeData(id, { timeoutMs: Math.max(1000, Number(e.target.value) || 1000) })
          }
          className="h-9! py-1.5!"
        />
      </label>

      <ActionSelector
        nodeId={id}
        label="Si no contesta"
        handleId={HANDLE_IDS.onNoAnswer}
        value={data.onNoAnswer}
        allowRepeat
        onChange={(action) => updateNodeData(id, { onNoAnswer: action })}
      />

      <ActionSelector
        nodeId={id}
        label="Si se completa"
        handleId={HANDLE_IDS.onCompleted}
        value={data.onCompleted}
        onChange={(action) => updateNodeData(id, { onCompleted: action })}
      />
    </IvrNodeShell>
  );
};
