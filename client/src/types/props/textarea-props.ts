export interface TextareaProps {
  id?: string;
  name?: string;
  placeholder?: string;
  value?: string;
  defaultValue?: string;
  onChange?: (e: React.ChangeEvent<HTMLTextAreaElement>) => void;
  className?: string;
  rows?: number;
  disabled?: boolean;
  required?: boolean;
  success?: boolean;
  error?: boolean;
  hint?: string;
  label?: string;
  maxLength?: number;
}
