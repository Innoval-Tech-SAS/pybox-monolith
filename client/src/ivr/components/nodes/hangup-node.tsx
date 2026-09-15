import { type NodeProps } from "@xyflow/react";
import { PhoneOff } from "lucide-react";
import { Input } from "@/ui/components/inputs/input";
import { useIvrEditor } from "@/ivr/hooks/use-ivr-editor";
import type { HangupNode as HangupNodeType } from "@/ivr/types/ivr-node-types";
import { IvrNodeShell } from "./ivr-node-shell";

/**
 * Nodo "Colgar" (→ `hangup` de Helena): nodo terminal al que pueden llegar
 * varias flechas. Colgar ya se puede hacer como *acción* dentro de cualquier
 * desenlace; este nodo existe para que el final de la llamada sea un punto
 * visible y con nombre en el lienzo, y para poder etiquetar ese desenlace en
 * el panel de resultados.
 *
 * ⚠️ EXPERIMENTAL: el motor de Helena todavía no lo tiene validado, así que no
 * se ofrece en la paleta (ver `constants/experimental-nodes.ts`).
 */
export const HangupNode: React.FC<NodeProps<HangupNodeType>> = ({ id, data, selected }) => {
  const { updateNodeData, entryNodeId, setEntryNode } = useIvrEditor();

  return (
    <IvrNodeShell
      icon={<PhoneOff size={16} />}
      title="Colgar"
      accent="bg-gray-100 text-gray-700 dark:bg-gray-700/40 dark:text-gray-200"
      selected={!!selected}
      // Nodo terminal: no tiene salidas.
      sourceHandles={[]}
      isEntry={entryNodeId === id}
      onMarkEntry={() => setEntryNode(id)}
    >
      <span className="rounded-md bg-warning-50 px-2 py-1 text-[10px] font-medium text-warning-700 dark:bg-warning-500/15 dark:text-warning-400">
        Experimental: sin validar contra Helena
      </span>

      <label className="flex flex-col gap-1">
        <span className="font-medium text-gray-600 dark:text-gray-300">Motivo</span>
        <Input
          value={data.reason}
          onChange={(e) => updateNodeData(id, { reason: e.target.value })}
          placeholder="HANGUP"
          className="h-9! py-1.5!"
        />
        <span className="text-[10px] text-gray-400 dark:text-gray-500">
          Queda en <code>ivrEndReason</code> y es la clave que se etiqueta en Resultados.
        </span>
      </label>
    </IvrNodeShell>
  );
};
