import { RegisterMode } from "../auth/register-mode";

export interface SignUpFormProps {
  mode: RegisterMode;
  onModeChange: (mode: RegisterMode) => void;
}
