import { useCallback, useEffect, useState } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import { API_URL } from "@/config/api";
import type { IvrAudio } from "@/ivr/types/ivr-audio-types";

type SoundsResponse = { sounds?: RawSound[] } | RawSound[];
type RawSound = {
  serverFileName?: string;
  userFriendlyName?: string;
  slotNumber?: string | number | null;
  transcription?: string | null;
  createdAt?: string | null;
  updatedAt?: string | null;
};

const normalize = (raw: RawSound): IvrAudio => ({
  serverFileName: raw.serverFileName ?? "",
  userFriendlyName: raw.userFriendlyName ?? raw.serverFileName ?? "Audio",
  slotNumber: raw.slotNumber ?? null,
  transcription: raw.transcription ?? null,
  createdAt: raw.createdAt ?? null,
  updatedAt: raw.updatedAt ?? null,
});

/**
 * Biblioteca de audios de Helena. Lista los sounds, reproduce vía stream (con
 * cookies httpOnly, por eso se obtiene un blob) y permite subir nuevos audios.
 */
export const useAudios = () => {
  const { apiClient } = useApiClient();
  const [audios, setAudios] = useState<IvrAudio[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);

  const fetchAudios = useCallback(() => {
    setLoading(true);
    apiClient("/ivr/audios/", { method: "GET" })
      .then((data: SoundsResponse) => {
        const list = Array.isArray(data) ? data : (data?.sounds ?? []);
        setAudios(list.map(normalize).filter((a) => a.serverFileName));
      })
      .catch(() => setAudios([]))
      .finally(() => setLoading(false));
  }, [apiClient]);

  useEffect(() => {
    fetchAudios();
  }, [fetchAudios]);

  /**
   * Descarga el audio como blob (adjuntando cookies) y devuelve un object URL
   * para el elemento <audio>. El llamador debe revocar la URL al terminar.
   */
  const getPlaybackUrl = useCallback(async (serverFileName: string): Promise<string> => {
    const res = await fetch(
      `${API_URL}/ivr/audios/${encodeURIComponent(serverFileName)}/stream`,
      { credentials: "include" },
    );
    if (!res.ok) throw new Error(`No se pudo cargar el audio (${res.status})`);
    const blob = await res.blob();
    return URL.createObjectURL(blob);
  }, []);

  const uploadAudio = useCallback(
    async (file: File, userFriendlyName?: string): Promise<boolean> => {
      setUploading(true);
      try {
        const form = new FormData();
        form.append("file", file);
        if (userFriendlyName) form.append("userFriendlyName", userFriendlyName);
        await apiClient("/ivr/audios/upload", { method: "POST", body: form });
        fetchAudios();
        return true;
      } catch {
        return false;
      } finally {
        setUploading(false);
      }
    },
    [apiClient, fetchAudios],
  );

  return { audios, loading, uploading, refetch: fetchAudios, getPlaybackUrl, uploadAudio };
};
