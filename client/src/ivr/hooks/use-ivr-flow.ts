import { useCallback, useRef, useState } from "react";
import {
  useNodesState,
  useEdgesState,
  addEdge,
  type Connection,
  type XYPosition,
} from "@xyflow/react";
import type {
  IvrNode,
  IvrEdge,
  IvrNodeType,
  IvrNodeDataPatch,
  IvrDefaults,
  IvrRedial,
  IvrOutcomeMap,
  IvrPacing,
} from "@/ivr/types/ivr-node-types";
import {
  createId,
  defaultDataFor,
  NODE_LABELS,
  DEFAULT_FLOW_DEFAULTS,
  DEFAULT_FLOW_REDIAL,
  DEFAULT_FLOW_PACING,
  DEFAULT_FLOW_AMD,
  DEFAULT_FLOW_AMD_PRESET,
} from "@/ivr/utils/ivr-utils";
import { AMD_PRESETS, type AmdPreset, type AmdVariables } from "@/ivr/constants/amd-presets";
import { isExperimentalNode } from "@/ivr/constants/experimental-nodes";

type Snapshot = { nodes: IvrNode[]; edges: IvrEdge[] };
type HydrateInput = Snapshot & {
  entryNodeId?: string | null;
  defaults?: IvrDefaults;
  redial?: IvrRedial;
  amdPreset?: AmdPreset;
  amd?: AmdVariables;
  outcomes?: IvrOutcomeMap;
  pacing?: IvrPacing;
};

const HISTORY_LIMIT = 50;
const DUP_OFFSET = 48;

/**
 * Estado central del diseñador IVR: nodos, conexiones, historial undo/redo y
 * las operaciones de alto nivel (crear, duplicar, actualizar datos de un nodo).
 * El canvas y los nodos consumen estas operaciones; la persistencia vive en
 * useSaveFlow.
 */
export const useIvrFlow = (initial?: Snapshot) => {
  const [nodes, setNodes, onNodesChange] = useNodesState<IvrNode>(initial?.nodes ?? []);
  const [edges, setEdges, onEdgesChange] = useEdgesState<IvrEdge>(initial?.edges ?? []);

  const [past, setPast] = useState<Snapshot[]>([]);
  const [future, setFuture] = useState<Snapshot[]>([]);
  const spawnCount = useRef(0);

  // Ajustes a nivel de flujo (compilan a entry_node / defaults / redial de Helena).
  const [entryNodeId, setEntryNodeId] = useState<string | null>(null);
  const [defaults, setDefaults] = useState<IvrDefaults>(DEFAULT_FLOW_DEFAULTS);
  const [redial, setRedial] = useState<IvrRedial>(DEFAULT_FLOW_REDIAL);
  const [pacing, setPacing] = useState<IvrPacing>(DEFAULT_FLOW_PACING);
  const [amdPreset, setAmdPreset] = useState<AmdPreset>(DEFAULT_FLOW_AMD_PRESET);
  const [amd, setAmd] = useState<AmdVariables>(DEFAULT_FLOW_AMD);

  // Etiquetas de resultado por desenlace, indexadas por id de nodo (estable
  // mientras se edita). El compilador las traduce al nombre del nodo en Helena.
  const [outcomes, setOutcomes] = useState<IvrOutcomeMap>({});

  /** Marca (o alterna) el nodo de entrada del flujo. */
  const setEntryNode = useCallback((nodeId: string) => {
    setEntryNodeId((prev) => (prev === nodeId ? null : nodeId));
  }, []);

  /** Aplica un preset AMD (carga sus valores; siguen siendo editables). */
  const applyAmdPreset = useCallback((preset: AmdPreset) => {
    setAmdPreset(preset);
    setAmd(AMD_PRESETS[preset]);
  }, []);

  /** Edita la etiqueta de un desenlace concreto. */
  const setOutcomeLabel = useCallback((nodeId: string, key: string, label: string) => {
    setOutcomes((prev) => ({ ...prev, [nodeId]: { ...(prev[nodeId] ?? {}), [key]: label } }));
  }, []);

  /** Edita una variable AMD concreta. */
  const setAmdVariable = useCallback((key: keyof AmdVariables, value: string) => {
    setAmd((prev) => ({ ...prev, [key]: value }));
  }, []);

  // Refs con el estado más reciente para que los callbacks sean estables (no se
  // recrean en cada render) y no provoquen re-renders innecesarios de los nodos.
  const nodesRef = useRef(nodes);
  const edgesRef = useRef(edges);
  nodesRef.current = nodes;
  edgesRef.current = edges;

  /** Guarda el estado actual en el historial antes de una mutación. */
  const takeSnapshot = useCallback(() => {
    setPast((p) => [
      ...p.slice(-(HISTORY_LIMIT - 1)),
      { nodes: [...nodesRef.current], edges: [...edgesRef.current] },
    ]);
    setFuture([]);
  }, []);

  const undo = useCallback(() => {
    setPast((p) => {
      if (p.length === 0) return p;
      const previous = p[p.length - 1];
      setFuture((f) => [{ nodes: [...nodesRef.current], edges: [...edgesRef.current] }, ...f]);
      setNodes(previous.nodes);
      setEdges(previous.edges);
      return p.slice(0, -1);
    });
  }, [setNodes, setEdges]);

  const redo = useCallback(() => {
    setFuture((f) => {
      if (f.length === 0) return f;
      const next = f[0];
      setPast((p) => [...p, { nodes: [...nodesRef.current], edges: [...edgesRef.current] }]);
      setNodes(next.nodes);
      setEdges(next.edges);
      return f.slice(1);
    });
  }, [setNodes, setEdges]);

  const onConnect = useCallback(
    (connection: Connection) => {
      takeSnapshot();
      setEdges((eds) => addEdge({ ...connection, animated: true }, eds));
    },
    [takeSnapshot, setEdges],
  );

  const addNode = useCallback(
    (type: IvrNodeType, position?: XYPosition) => {
      // Compuerta única de creación de nodos: la paleta ya no los ofrece, pero
      // esto cubre también el drag & drop y cualquier camino futuro. Un flujo
      // que YA los contenga se sigue abriendo y editando con normalidad.
      if (isExperimentalNode(type)) {
        console.warn(`[ivr] nodo experimental "${type}" no habilitado; no se crea`);
        return;
      }
      takeSnapshot();
      const offset = (spawnCount.current++ % 6) * 32;
      const node = {
        id: createId(),
        type,
        position: position ?? { x: 260 + offset, y: 120 + offset },
        data: defaultDataFor(type),
      } as IvrNode;
      setNodes((nds) => [...nds, node]);
    },
    [takeSnapshot, setNodes],
  );

  /** Actualiza parcialmente el `data` de un nodo (usado por la config inline). */
  const updateNodeData = useCallback(
    (id: string, patch: IvrNodeDataPatch) => {
      setNodes((nds) =>
        nds.map((n) =>
          n.id === id ? ({ ...n, data: { ...n.data, ...patch } } as IvrNode) : n,
        ),
      );
    },
    [setNodes],
  );

  /** Elimina las conexiones que parten de un handle de salida concreto. */
  const removeHandleEdges = useCallback(
    (nodeId: string, handleId: string) => {
      setEdges((eds) =>
        eds.filter((e) => !(e.source === nodeId && e.sourceHandle === handleId)),
      );
    },
    [setEdges],
  );

  /** Duplica los nodos seleccionados (Ctrl+D), desplazados y ya seleccionados. */
  const duplicateSelection = useCallback(() => {
    const selected = nodesRef.current.filter((n) => n.selected);
    if (selected.length === 0) return;
    takeSnapshot();
    const clones = selected.map(
      (n) =>
        ({
          ...n,
          id: createId(),
          position: { x: n.position.x + DUP_OFFSET, y: n.position.y + DUP_OFFSET },
          selected: true,
          data: { ...n.data },
        }) as IvrNode,
    );
    setNodes((nds) => [...nds.map((n) => ({ ...n, selected: false })), ...clones]);
  }, [takeSnapshot, setNodes]);

  const selectAll = useCallback(() => {
    setNodes((nds) => nds.map((n) => ({ ...n, selected: true })));
  }, [setNodes]);

  /** Reemplaza todo el flujo (hidratación desde el backend). */
  const hydrate = useCallback(
    (snapshot: HydrateInput) => {
      setNodes(snapshot.nodes);
      setEdges(snapshot.edges);
      if (snapshot.entryNodeId !== undefined) setEntryNodeId(snapshot.entryNodeId);
      if (snapshot.defaults) setDefaults(snapshot.defaults);
      if (snapshot.redial) setRedial(snapshot.redial);
      if (snapshot.amdPreset) setAmdPreset(snapshot.amdPreset);
      if (snapshot.amd) setAmd(snapshot.amd);
      setOutcomes(snapshot.outcomes ?? {});
      setPacing(snapshot.pacing ?? DEFAULT_FLOW_PACING);
      setPast([]);
      setFuture([]);
    },
    [setNodes, setEdges],
  );

  return {
    nodes,
    edges,
    setNodes,
    setEdges,
    onNodesChange,
    onEdgesChange,
    onConnect,
    takeSnapshot,
    addNode,
    updateNodeData,
    removeHandleEdges,
    duplicateSelection,
    selectAll,
    undo,
    redo,
    hydrate,
    entryNodeId,
    setEntryNode,
    defaults,
    setDefaults,
    redial,
    setRedial,
    pacing,
    setPacing,
    amdPreset,
    amd,
    applyAmdPreset,
    setAmdVariable,
    outcomes,
    setOutcomeLabel,
    canUndo: past.length > 0,
    canRedo: future.length > 0,
    nodeLabels: NODE_LABELS,
  };
};
