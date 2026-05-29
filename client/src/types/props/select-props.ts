export interface SelectOption {
  value: string;
  label: string;
}

export interface SelectOptionGroup {
  group: string;
  options: SelectOption[];
}

export interface SelectProps {
  options?: SelectOption[];
  groups?: SelectOptionGroup[];
  placeholder?: string;
  onChange: (value: string) => void;
  className?: string;
  value?: string;
  defaultValue?: string;
  disabled?: boolean;
}
