const MAX_FILE_SIZE = 10 * 1024 * 1024;
const ALLOWED_MIME = new Set(["image/png", "image/jpeg", "application/pdf"]);

export const validateOrgDocumentFile = (
  file: File | null,
  label: string,
): string | null => {
  if (!file) return `Debes adjuntar el archivo de ${label}.`;
  if (file.size > MAX_FILE_SIZE) return `El archivo de ${label} supera el límite de 10MB.`;
  if (!ALLOWED_MIME.has(file.type)) return `Formato no permitido para ${label}. Usa PDF, JPG o PNG.`;
  return null;
};
