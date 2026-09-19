export interface PasswordInputProps {
  id?: string;
  name?: string;
  placeholder?: string;
  value?: string;
  defaultValue?: string;
  onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void;
  className?: string;
  disabled?: boolean;
  required?: boolean;
  success?: boolean;
  error?: boolean;
  hint?: string;
  label?: string;
  autoComplete?: string;
  minLength?: number;
  maxLength?: number;
}
