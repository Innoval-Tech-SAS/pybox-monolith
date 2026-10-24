import type {
  IvrNodeType,
  IvrNodeData,
  IvrNode,
  IvrEdge,
  IvrDefaults,
  IvrRedial,
  IvrFlowSerialized,
  IvrOutcomeMap,
  IvrPacing,
} from "@/ivr/types/ivr-node-types";
import type { AmdPreset, AmdVariables } from "@/ivr/constants/amd-presets";
import { AMD_PRESETS, DEFAULT_AMD_PRESET } from "@/ivr/constants/amd-presets";

/** Versión del formato de serialización del flujo. */
export const IVR_FLOW_VERSION = 1;

/** Ajustes por defecto de un flujo nuevo (compilan a `defaults` de Helena). */
export const DEFAULT_FLOW_DEFAULTS: IvrDefaults = {
  dtmfTimeoutMs: 8000,
  maxRetries: 2,
  interruptible: true,
};

/** Remarcado por defecto (1 = sin redial). */
export const DEFAULT_FLOW_REDIAL: IvrRedial = {
  maxAttempts: 1,
  retryDelaySeconds: 0,
};

/** Sin ritmo propio: Helena aplica sus defaults de sistema. */
export const DEFAULT_FLOW_PACING: IvrPacing = {
  callsPerSecond: null,
  maxConcurrent: null,
  callerId: "",
  contactPolicyId: "",
};

/** Preset AMD por defecto de un flujo nuevo. */
export const DEFAULT_FLOW_AMD_PRESET: AmdPreset = DEFAULT_AMD_PRESET;
export const DEFAULT_FLOW_AMD: AmdVariables = AMD_PRESETS[DEFAULT_AMD_PRESET];

/**
 * Ids de handle de salida fijos por desenlace. Los dígitos del menú usan
 * `digitHandleId(digitId)` porque son dinámicos.
 */
export const HANDLE_IDS = {
  onFinish: "onFinish",
  onTimeout: "onTimeout",
  onInvalid: "onInvalid",
  onNoAnswer: "onNoAnswer",
  onCompleted: "onCompleted",
  onDefault: "onDefault",
} as const;

export const digitHandleId = (digitId: string): string => `digit-${digitId}`;

/** Handle de salida de una rama del nodo `condition` (dinámica, como los dígitos). */
export const caseHandleId = (caseId: string): string => `case-${caseId}`;

/** Id único y estable para nodos/edges/dígitos. */
export const createId = (): string =>
  `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8)}`;

/**
 * Valida el formato de endpoint SIP `protocolo/servidor/extension` (o
 * `protocolo/destino`), tal como lo espera Helena (ej. `SIP/SERVER25200/6428`).
 * Solo valida el formato, no la existencia real del destino.
 */
export const ENDPOINT_REGEX = /^[A-Za-z0-9]+\/[A-Za-z0-9._\-/]+$/;

export const isValidEndpoint = (value: string): boolean => ENDPOINT_REGEX.test(value.trim());

/** Estado inicial de cada tipo de nodo al crearlo. */
export const defaultDataFor = (type: IvrNodeType): IvrNodeData => {
  switch (type) {
    case "play":
      return {
        audio: null,
        audioLabel: null,
        interruptible: true,
        onFinish: { kind: "hangup" },
      };
    case "menu":
      return {
        audio: null,
        audioLabel: null,
        interruptible: true,
        digits: [],
        onTimeout: { kind: "repeat" },
        onInvalid: { kind: "repeat" },
      };
    case "transfer":
      return {
        endpoint: "",
        timeoutMs: 30000,
        onNoAnswer: { kind: "hangup" },
        onCompleted: { kind: "hangup" },
      };
    case "capture":
      return {
        audio: null,
        audioLabel: null,
        interruptible: true,
        numDigits: 4,
        finishKey: "#",
        timeoutSeconds: 5,
        variable: "",
        onTimeout: { kind: "repeat" },
        onCompleted: { kind: "hangup" },
      };
    case "condition":
      return {
        variable: "amd_status",
        cases: [],
        onDefault: { kind: "hangup" },
      };
    case "hangup":
      return { reason: "" };
  }
};

/** Etiquetas legibles por tipo de nodo. */
export const NODE_LABELS: Record<IvrNodeType, string> = {
  play: "Reproducir",
  menu: "Menú",
  transfer: "Transferir",
  capture: "Captura",
  condition: "Condición",
  hangup: "Colgar",
};

/**
 * Serializa el flujo (nodos + conexiones + ajustes) al `graph` crudo que se
 * persiste en el backend para poder reeditarlo. La compilación al contrato de
 * Helena vive en `utils/compile-flow.ts`.
 */
export const serializeFlow = (params: {
  id: string;
  name: string;
  nodes: IvrNode[];
  edges: IvrEdge[];
  entryNodeId: string | null;
  defaults: IvrDefaults;
  redial: IvrRedial;
  amdPreset: AmdPreset;
  amd: AmdVariables;
  outcomes?: IvrOutcomeMap;
}): IvrFlowSerialized => ({
  id: params.id,
  name: params.name,
  version: IVR_FLOW_VERSION,
  updatedAt: new Date().toISOString(),
  entryNodeId: params.entryNodeId,
  defaults: params.defaults,
  redial: params.redial,
  amdPreset: params.amdPreset,
  amd: params.amd,
  outcomes: params.outcomes ?? {},
  nodes: params.nodes.map((n) => ({
    id: n.id,
    type: n.type as IvrNodeType,
    position: n.position,
    data: n.data,
  })),
  edges: params.edges.map((e) => ({
    id: e.id,
    source: e.source,
    sourceHandle: e.sourceHandle ?? null,
    target: e.target,
    targetHandle: e.targetHandle ?? null,
  })),
});
