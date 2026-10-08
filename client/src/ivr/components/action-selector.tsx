import { Select } from "@/ui/components/inputs/select";
import { Input } from "@/ui/components/inputs/input";
import { useIvrEditor } from "@/ivr/hooks/use-ivr-editor";
import type { IvrAction, IvrActionKind } from "@/ivr/types/ivr-node-types";

type ActionSelectorProps = {
  nodeId: string;
  label: string;
  /** Id del handle de salida que se activa cuando la acción es "Ir a nodo". */
  handleId: string;
  value: IvrAction;
  /** "Repetir" solo se ofrece donde tiene sentido (no genera loop sin salida). */
  allowRepeat?: boolean;
  onChange: (action: IvrAction) => void;
};

/**
 * Selector de acción de un desenlace (fin de audio, dígito, timeout, etc.).
 * Al elegir "Ir a nodo" el nodo mostrará un handle de salida (`handleId`); al
 * cambiar a otra acción, se limpian las conexiones que colgaban de ese handle.
 * Para "Colgar llamada" se ofrece un motivo opcional (reportería en Helena).
 */
export const ActionSelector: React.FC<ActionSelectorProps> = ({
  nodeId,
  label,
  handleId,
  value,
  allowRepeat = false,
  onChange,
}) => {
  const { takeSnapshot, removeHandleEdges } = useIvrEditor();

  const options = [
    { value: "goto", label: "Ir a nodo" },
    { value: "hangup", label: "Colgar llamada" },
    ...(allowRepeat ? [{ value: "repeat", label: "Repetir" }] : []),
  ];

  const handleChange = (raw: string) => {
    const kind = raw as IvrActionKind;
    if (kind === value.kind) return;
    takeSnapshot();
    if (value.kind === "goto" && kind !== "goto") removeHandleEdges(nodeId, handleId);
    onChange({
      kind,
      handleId: kind === "goto" ? handleId : undefined,
      reason: kind === "hangup" ? value.reason : undefined,
    });
  };

  return (
    <label className="flex flex-col gap-1">
      <span className="font-medium text-gray-600 dark:text-gray-300">{label}</span>
      <Select
        options={options}
        value={value.kind}
        onChange={handleChange}
        className="h-9! py-1.5!"
      />
      {value.kind === "hangup" && (
        <Input
          value={value.reason ?? ""}
          onChange={(e) => onChange({ ...value, reason: e.target.value })}
          placeholder="Motivo (opcional)"
          className="h-9! py-1.5!"
        />
      )}
    </label>
  );
};
