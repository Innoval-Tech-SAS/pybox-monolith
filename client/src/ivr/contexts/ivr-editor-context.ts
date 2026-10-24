import { createContext } from "react";
import type { IvrNodeDataPatch } from "@/ivr/types/ivr-node-types";
import type { IvrAudio } from "@/ivr/types/ivr-audio-types";

/**
 * Puente entre los nodos (renderizados por React Flow) y el estado del editor.
 * Permite que la config inline de cada nodo actualice sus datos, marque el nodo
 * de entrada y abra la Biblioteca de Audios sin acoplarse a la página.
 */
export type IvrEditorContextValue = {
  updateNodeData: (id: string, patch: IvrNodeDataPatch) => void;
  /** Antes de mutar (para historial undo/redo). */
  takeSnapshot: () => void;
  /** Elimina las conexiones que parten de un handle de salida concreto. */
  removeHandleEdges: (nodeId: string, handleId: string) => void;
  /** Abre el modal de audios; `onSelect` recibe el audio elegido. */
  openAudioLibrary: (onSelect: (audio: IvrAudio) => void) => void;
  /** Id del nodo de entrada (inicio de la llamada), o null si no hay. */
  entryNodeId: string | null;
  /** Marca (o alterna) un nodo como entrada del flujo. */
  setEntryNode: (nodeId: string) => void;
};

export const IvrEditorContext = createContext<IvrEditorContextValue | undefined>(undefined);
