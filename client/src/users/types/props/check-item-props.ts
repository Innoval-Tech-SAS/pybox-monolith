export interface CheckItemProps {
  id: string;
  label: string;
  sublabel?: string;
  checked: boolean;
  busy: boolean;
  indent?: boolean;
  onChange: (checked: boolean) => void;
}
