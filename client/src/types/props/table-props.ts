/**
 * Props para el componente Table.
 * @property children - Contenido de la tabla (thead, tbody, etc.).
 * @property className - Clases adicionales para personalizar estilos.
 */
export interface TableProps {
  children: ReactNode;
  className?: string;
}

/**
 * Props para el componente TableHeader.
 * @property children - Fila(s) del encabezado de la tabla.
 * @property className - Clases adicionales para personalizar estilos.
 */
export interface TableHeaderProps {
  children: ReactNode;
  className?: string;
}

/**
 * Props para el componente TableBody.
 * @property children - Fila(s) del cuerpo de la tabla.
 * @property className - Clases adicionales para personalizar estilos.
 */
export interface TableBodyProps {
  children: ReactNode;
  className?: string;
}

/**
 * Props para el componente TableRow.
 * @property children - Celdas de la fila (th o td).
 * @property className - Clases adicionales para personalizar estilos.
 */
export interface TableRowProps {
  children: ReactNode;
  className?: string;
}

/**
 * Props para el componente TableCell.
 * @property children - Contenido de la celda.
 * @property isHeader - Si es true, se renderiza como <th>, de lo contrario como <td>.
 * @property className - Clases adicionales para personalizar estilos.
 */
export interface TableCellProps {
  children: ReactNode;
  isHeader?: boolean;
  className?: string;
}
