import type {
  IvrAction,
  IvrDefaults,
  IvrEdge,
  IvrNode,
  IvrNodeType,
  IvrOutcomeMap,
  IvrRedial,
} from "@/ivr/types/ivr-node-types";
import {
  CALL_LEVEL_NODE,
  SYSTEM_OUTCOMES,
  TRANSFER_SYSTEM_OUTCOME,
} from "@/ivr/types/ivr-node-types";
import { NODE_LABELS, isValidEndpoint } from "@/ivr/utils/ivr-utils";

/**
 * Compilador del grafo visual (React Flow) al contrato declarativo de Helena
 * (`CampaignIvrConfig`). También valida el flujo antes de compilar: si hay
 * errores, el diseñador bloquea el guardado y los muestra al usuario.
 */

// ── Tipos del contrato Helena (destino de la compilación) ────────────────────

type HelenaAction =
  | { action: "goto"; node: string }
  | { action: "hangup"; reason: string }
  | { action: "repeat" };

type HelenaNode = Record<string, unknown> & { type: string };

export type CampaignIvrConfig = {
  version: number;
  entry_node: string;
  defaults: { dtmf_timeout_ms: number; max_retries: number; interruptible: boolean };
  nodes: Record<string, HelenaNode>;
};

export type CampaignRedialConfig = { maxAttempts: number; retryDelaySeconds?: number };

export type CompileResult = {
  errors: string[];
  /**
   * Avisos que NO bloquean el guardado: el flujo es válido para Helena, pero
   * hay algo que casi siempre es un descuido (un nodo sin conectar, por
   * ejemplo). Se separan de `errors` a propósito: bloquear el guardado por
   * esto impediría dejar un nodo a medio cablear y volver después.
   */
  warnings: string[];
  config: CampaignIvrConfig | null;
  redialConfig: CampaignRedialConfig | null;
  /** Etiquetas de resultado indexadas por el nombre del nodo en Helena. */
  outcomes: IvrOutcomeMap | null;
};

const HELENA_TYPE: Record<IvrNodeType, string> = {
  play: "playback",
  menu: "menu",
  transfer: "transfer",
  capture: "collect",
  condition: "condition",
  hangup: "hangup",
};

/** Motivos por defecto de `hangup` según el desenlace (para reportería en Helena). */
const DEFAULT_REASON: Record<string, string> = {
  onFinish: "PLAYBACK_DONE",
  menuTimeout: "NO_INPUT",
  onInvalid: "INVALID",
  onNoAnswer: "NO_ANSWER",
  transferCompleted: "TRANSFER_DONE",
  captureTimeout: "TIMEOUT",
  captureCompleted: "COLLECT_DONE",
  digit: "OPTION",
  conditionCase: "CONDITION",
  conditionDefault: "CONDITION_DEFAULT",
  hangupNode: "HANGUP",
};

/**
 * Motivo por defecto al colgar tras una tecla. Es por dígito (OPTION_1,
 * OPTION_2, …) y no un OPTION común: si todas las teclas compartieran motivo, el
 * reporte no podría distinguir quién aceptó de quién rechazó, que es justamente
 * para lo que sirven las etiquetas de resultado.
 */
const digitReason = (key: string): string => "OPTION_" + key;

/** Motivo efectivo de una acción `hangup` (el escrito por el usuario, o el default). */
const reasonFor = (action: IvrAction, fallback: string): string =>
  action.reason?.trim() || fallback;

const nodeLabel = (node: IvrNode, index: number): string =>
  `${NODE_LABELS[node.type as IvrNodeType]} (#${index + 1})`;

/**
 * Nombre del nodo dentro del `nodes` de Helena.
 *
 * Se deriva del **id del nodo**, no de su posición en el array. El nombre viaja
 * a Helena y vuelve en `ivrEndNodeId`, y es la clave contra la que se resuelven
 * las etiquetas de resultado: si dependiera del índice, insertar o borrar un
 * nodo renombraría a todos los siguientes y las llamadas de un bulk ya
 * despachado se tipificarían contra el nodo equivocado.
 *
 * Se antepone el tipo para que el nombre siga siendo legible en los reportes y
 * en los logs de Helena.
 */
const nodeNameFor = (node: IvrNode): string =>
  `${HELENA_TYPE[node.type as IvrNodeType]}_${node.id.replace(/[^A-Za-z0-9]/g, "")}`;

type Ctx = {
  nodeName: Map<string, string>;
  edges: IvrEdge[];
  nodeId: string;
  label: string;
  errors: string[];
};

/** Resuelve el destino de un `goto` siguiendo el edge que sale de `handleId`. */
const resolveGoto = (ctx: Ctx, handleId: string | undefined, outcome: string): string | null => {
  const edge = ctx.edges.find((e) => e.source === ctx.nodeId && e.sourceHandle === handleId);
  if (!edge) {
    ctx.errors.push(`${ctx.label}: el desenlace "${outcome}" ("Ir a nodo") no está conectado.`);
    return null;
  }
  return ctx.nodeName.get(edge.target) ?? null;
};

const compileAction = (
  ctx: Ctx,
  action: IvrAction,
  outcome: string,
  reasonKey: string,
): HelenaAction => {
  if (action.kind === "goto") {
    const target = resolveGoto(ctx, action.handleId, outcome);
    return { action: "goto", node: target ?? "__unresolved__" };
  }
  if (action.kind === "repeat") return { action: "repeat" };
  return { action: "hangup", reason: reasonFor(action, DEFAULT_REASON[reasonKey] || "HANGUP") };
};

/**
 * Desenlaces por los que una llamada puede terminar dentro de un nodo, con una
 * pista legible. Son las claves que el diseñador puede etiquetar y contra las
 * que el backend resuelve `ivrEndReason` al cerrar la llamada.
 */
export const outcomeKeysForNode = (node: IvrNode): Array<{ key: string; hint: string }> => {
  const out: Array<{ key: string; hint: string }> = [];
  const push = (key: string, hint: string) => {
    if (key && !out.some((o) => o.key === key)) out.push({ key, hint });
  };

  if (node.type === "play") {
    if (node.data.onFinish.kind === "hangup") {
      push(reasonFor(node.data.onFinish, DEFAULT_REASON.onFinish), "Terminó el audio y colgó");
    }
  } else if (node.type === "menu") {
    node.data.digits.forEach((d) => {
      if (d.key !== "" && d.action.kind === "hangup") {
        push(reasonFor(d.action, digitReason(d.key)), "Marcó " + d.key + " y colgó");
      }
    });
    if (node.data.onTimeout.kind === "hangup") {
      push(reasonFor(node.data.onTimeout, DEFAULT_REASON.menuTimeout), "No marcó nada");
    }
    if (node.data.onInvalid.kind === "hangup") {
      push(reasonFor(node.data.onInvalid, DEFAULT_REASON.onInvalid), "Marcó una tecla inválida");
    }
  } else if (node.type === "transfer") {
    if (node.data.onNoAnswer.kind === "hangup") {
      push(reasonFor(node.data.onNoAnswer, DEFAULT_REASON.onNoAnswer), "Ningún agente contestó");
    }
    if (node.data.onCompleted.kind === "hangup") {
      push(
        reasonFor(node.data.onCompleted, DEFAULT_REASON.transferCompleted),
        "Terminó la transferencia",
      );
    }
    push(TRANSFER_SYSTEM_OUTCOME.key, TRANSFER_SYSTEM_OUTCOME.hint);
  } else if (node.type === "capture") {
    if (node.data.onTimeout.kind === "hangup") {
      push(reasonFor(node.data.onTimeout, DEFAULT_REASON.captureTimeout), "No capturó dígitos");
    }
    if (node.data.onCompleted.kind === "hangup") {
      push(
        reasonFor(node.data.onCompleted, DEFAULT_REASON.captureCompleted),
        "Capturó los dígitos y colgó",
      );
    }
  } else if (node.type === "condition") {
    node.data.cases.forEach((c) => {
      if (c.action.kind === "hangup") {
        push(
          reasonFor(c.action, DEFAULT_REASON.conditionCase),
          `Cayó en la rama "${c.value || "?"}" y colgó`,
        );
      }
    });
    if (node.data.onDefault.kind === "hangup") {
      push(
        reasonFor(node.data.onDefault, DEFAULT_REASON.conditionDefault),
        "No coincidió ninguna rama y colgó",
      );
    }
  } else if (node.type === "hangup") {
    push(node.data.reason.trim() || DEFAULT_REASON.hangupNode, "Llegó a este nodo y colgó");
  }

  SYSTEM_OUTCOMES.forEach((o) => push(o.key, o.hint));
  return out;
};

/** Nombre con el que cada nodo del editor aparece en el contrato de Helena. */
export const compiledNodeNames = (nodes: IvrNode[]): Map<string, string> =>
  new Map(nodes.map((n) => [n.id, nodeNameFor(n)]));

/**
 * Valida el flujo. Devuelve una lista de errores legibles (vacía si es válido).
 */
export const validateFlow = (
  nodes: IvrNode[],
  edges: IvrEdge[],
  entryNodeId: string | null,
): string[] => {
  const errors: string[] = [];
  if (nodes.length === 0) {
    errors.push("El flujo no tiene nodos. Agrega al menos uno.");
    return errors;
  }
  if (!entryNodeId || !nodes.some((n) => n.id === entryNodeId)) {
    errors.push("Marca un nodo como entrada (inicio de la llamada).");
  }

  const nodeName = compiledNodeNames(nodes);

  nodes.forEach((node, i) => {
    const label = nodeLabel(node, i);
    const ctx: Ctx = { nodeName, edges, nodeId: node.id, label, errors };

    if (node.type === "play") {
      if (!node.data.audio) errors.push(`${label}: falta seleccionar un audio.`);
      if (node.data.onFinish.kind === "goto") resolveGoto(ctx, node.data.onFinish.handleId, "al finalizar");
    } else if (node.type === "menu") {
      if (!node.data.audio) errors.push(`${label}: falta seleccionar un audio.`);
      const withKey = node.data.digits.filter((d) => d.key !== "");
      if (withKey.length === 0) errors.push(`${label}: agrega al menos una opción (dígito).`);
      const keys = withKey.map((d) => d.key);
      if (new Set(keys).size !== keys.length) errors.push(`${label}: hay dígitos repetidos en las opciones.`);
      node.data.digits.forEach((d) => {
        if (d.key === "") errors.push(`${label}: hay una opción sin tecla asignada.`);
        if (d.action.kind === "goto") resolveGoto(ctx, d.action.handleId, `tecla ${d.key || "?"}`);
      });
      if (node.data.onTimeout.kind === "goto") resolveGoto(ctx, node.data.onTimeout.handleId, "sin respuesta");
      if (node.data.onInvalid.kind === "goto") resolveGoto(ctx, node.data.onInvalid.handleId, "dígito inválido");
    } else if (node.type === "transfer") {
      if (!isValidEndpoint(node.data.endpoint)) errors.push(`${label}: el endpoint SIP no es válido (ej. SIP/SERVIDOR/6428).`);
      if (!(node.data.timeoutMs > 0)) errors.push(`${label}: el tiempo de ring debe ser mayor a 0.`);
      if (node.data.onNoAnswer.kind === "goto") resolveGoto(ctx, node.data.onNoAnswer.handleId, "no contesta");
      if (node.data.onCompleted.kind === "goto") resolveGoto(ctx, node.data.onCompleted.handleId, "completada");
    } else if (node.type === "capture") {
      if (!node.data.variable.trim()) errors.push(`${label}: falta el nombre de la variable donde guardar los dígitos.`);
      if (!(node.data.numDigits >= 1)) errors.push(`${label}: la cantidad de dígitos debe ser al menos 1.`);
      if (node.data.onTimeout.kind === "goto") resolveGoto(ctx, node.data.onTimeout.handleId, "sin respuesta");
      if (node.data.onCompleted.kind === "goto") resolveGoto(ctx, node.data.onCompleted.handleId, "completada");
    } else if (node.type === "condition") {
      if (!node.data.variable.trim()) errors.push(`${label}: falta la variable a evaluar.`);
      const values = node.data.cases.map((c) => c.value.trim());
      if (values.some((v) => !v)) errors.push(`${label}: hay una rama sin valor a comparar.`);
      if (new Set(values).size !== values.length) {
        errors.push(`${label}: hay valores repetidos entre las ramas.`);
      }
      node.data.cases.forEach((c) => {
        if (c.action.kind === "goto") {
          resolveGoto(ctx, c.action.handleId, `rama "${c.value || "?"}"`);
        }
      });
      // `cases: {}` es válido en Helena (cae siempre al default), así que no se
      // exige al menos una rama: solo que el default esté bien resuelto.
      if (node.data.onDefault.kind === "goto") {
        resolveGoto(ctx, node.data.onDefault.handleId, "sin coincidencia");
      }
    }
    // `hangup` es terminal y no tiene desenlaces: nada que validar.
  });

  return errors;
};

/**
 * Avisos no bloqueantes del flujo. Hoy solo la inalcanzabilidad, que Helena
 * acepta sin problema (el nodo simplemente nunca se ejecuta) pero que casi
 * siempre significa que quedó un desenlace sin conectar.
 */
export const flowWarnings = (
  nodes: IvrNode[],
  edges: IvrEdge[],
  entryNodeId: string | null,
): string[] => findUnreachableNodes(nodes, edges, entryNodeId);

/**
 * Nodos a los que la llamada nunca puede llegar partiendo del nodo de entrada.
 *
 * Se recorre el grafo por los edges reales, que es exactamente lo que resuelve
 * los `goto` al compilar: un nodo suelto en el lienzo compila igual y Helena lo
 * acepta, pero es trabajo que nunca se va a ejecutar, y casi siempre significa
 * que quedó un desenlace sin conectar.
 */
const findUnreachableNodes = (
  nodes: IvrNode[],
  edges: IvrEdge[],
  entryNodeId: string | null,
): string[] => {
  if (!entryNodeId || nodes.length === 0) return [];
  if (!nodes.some((n) => n.id === entryNodeId)) return [];

  const outgoing = new Map<string, string[]>();
  edges.forEach((e) => {
    const list = outgoing.get(e.source) ?? [];
    list.push(e.target);
    outgoing.set(e.source, list);
  });

  const reachable = new Set<string>([entryNodeId]);
  const pending = [entryNodeId];
  while (pending.length > 0) {
    const current = pending.pop()!;
    for (const next of outgoing.get(current) ?? []) {
      if (!reachable.has(next)) {
        reachable.add(next);
        pending.push(next);
      }
    }
  }

  return nodes
    .map((node, i) => ({ node, i }))
    .filter(({ node }) => !reachable.has(node.id))
    .map(
      ({ node, i }) =>
        `${nodeLabel(node, i)}: no se puede llegar a este nodo desde el nodo de entrada.`,
    );
};

/**
 * Compila el flujo al `CampaignIvrConfig` de Helena. Devuelve también los
 * errores de validación; si hay alguno, `config` es null.
 */
export const compileFlow = (params: {
  nodes: IvrNode[];
  edges: IvrEdge[];
  entryNodeId: string | null;
  defaults: IvrDefaults;
  redial: IvrRedial;
  /** Etiquetas de resultado del editor, indexadas por id de nodo. */
  outcomes?: IvrOutcomeMap;
}): CompileResult => {
  const { nodes, edges, entryNodeId, defaults, redial, outcomes } = params;
  const errors = validateFlow(nodes, edges, entryNodeId);
  const warnings = flowWarnings(nodes, edges, entryNodeId);
  if (errors.length > 0) {
    return { errors, warnings, config: null, redialConfig: null, outcomes: null };
  }

  const nodeName = compiledNodeNames(nodes);
  const helenaNodes: Record<string, HelenaNode> = {};

  nodes.forEach((node, i) => {
    const ctx: Ctx = { nodeName, edges, nodeId: node.id, label: nodeLabel(node, i), errors };
    const name = nodeNameFor(node);

    if (node.type === "play") {
      helenaNodes[name] = {
        type: "playback",
        audio: node.data.audio,
        interruptible: node.data.interruptible,
        after: compileAction(ctx, node.data.onFinish, "al finalizar", "onFinish"),
      };
    } else if (node.type === "menu") {
      const withKey = node.data.digits.filter((d) => d.key !== "");
      const options: Record<string, HelenaAction> = {};
      withKey.forEach((d) => {
        const compiled = compileAction(ctx, d.action, `tecla ${d.key}`, "digit");
        if (compiled.action === "hangup") {
          compiled.reason = reasonFor(d.action, digitReason(d.key));
        }
        options[d.key] = compiled;
      });
      helenaNodes[name] = {
        type: "menu",
        audio: node.data.audio,
        interruptible: node.data.interruptible,
        valid_digits: withKey.map((d) => d.key),
        options,
        on_no_input: compileAction(ctx, node.data.onTimeout, "sin respuesta", "menuTimeout"),
        on_invalid: compileAction(ctx, node.data.onInvalid, "dígito inválido", "onInvalid"),
      };
    } else if (node.type === "transfer") {
      helenaNodes[name] = {
        type: "transfer",
        endpoint: node.data.endpoint.trim(),
        timeout_ms: node.data.timeoutMs,
        on_no_answer: compileAction(ctx, node.data.onNoAnswer, "no contesta", "onNoAnswer"),
        on_finish: compileAction(ctx, node.data.onCompleted, "completada", "transferCompleted"),
      };
    } else if (node.type === "capture") {
      const collect: HelenaNode = {
        type: "collect",
        num_digits: node.data.numDigits,
        timeout_ms: node.data.timeoutSeconds * 1000,
        finish_on_key: node.data.finishKey,
        variable: node.data.variable.trim(),
        on_complete: compileAction(ctx, node.data.onCompleted, "completada", "captureCompleted"),
        on_timeout: compileAction(ctx, node.data.onTimeout, "sin respuesta", "captureTimeout"),
      };
      if (node.data.audio) collect.audio = node.data.audio;
      helenaNodes[name] = collect;
    } else if (node.type === "condition") {
      const cases: Record<string, HelenaAction> = {};
      node.data.cases.forEach((c) => {
        const value = c.value.trim();
        if (!value) return;
        cases[value] = compileAction(
          { ...ctx, nodeId: node.id },
          c.action,
          `rama "${value}"`,
          "conditionCase",
        );
      });
      helenaNodes[name] = {
        type: "condition",
        variable: node.data.variable.trim(),
        cases,
        default: compileAction(ctx, node.data.onDefault, "sin coincidencia", "conditionDefault"),
      };
    } else if (node.type === "hangup") {
      helenaNodes[name] = {
        type: "hangup",
        reason: node.data.reason.trim() || DEFAULT_REASON.hangupNode,
      };
    }
  });

  // La resolución de gotos durante la compilación pudo detectar inconsistencias.
  if (errors.length > 0) {
    return { errors, warnings, config: null, redialConfig: null, outcomes: null };
  }

  const entryName = entryNodeId ? nodeName.get(entryNodeId) ?? "" : "";
  const config: CampaignIvrConfig = {
    version: 1,
    entry_node: entryName,
    defaults: {
      dtmf_timeout_ms: defaults.dtmfTimeoutMs,
      max_retries: defaults.maxRetries,
      interruptible: defaults.interruptible,
    },
    nodes: helenaNodes,
  };

  const redialConfig: CampaignRedialConfig | null =
    redial.maxAttempts > 1
      ? { maxAttempts: redial.maxAttempts, retryDelaySeconds: redial.retryDelaySeconds }
      : null;

  return {
    errors: [],
    warnings,
    config,
    redialConfig,
    outcomes: compileOutcomes(nodes, outcomes),
  };
};

/**
 * Traduce las etiquetas del editor (indexadas por id de nodo) al mapa que
 * consume el backend (indexado por el nombre del nodo en Helena, que es lo que
 * llega en `ivrEndNodeId`). Se descartan las etiquetas vacías.
 */
const compileOutcomes = (
  nodes: IvrNode[],
  outcomes: IvrOutcomeMap | undefined,
): IvrOutcomeMap => {
  const compiled: IvrOutcomeMap = {};
  if (!outcomes) return compiled;

  const clean = (entries: Record<string, string> | undefined): Record<string, string> | null => {
    if (!entries) return null;
    const result: Record<string, string> = {};
    Object.entries(entries).forEach(([key, label]) => {
      const trimmed = (label ?? "").trim();
      if (trimmed) result[key] = trimmed;
    });
    return Object.keys(result).length > 0 ? result : null;
  };

  const callLevel = clean(outcomes[CALL_LEVEL_NODE]);
  if (callLevel) compiled[CALL_LEVEL_NODE] = callLevel;

  nodes.forEach((node) => {
    const entries = clean(outcomes[node.id]);
    if (entries) compiled[nodeNameFor(node)] = entries;
  });

  return compiled;
};
