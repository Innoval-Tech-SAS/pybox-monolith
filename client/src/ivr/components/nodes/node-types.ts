import type { NodeTypes } from "@xyflow/react";
import { PlayNode } from "./play-node";
import { MenuNode } from "./menu-node";
import { TransferNode } from "./transfer-node";
import { CaptureNode } from "./capture-node";
import { ConditionNode } from "./condition-node";
import { HangupNode } from "./hangup-node";

/**
 * Mapa de tipos de nodo para React Flow. Se declara fuera de todo componente
 * para mantener la referencia estable (evita re-montar los nodos en cada render).
 * El cast salva la varianza estricta entre `NodeProps<TipoConcreto>` y el
 * `NodeProps` genérico que espera `NodeTypes`.
 *
 * `condition` y `hangup` se registran aunque estén marcados como experimentales
 * y no se puedan crear desde la paleta: si un flujo guardado los contiene, tiene
 * que poder abrirse y editarse en vez de romper el lienzo. La compuerta que
 * impide crearlos está en `useIvrFlow.addNode`.
 */
export const IVR_NODE_TYPES = {
  play: PlayNode,
  menu: MenuNode,
  transfer: TransferNode,
  capture: CaptureNode,
  condition: ConditionNode,
  hangup: HangupNode,
} as unknown as NodeTypes;
