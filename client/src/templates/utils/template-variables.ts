const VARIABLE_PATTERN = /\{(\w+)\}/g;

export function extractVariables(source: string): string[] {
  const matches = [...source.matchAll(VARIABLE_PATTERN)];
  return [...new Set(matches.map((m) => m[1]))];
}
