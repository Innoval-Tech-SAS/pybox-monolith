import { type NodeProps } from "@xyflow/react";
import { GitBranch, Plus, Trash2 } from "lucide-react";
import { Input } from "@/ui/components/inputs/input";
import { useIvrEditor } from "@/ivr/hooks/use-ivr-editor";
import { caseHandleId, createId, HANDLE_IDS } from "@/ivr/utils/ivr-utils";
import {
  CONDITION_BUILTIN_VARIABLES,
  type ConditionCase,
  type ConditionNode as ConditionNodeType,
} from "@/ivr/types/ivr-node-types";
import { IvrNodeShell, type SourceHandleDef } from "./ivr-node-shell";
import { ActionSelector } from "../action-selector";

/**
 * Nodo "Condición" (→ `condition` de Helena): bifurca automáticamente según el
 * valor de una variable de sesión o built-in, sin intervención del cliente.
 *
 * ⚠️ EXPERIMENTAL: el motor de Helena todavía no lo tiene validado, así que no
 * se ofrece en la paleta (ver `constants/experimental-nodes.ts`). El componente
 * existe para que un flujo que lo contenga se pueda abrir y editar.
 */
export const ConditionNode: React.FC<NodeProps<ConditionNodeType>> = ({ id, data, selected }) => {
  const { updateNodeData, takeSnapshot, removeHandleEdges, entryNodeId, setEntryNode } =
    useIvrEditor();

  const sourceHandles: SourceHandleDef[] = [
    ...data.cases
      .filter((c) => c.action.kind === "goto")
      .map((c) => ({ id: caseHandleId(c.id), label: c.value || "?" })),
    ...(data.onDefault.kind === "goto"
      ? [{ id: HANDLE_IDS.onDefault, label: "Si no coincide" }]
      : []),
  ];

  const updateCase = (caseId: string, patch: Partial<ConditionCase>) => {
    updateNodeData(id, {
      cases: data.cases.map((c) => (c.id === caseId ? { ...c, ...patch } : c)),
    });
  };

  const addCase = () => {
    takeSnapshot();
    const newCase: ConditionCase = {
      id: createId(),
      value: "",
      action: { kind: "hangup" },
    };
    updateNodeData(id, { cases: [...data.cases, newCase] });
  };

  const removeCase = (caseId: string) => {
    takeSnapshot();
    removeHandleEdges(id, caseHandleId(caseId));
    updateNodeData(id, { cases: data.cases.filter((c) => c.id !== caseId) });
  };

  return (
    <IvrNodeShell
      icon={<GitBranch size={16} />}
      title="Condición"
      accent="bg-purple-50 text-purple-700 dark:bg-purple-500/10 dark:text-purple-300"
      selected={!!selected}
      sourceHandles={sourceHandles}
      isEntry={entryNodeId === id}
      onMarkEntry={() => setEntryNode(id)}
    >
      <span className="rounded-md bg-warning-50 px-2 py-1 text-[10px] font-medium text-warning-700 dark:bg-warning-500/15 dark:text-warning-400">
        Experimental: sin validar contra Helena
      </span>

      <label className="flex flex-col gap-1">
        <span className="font-medium text-gray-600 dark:text-gray-300">Variable a evaluar</span>
        <Input
          value={data.variable}
          onChange={(e) => updateNodeData(id, { variable: e.target.value })}
          placeholder="amd_status"
          className="h-9! py-1.5!"
        />
        <span className="text-[10px] leading-snug text-gray-400 dark:text-gray-500">
          Built-in: {CONDITION_BUILTIN_VARIABLES.map((v) => v.value).join(", ")}. También
          sirve cualquier variable capturada por un nodo Captura.
        </span>
      </label>

      <div className="flex flex-col gap-2">
        {data.cases.map((c) => (
          <div
            key={c.id}
            className="flex flex-col gap-2 rounded-lg border border-gray-200 p-2 dark:border-gray-700"
          >
            <div className="flex items-center gap-2">
              <Input
                value={c.value}
                onChange={(e) => updateCase(c.id, { value: e.target.value })}
                placeholder="Valor (ej. HUMAN)"
                className="h-9! py-1.5!"
              />
              <button
                type="button"
                onClick={() => removeCase(c.id)}
                title="Quitar rama"
                className="rounded p-1.5 text-gray-400 hover:bg-error-50 hover:text-error-500"
              >
                <Trash2 size={14} />
              </button>
            </div>
            <ActionSelector
              nodeId={id}
              label="Entonces"
              handleId={caseHandleId(c.id)}
              value={c.action}
              onChange={(action) => updateCase(c.id, { action })}
            />
          </div>
        ))}

        <button
          type="button"
          onClick={addCase}
          className="flex items-center justify-center gap-1.5 rounded-lg border border-dashed border-gray-300 py-1.5 text-[11px] font-medium text-gray-500 hover:border-brand-300 hover:text-brand-600 dark:border-gray-600 dark:text-gray-400"
        >
          <Plus size={13} />
          Agregar rama
        </button>
      </div>

      <ActionSelector
        nodeId={id}
        label="Si no coincide ninguna"
        handleId={HANDLE_IDS.onDefault}
        value={data.onDefault}
        onChange={(action) => updateNodeData(id, { onDefault: action })}
      />
    </IvrNodeShell>
  );
};
