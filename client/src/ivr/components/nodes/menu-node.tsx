import { type NodeProps } from "@xyflow/react";
import { ListTree, Plus, X } from "lucide-react";
import { Switch } from "@/ui/components/switch";
import { Select } from "@/ui/components/inputs/select";
import { useIvrEditor } from "@/ivr/hooks/use-ivr-editor";
import { HANDLE_IDS, digitHandleId, createId } from "@/ivr/utils/ivr-utils";
import type {
  MenuNode as MenuNodeType,
  MenuDigit,
  DigitKey,
  IvrAction,
} from "@/ivr/types/ivr-node-types";
import { IvrNodeShell, type SourceHandleDef } from "./ivr-node-shell";
import { AudioPickerField } from "./audio-picker-field";
import { ActionSelector } from "../action-selector";

const DIGIT_KEYS: DigitKey[] = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "*", "#"];

/**
 * Nodo "Menú": reproduce un audio y enruta según el dígito marcado. Los dígitos
 * se agregan de uno en uno (numeración lógica desde 1); timeout e inválido son
 * excepciones configurables. Cada acción "Ir a nodo" genera su propio handle.
 */
export const MenuNode: React.FC<NodeProps<MenuNodeType>> = ({ id, data, selected }) => {
  const { updateNodeData, takeSnapshot, removeHandleEdges, entryNodeId, setEntryNode } =
    useIvrEditor();

  const setDigits = (next: MenuDigit[]) => updateNodeData(id, { digits: next });

  const addDigit = () => {
    takeSnapshot();
    const nid = createId();
    const digit: MenuDigit = {
      id: nid,
      key: "",
      action: { kind: "goto", handleId: digitHandleId(nid) },
    };
    setDigits([...data.digits, digit]);
  };

  const removeDigit = (did: string) => {
    takeSnapshot();
    removeHandleEdges(id, digitHandleId(did));
    setDigits(data.digits.filter((d) => d.id !== did));
  };

  const changeKey = (did: string, key: DigitKey) => {
    takeSnapshot();
    setDigits(data.digits.map((d) => (d.id === did ? { ...d, key } : d)));
  };

  const changeAction = (did: string, action: IvrAction) =>
    setDigits(data.digits.map((d) => (d.id === did ? { ...d, action } : d)));

  const sourceHandles: SourceHandleDef[] = [
    ...data.digits
      .filter((d) => d.action.kind === "goto")
      .map((d) => ({ id: digitHandleId(d.id), label: `Tecla ${d.key || "?"}` })),
    ...(data.onTimeout.kind === "goto" ? [{ id: HANDLE_IDS.onTimeout, label: "Timeout" }] : []),
    ...(data.onInvalid.kind === "goto" ? [{ id: HANDLE_IDS.onInvalid, label: "Inválido" }] : []),
  ];

  return (
    <IvrNodeShell
      icon={<ListTree size={16} />}
      title="Menú"
      accent="bg-orange-50 text-orange-700 dark:bg-orange-500/10 dark:text-orange-300"
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

      <div className="flex flex-col gap-2">
        <div className="flex items-center justify-between">
          <span className="font-medium text-gray-600 dark:text-gray-300">Opciones (dígitos)</span>
          <button
            type="button"
            onClick={addDigit}
            className="inline-flex items-center gap-1 rounded-md bg-brand-500 px-2 py-1 text-[10px] font-medium text-white hover:bg-brand-600"
          >
            <Plus size={11} /> Agregar
          </button>
        </div>

        {data.digits.length === 0 && (
          <span className="text-[10px] text-gray-400 dark:text-gray-500">
            Sin opciones aún. Agrega un dígito.
          </span>
        )}

        {data.digits.map((digit, index) => (
          <div
            key={digit.id}
            className="flex flex-col gap-1.5 rounded-lg border border-gray-200 p-2 dark:border-gray-700"
          >
            <div className="flex items-center justify-between">
              <span className="text-[10px] font-semibold text-gray-500 dark:text-gray-400">
                Opción {index + 1}
              </span>
              <button
                type="button"
                onClick={() => removeDigit(digit.id)}
                className="text-gray-400 hover:text-error-500"
                aria-label="Eliminar opción"
              >
                <X size={13} />
              </button>
            </div>
            <Select
              options={DIGIT_KEYS.map((k) => ({ value: k, label: k }))}
              value={digit.key}
              placeholder="Tecla"
              onChange={(v) => changeKey(digit.id, v as DigitKey)}
              className="h-9! py-1.5!"
            />
            <ActionSelector
              nodeId={id}
              label="Acción"
              handleId={digitHandleId(digit.id)}
              value={digit.action}
              allowRepeat
              onChange={(action) => changeAction(digit.id, action)}
            />
          </div>
        ))}
      </div>

      <ActionSelector
        nodeId={id}
        label="Si no marca nada (timeout)"
        handleId={HANDLE_IDS.onTimeout}
        value={data.onTimeout}
        allowRepeat
        onChange={(action) => updateNodeData(id, { onTimeout: action })}
      />

      <ActionSelector
        nodeId={id}
        label="Si marca un dígito inválido"
        handleId={HANDLE_IDS.onInvalid}
        value={data.onInvalid}
        allowRepeat
        onChange={(action) => updateNodeData(id, { onInvalid: action })}
      />
    </IvrNodeShell>
  );
};
