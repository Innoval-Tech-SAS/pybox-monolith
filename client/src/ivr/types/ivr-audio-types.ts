/**
 * Audio real de Helena (endpoint `/ivr/audios`, que proxea los sounds de Helena).
 * `serverFileName` es el identificador que se guarda en el nodo y se envía a
 * Helena como `audio`; `userFriendlyName` es solo para mostrar.
 */
export type IvrAudio = {
  serverFileName: string;
  userFriendlyName: string;
  slotNumber?: string | number | null;
  transcription?: string | null;
  createdAt?: string | null;
  updatedAt?: string | null;
};
