import { useCallback } from "react";
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  useReactFlow,
  type Connection,
  type XYPosition,
  type OnNodesChange,
  type OnEdgesChange,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import type { IvrNode, IvrEdge, IvrNodeType } from "@/ivr/types/ivr-node-types";
import { IVR_NODE_TYPES } from "./nodes/node-types";
import { NODE_DND_MIME } from "./ivr-node-sidebar";

type IvrCanvasProps = {
  nodes: IvrNode[];
  edges: IvrEdge[];
  onNodesChange: OnNodesChange<IvrNode>;
  onEdgesChange: OnEdgesChange<IvrEdge>;
  onConnect: (connection: Connection) => void;
  onAddNodeAt: (type: IvrNodeType, position: XYPosition) => void;
  /** Snapshot para historial al empezar a mover un nodo. */
  onNodeDragStart: () => void;
};

/**
 * Lienzo de React Flow: nodos custom, minimapa, controles, fondo y drop desde
 * el panel lateral. Debe renderizarse dentro de un <ReactFlowProvider>.
 */
export const IvrCanvas: React.FC<IvrCanvasProps> = ({
  nodes,
  edges,
  onNodesChange,
  onEdgesChange,
  onConnect,
  onAddNodeAt,
  onNodeDragStart,
}) => {
  const { screenToFlowPosition } = useReactFlow();

  const onDrop = useCallback(
    (event: React.DragEvent) => {
      event.preventDefault();
      const type = event.dataTransfer.getData(NODE_DND_MIME) as IvrNodeType;
      if (!type) return;
      const position = screenToFlowPosition({ x: event.clientX, y: event.clientY });
      onAddNodeAt(type, position);
    },
    [screenToFlowPosition, onAddNodeAt],
  );

  const onDragOver = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = "move";
  }, []);

  return (
    <div className="h-full w-full" onDrop={onDrop} onDragOver={onDragOver}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={IVR_NODE_TYPES}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onNodeDragStart={onNodeDragStart}
        deleteKeyCode={["Delete", "Backspace"]}
        multiSelectionKeyCode={["Meta", "Control"]}
        selectionKeyCode={["Shift"]}
        fitView
        minZoom={0.2}
        className="bg-gray-50 dark:bg-gray-950"
      >
        <Background className="bg-gray-50! dark:bg-gray-950!" gap={18} />
        <MiniMap pannable zoomable className="bg-white! dark:bg-gray-900!" />
        <Controls />
      </ReactFlow>
    </div>
  );
};
