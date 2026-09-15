import type { IvrNodeType } from "@/ivr/types/ivr-node-types";

/**
 * Nodos que el contrato de Helena declara pero cuyo motor **todavía no está
 * probado del lado de Helena**.
 *
 * Están integrados de punta a punta — tipos, compilador, validación y
 * componente visual — pero no se ofrecen en la paleta ni se pueden crear. La
 * razón de integrarlos igual y no dejarlos fuera:
 *
 * - Un flujo guardado que ya los contenga (o uno creado cuando se habiliten)
 *   se abre, se valida y se compila sin tocar nada más.
 * - Habilitarlos cuando Helena los valide es **quitar el tipo de este set**,
 *   no volver a escribir la funcionalidad.
 *
 * La compuerta real está en `useIvrFlow.addNode`, que es por donde pasa toda
 * creación de nodos (paleta, drag & drop y cualquier camino futuro).
 */
export const EXPERIMENTAL_NODE_TYPES: ReadonlySet<IvrNodeType> = new Set<IvrNodeType>([
  "condition",
  "hangup",
]);

export const isExperimentalNode = (type: IvrNodeType): boolean =>
  EXPERIMENTAL_NODE_TYPES.has(type);
