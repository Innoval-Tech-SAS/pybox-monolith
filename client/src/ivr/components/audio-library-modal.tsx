import { useRef } from "react";
import { Play, Pause, Volume2, Check, Loader2, Upload, Music } from "lucide-react";
import { Modal } from "@/ui/components/modal/modal";
import { useAudioPlayer } from "@/ivr/hooks/use-audio-player";
import { useAudios } from "@/ivr/hooks/use-audios";
import type { IvrAudio } from "@/ivr/types/ivr-audio-types";

type AudioLibraryModalProps = {
  isOpen: boolean;
  onClose: () => void;
  onSelect: (audio: IvrAudio) => void;
};

const formatTime = (seconds: number): string => {
  if (!Number.isFinite(seconds)) return "0:00";
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return `${m}:${s.toString().padStart(2, "0")}`;
};

/**
 * Biblioteca de audios de Helena. Lista los sounds reales, permite reproducir
 * (stream con credenciales), subir nuevos y seleccionar uno para un nodo.
 */
export const AudioLibraryModal: React.FC<AudioLibraryModalProps> = ({
  isOpen,
  onClose,
  onSelect,
}) => {
  const player = useAudioPlayer();
  const { audios, loading, uploading, getPlaybackUrl, uploadAudio } = useAudios();
  const fileInput = useRef<HTMLInputElement | null>(null);

  const handleClose = () => {
    player.stop();
    onClose();
  };

  const handleSelect = (audio: IvrAudio) => {
    player.stop();
    onSelect(audio);
  };

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    e.target.value = "";
    if (!file) return;
    await uploadAudio(file, file.name.replace(/\.[^.]+$/, ""));
  };

  return (
    <Modal isOpen={isOpen} onClose={handleClose} className="m-4 max-w-2xl p-6">
      <div className="mb-5 flex items-start justify-between gap-3">
        <div>
          <h4 className="mb-1 text-lg font-semibold text-gray-800 dark:text-white/90">
            Biblioteca de audios
          </h4>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Selecciona un audio de Helena para asignarlo al nodo.
          </p>
        </div>
        <button
          type="button"
          onClick={() => fileInput.current?.click()}
          disabled={uploading}
          className="inline-flex shrink-0 items-center gap-1.5 rounded-lg border border-brand-500 px-3 py-2 text-xs font-medium text-brand-600 hover:bg-brand-500 hover:text-white disabled:opacity-60 dark:text-brand-400"
        >
          {uploading ? <Loader2 size={14} className="animate-spin" /> : <Upload size={14} />}
          {uploading ? "Subiendo…" : "Subir audio"}
        </button>
        <input
          ref={fileInput}
          type="file"
          accept="audio/*,.wav"
          onChange={handleUpload}
          className="hidden"
        />
      </div>

      {loading ? (
        <div className="flex items-center justify-center gap-2 py-12 text-sm text-gray-500 dark:text-gray-400">
          <Loader2 size={16} className="animate-spin" /> Cargando audios…
        </div>
      ) : audios.length === 0 ? (
        <div className="flex flex-col items-center gap-2 py-12 text-sm text-gray-400 dark:text-gray-500">
          <Music size={28} />
          No hay audios todavía. Sube el primero.
        </div>
      ) : (
        <ul className="flex max-h-96 flex-col gap-1 overflow-y-auto custom-scrollbar pr-1">
          {audios.map((audio) => {
            const key = audio.serverFileName;
            const isCurrent = player.currentKey === key;
            const isPlaying = isCurrent && player.playing;
            const isLoading = player.loadingKey === key;
            return (
              <li
                key={key}
                className={`flex items-center gap-3 rounded-xl border p-3 transition ${
                  isCurrent
                    ? "border-brand-300 bg-brand-50 dark:border-brand-500/40 dark:bg-brand-500/10"
                    : "border-transparent hover:bg-gray-50 dark:hover:bg-white/5"
                }`}
              >
                <button
                  type="button"
                  onClick={() => player.toggle(key, () => getPlaybackUrl(key))}
                  disabled={isLoading}
                  className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-brand-500 text-white hover:bg-brand-600 disabled:opacity-60"
                  aria-label={isPlaying ? "Pausar" : "Reproducir"}
                >
                  {isLoading ? (
                    <Loader2 size={16} className="animate-spin" />
                  ) : isPlaying ? (
                    <Pause size={16} />
                  ) : (
                    <Play size={16} />
                  )}
                </button>

                <div className="min-w-0 flex-1">
                  <p className="truncate text-sm font-medium text-gray-800 dark:text-white/90">
                    {audio.userFriendlyName}
                  </p>
                  {isCurrent ? (
                    <div className="mt-1 flex items-center gap-2">
                      <span className="text-[11px] tabular-nums text-gray-500 dark:text-gray-400">
                        {formatTime(player.currentTime)}
                      </span>
                      <input
                        type="range"
                        min={0}
                        max={player.duration || 0}
                        step={0.1}
                        value={player.currentTime}
                        onChange={(e) => player.seek(Number(e.target.value))}
                        className="h-1 flex-1 cursor-pointer accent-brand-500"
                      />
                      <span className="text-[11px] tabular-nums text-gray-500 dark:text-gray-400">
                        {formatTime(player.duration)}
                      </span>
                    </div>
                  ) : (
                    <span className="truncate text-xs text-gray-400 dark:text-gray-500">
                      {audio.serverFileName}
                    </span>
                  )}
                </div>

                <button
                  type="button"
                  onClick={() => handleSelect(audio)}
                  className="inline-flex shrink-0 items-center gap-1 rounded-lg border border-brand-500 px-3 py-1.5 text-xs font-medium text-brand-600 hover:bg-brand-500 hover:text-white dark:text-brand-400"
                >
                  <Check size={13} /> Seleccionar
                </button>
              </li>
            );
          })}
        </ul>
      )}

      <div className="mt-5 flex items-center gap-3 border-t border-gray-100 pt-4 dark:border-gray-800">
        <Volume2 size={16} className="text-gray-500 dark:text-gray-400" />
        <input
          type="range"
          min={0}
          max={1}
          step={0.05}
          value={player.volume}
          onChange={(e) => player.setVolume(Number(e.target.value))}
          className="h-1 w-40 cursor-pointer accent-brand-500"
          aria-label="Volumen"
        />
      </div>
    </Modal>
  );
};
