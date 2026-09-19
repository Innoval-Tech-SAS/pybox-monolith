import { Modal } from "@/ui/components/modal/modal";
import { Input } from "@/ui/components/inputs/input";
import { outcomeKeysForNode } from "@/ivr/utils/compile-flow";
import { NODE_LABELS } from "@/ivr/utils/ivr-utils";
import {
  CALL_LEVEL_NODE,
  CALL_LEVEL_OUTCOMES,
  type IvrNode,
  type IvrNodeType,
  type IvrOutcomeMap,
} from "@/ivr/types/ivr-node-types";

type OutcomesPanelProps = {
  isOpen: boolean;
  onClose: () => void;
  nodes: IvrNode[];
  outcomes: IvrOutcomeMap;
  onChange: (nodeId: string, key: string, label: string) => void;
};

const Row: React.FC<{
  outcomeKey: string;
  hint: string;
  value: string;
  onChange: (value: string) => void;
}> = ({ outcomeKey, hint, value, onChange }) => (
  <div className="grid grid-cols-1 gap-2 sm:grid-cols-2 sm:items-center">
    <div className="min-w-0">
      <p className="truncate text-sm text-gray-700 dark:text-gray-300">{hint}</p>
      <code className="text-xs text-gray-400 dark:text-gray-500">{outcomeKey}</code>
    </div>
    <Input
      value={value}
      onChange={(e) => onChange(e.target.value)}
      placeholder="Sin etiqueta"
    />
  </div>
);

/**
 * Edición de las etiquetas de resultado del flujo.
 *
 * Va en un panel propio y no dentro de cada tarjeta del lienzo: las claves de un
 * nodo dependen de sus acciones (qué teclas cuelgan, con qué motivo), así que
 * verlas todas juntas es lo que deja comprobar de un vistazo que no quedó ningún
 * desenlace sin etiquetar.
 */
export const OutcomesPanel: React.FC<OutcomesPanelProps> = ({
  isOpen,
  onClose,
  nodes,
  outcomes,
  onChange,
}) => {
  const nodesWithOutcomes = nodes
    .map((node, index) => ({ node, index, keys: outcomeKeysForNode(node) }))
    .filter((entry) => entry.keys.length > 0);

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      className="m-4 max-h-[85vh] max-w-2xl overflow-y-auto custom-scrollbar p-6"
    >
      <h4 className="mb-1 text-lg font-semibold text-gray-800 dark:text-white/90">
        Resultados de la llamada
      </h4>
      <p className="mb-5 text-sm text-gray-500 dark:text-gray-400">
        Ponle nombre de negocio a cada desenlace. Es lo que verás en el reporte de la campaña
        en vez del motivo técnico. Los desenlaces sin etiqueta igual se registran, solo que
        sin nombre.
      </p>

      <section className="mb-6">
        <h5 className="mb-1 text-sm font-semibold text-gray-800 dark:text-white/90">
          Antes de entrar al flujo
        </h5>
        <p className="mb-3 text-xs text-gray-500 dark:text-gray-400">
          Llamadas que nunca llegaron a reproducir el primer nodo.
        </p>
        <div className="flex flex-col gap-3">
          {CALL_LEVEL_OUTCOMES.map(({ key, hint }) => (
            <Row
              key={key}
              outcomeKey={key}
              hint={hint}
              value={outcomes[CALL_LEVEL_NODE]?.[key] ?? ""}
              onChange={(value) => onChange(CALL_LEVEL_NODE, key, value)}
            />
          ))}
        </div>
      </section>

      {nodesWithOutcomes.length === 0 ? (
        <p className="text-sm text-gray-500 dark:text-gray-400">
          Ningún nodo del flujo termina la llamada todavía. Agrega una acción "Colgar" en algún
          desenlace para poder etiquetarlo.
        </p>
      ) : (
        nodesWithOutcomes.map(({ node, index, keys }) => (
          <section key={node.id} className="mb-6 last:mb-0">
            <h5 className="mb-3 text-sm font-semibold text-gray-800 dark:text-white/90">
              {NODE_LABELS[node.type as IvrNodeType]}{" "}
              <span className="font-normal text-gray-400">(#{index + 1})</span>
            </h5>
            <div className="flex flex-col gap-3">
              {keys.map(({ key, hint }) => (
                <Row
                  key={key}
                  outcomeKey={key}
                  hint={hint}
                  value={outcomes[node.id]?.[key] ?? ""}
                  onChange={(value) => onChange(node.id, key, value)}
                />
              ))}
            </div>
          </section>
        ))
      )}
    </Modal>
  );
};
