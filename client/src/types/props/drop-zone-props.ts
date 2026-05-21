export interface DropZoneProps {
  label: string;
  file: File | null;
  onChange: (file: File | null) => void;
  error?: string;
}
