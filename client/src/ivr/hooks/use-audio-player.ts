import { useCallback, useEffect, useRef, useState } from "react";

/**
 * Reproductor de audio para la Biblioteca de Audios. Maneja una sola instancia
 * de <audio> compartida entre las pistas (estilo Spotify): al reproducir otra,
 * la anterior se detiene. Las URLs son object URLs (blobs descargados con
 * credenciales), así que se revocan al cambiar/detener para no filtrar memoria.
 */
export const useAudioPlayer = () => {
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const objectUrlRef = useRef<string | null>(null);
  const [currentKey, setCurrentKey] = useState<string | null>(null);
  const [playing, setPlaying] = useState(false);
  const [loadingKey, setLoadingKey] = useState<string | null>(null);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolumeState] = useState(1);

  const getAudio = useCallback((): HTMLAudioElement => {
    if (!audioRef.current) {
      const audio = new Audio();
      audio.volume = volume;
      audio.addEventListener("timeupdate", () => setCurrentTime(audio.currentTime));
      audio.addEventListener("loadedmetadata", () => setDuration(audio.duration || 0));
      audio.addEventListener("ended", () => {
        setPlaying(false);
        setCurrentTime(0);
      });
      audioRef.current = audio;
    }
    return audioRef.current;
  }, [volume]);

  const revokeUrl = useCallback(() => {
    if (objectUrlRef.current) {
      URL.revokeObjectURL(objectUrlRef.current);
      objectUrlRef.current = null;
    }
  }, []);

  const pause = useCallback(() => {
    audioRef.current?.pause();
    setPlaying(false);
  }, []);

  /**
   * Play/pause de una pista identificada por `key`. `resolveUrl` descarga el
   * audio (blob) y devuelve un object URL; solo se invoca al iniciar una pista
   * nueva.
   */
  const toggle = useCallback(
    async (key: string, resolveUrl: () => Promise<string>) => {
      const audio = getAudio();
      if (currentKey === key && playing) {
        pause();
        return;
      }
      if (currentKey === key && !playing && objectUrlRef.current) {
        void audio.play();
        setPlaying(true);
        return;
      }
      setLoadingKey(key);
      try {
        const url = await resolveUrl();
        revokeUrl();
        objectUrlRef.current = url;
        audio.src = url;
        setCurrentKey(key);
        setCurrentTime(0);
        void audio.play();
        setPlaying(true);
      } catch {
        setCurrentKey(null);
      } finally {
        setLoadingKey(null);
      }
    },
    [getAudio, currentKey, playing, pause, revokeUrl],
  );

  const seek = useCallback((seconds: number) => {
    const audio = audioRef.current;
    if (!audio) return;
    audio.currentTime = seconds;
    setCurrentTime(seconds);
  }, []);

  const setVolume = useCallback((value: number) => {
    setVolumeState(value);
    if (audioRef.current) audioRef.current.volume = value;
  }, []);

  const stop = useCallback(() => {
    const audio = audioRef.current;
    if (audio) {
      audio.pause();
      audio.currentTime = 0;
    }
    revokeUrl();
    setPlaying(false);
    setCurrentTime(0);
    setCurrentKey(null);
  }, [revokeUrl]);

  useEffect(
    () => () => {
      audioRef.current?.pause();
      audioRef.current = null;
      if (objectUrlRef.current) URL.revokeObjectURL(objectUrlRef.current);
    },
    [],
  );

  return {
    currentKey,
    playing,
    loadingKey,
    currentTime,
    duration,
    volume,
    toggle,
    seek,
    setVolume,
    stop,
  };
};
