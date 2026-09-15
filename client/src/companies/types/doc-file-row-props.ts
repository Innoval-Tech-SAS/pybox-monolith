export type DocType = "fiscal" | "mercantil" | "representante";

export interface DocFileRowProps {
  label: string;
  fileUrl: string | null | undefined;
  docType: DocType;
  saving: boolean;
  onUpload: (docType: DocType, file: File) => void;
}
