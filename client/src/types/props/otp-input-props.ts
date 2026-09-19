export interface OtpInputProps {
  length?: number;
  value: string[];
  onChange: (value: string[]) => void;
  disabled?: boolean;
  error?: boolean;
}
