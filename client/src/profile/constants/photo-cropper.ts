export const OUTPUT_SIZE = 512;
export const VIEW_SIZE = 288;
export const PREVIEW_SIZE = 96;
export const MIN_ZOOM = 1;
export const MAX_ZOOM = 3;

export const formatFileSize = (bytes: number) => {
  if (bytes < 1024 * 1024) return `${Math.max(1, Math.round(bytes / 1024))} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
};
