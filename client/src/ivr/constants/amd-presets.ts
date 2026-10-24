/**
 * Configuración AMD (detección de contestadora) que Helena recibe en el
 * parámetro `variables`. Los presets viven en memoria en el front; el usuario
 * puede partir de uno y editar cada valor. Valores portados de collectia,
 * calibrados para operadores/celulares colombianos.
 */

export type AmdPreset = "Balanceado" | "Conservador" | "Agresivo";

export type AmdVariables = {
  AMD_INITIAL_SILENCE: string;
  AMD_GREETING: string;
  AMD_AFTER_GREETING_SILENCE: string;
  AMD_TOTAL_ANALYSIS_TIME: string;
  AMD_MIN_WORD_LENGTH: string;
  AMD_BETWEEN_WORDS_SILENCE: string;
  AMD_MAX_WORDS: string;
  AMD_SILENCE_THRESHOLD: string;
  AMD_MAX_WORD_LENGTH: string;
};

export const AMD_PRESET_OPTIONS: AmdPreset[] = ["Balanceado", "Conservador", "Agresivo"];

export const DEFAULT_AMD_PRESET: AmdPreset = "Balanceado";

/** Campos AMD en orden de despliegue, con su etiqueta legible. */
export const AMD_FIELDS: [keyof AmdVariables, string][] = [
  ["AMD_INITIAL_SILENCE", "Silencio inicial (ms)"],
  ["AMD_GREETING", "Saludo (ms)"],
  ["AMD_AFTER_GREETING_SILENCE", "Sil. post-saludo (ms)"],
  ["AMD_TOTAL_ANALYSIS_TIME", "T. análisis (ms)"],
  ["AMD_MIN_WORD_LENGTH", "Min. palabra (ms)"],
  ["AMD_BETWEEN_WORDS_SILENCE", "Sil. entre palabras (ms)"],
  ["AMD_MAX_WORDS", "Máx. palabras"],
  ["AMD_SILENCE_THRESHOLD", "Umbral silencio"],
  ["AMD_MAX_WORD_LENGTH", "Máx. palabra (ms)"],
];

export const AMD_PRESETS: Record<AmdPreset, AmdVariables> = {
  Balanceado: {
    AMD_INITIAL_SILENCE: "2500",
    AMD_GREETING: "2800",
    AMD_AFTER_GREETING_SILENCE: "600",
    AMD_TOTAL_ANALYSIS_TIME: "7000",
    AMD_MIN_WORD_LENGTH: "100",
    AMD_BETWEEN_WORDS_SILENCE: "200",
    AMD_MAX_WORDS: "6",
    AMD_SILENCE_THRESHOLD: "384",
    AMD_MAX_WORD_LENGTH: "2500",
  },
  Conservador: {
    AMD_INITIAL_SILENCE: "3500",
    AMD_GREETING: "3000",
    AMD_AFTER_GREETING_SILENCE: "500",
    AMD_TOTAL_ANALYSIS_TIME: "7500",
    AMD_MIN_WORD_LENGTH: "80",
    AMD_BETWEEN_WORDS_SILENCE: "250",
    AMD_MAX_WORDS: "7",
    AMD_SILENCE_THRESHOLD: "256",
    AMD_MAX_WORD_LENGTH: "3000",
  },
  Agresivo: {
    AMD_INITIAL_SILENCE: "2000",
    AMD_GREETING: "1800",
    AMD_AFTER_GREETING_SILENCE: "1200",
    AMD_TOTAL_ANALYSIS_TIME: "6000",
    AMD_MIN_WORD_LENGTH: "100",
    AMD_BETWEEN_WORDS_SILENCE: "200",
    AMD_MAX_WORDS: "3",
    AMD_SILENCE_THRESHOLD: "512",
    AMD_MAX_WORD_LENGTH: "2000",
  },
};
