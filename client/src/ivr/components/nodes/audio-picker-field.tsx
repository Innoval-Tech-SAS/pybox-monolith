import { Music, Check } from "lucide-react";
import { useIvrEditor } from "@/ivr/hooks/use-ivr-editor";
import type { IvrNodeDataPatch } from "@/ivr/types/ivr-node-types";

type AudioPickerFieldProps = {
  nodeId: string;
  /** Nombre amigable del audio seleccionado (o null). */
  audioLabel: string | null;
};

/**
 * Botón de selección de audio compartido por los nodos Reproducir, Menú y
 * Captura. Abre la Biblioteca de Audios y asigna al nodo el `serverFileName`
 * (lo que Helena necesita) más el nombre amigable para mostrar.
 */
export const AudioPickerField: React.FC<AudioPickerFieldProps> = ({ nodeId, audioLabel }) => {
  const { openAudioLibrary, updateNodeData, takeSnapshot } = useIvrEditor();

  const pick = () =>
    openAudioLibrary((audio) => {
      takeSnapshot();
      updateNodeData(nodeId, {
        audio: audio.serverFileName,
        audioLabel: audio.userFriendlyName,
      } as IvrNodeDataPatch);
    });

  return (
    <label className="flex flex-col gap-1">
      <span className="font-medium text-gray-600 dark:text-gray-300">Audio</span>
      <button
        type="button"
        onClick={pick}
        className={`flex items-center gap-2 rounded-lg border px-3 py-2 text-left transition ${
          audioLabel
            ? "border-brand-300 bg-brand-50 text-brand-700 dark:border-brand-500/40 dark:bg-brand-500/10 dark:text-brand-300"
            : "border-gray-300 bg-transparent text-gray-500 hover:border-brand-300 dark:border-gray-700 dark:text-gray-400"
        }`}
      >
        {audioLabel ? <Check size={14} /> : <Music size={14} />}
        <span className="truncate">{audioLabel ?? "Seleccionar audio"}</span>
      </button>
    </label>
  );
};
