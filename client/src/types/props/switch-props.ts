export interface SwitchProps {
  checked: boolean;
  onChange: (checked: boolean) => void;
  label?: string;
  /** Nombre accesible cuando no hay `label` visible junto al switch (p. ej. en una
   * fila de tabla). Si se omite, cae a `label`. */
  ariaLabel?: string;
  disabled?: boolean;
}
