export interface LogoUploadCardProps {
  logoUrl: string | null | undefined;
  saving: boolean;
  onUpload: (file: File) => void;
  label?: string;
}
