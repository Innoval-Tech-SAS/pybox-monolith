import type { TableProps, TableHeaderProps, TableBodyProps, TableRowProps, TableCellProps } from "@/types/props/table-props";

const Table: React.FC<TableProps> = ({ children, className }) => (
  <table className={`min-w-full ${className ?? ""}`}>{children}</table>
);

const TableHeader: React.FC<TableHeaderProps> = ({ children, className }) => (
  <thead className={className}>{children}</thead>
);

const TableBody: React.FC<TableBodyProps> = ({ children, className }) => (
  <tbody className={className}>{children}</tbody>
);

const TableRow: React.FC<TableRowProps> = ({ children, className }) => (
  <tr className={className}>{children}</tr>
);

const TableCell: React.FC<TableCellProps> = ({ children, isHeader = false, className, colSpan }) => {
  const Tag = isHeader ? "th" : "td";
  return <Tag className={className ?? ""} colSpan={colSpan}>{children}</Tag>;
};

export { Table, TableHeader, TableBody, TableRow, TableCell };
