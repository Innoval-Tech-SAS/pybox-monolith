export const DEFAULT_ALLOWED_FILE_TYPES = ["application/pdf", "image/png"];

export const fileMatchesAllowedTypes = (file: File, allowedTypes: string[]): boolean => {
  const byMime = allowedTypes.includes(file.type);
  const byExt = allowedTypes.some((mime) =>
    file.name.toLowerCase().endsWith(`.${mime.split("/")[1]}`),
  );
  return byMime || byExt;
};
