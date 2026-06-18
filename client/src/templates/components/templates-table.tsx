import { Eye, Mail, Pencil, Trash2 } from "lucide-react";
import {
  Table,
  TableBody,
  TableCell,
  TableHeader,
  TableRow,
} from "@/ui/components/table/table";
import type { TemplateStatus } from "@/types/templates/template-types";
import type { TemplatesTableProps } from "@/templates/types/templates-table-props";

const STATUS_LABELS: Record<TemplateStatus, string> = {
  DRAFT: "Borrador",
  ACTIVE: "Activa",
  INACTIVE: "Inactiva",
};

const STATUS_COLORS: Record<TemplateStatus, string> = {
  DRAFT: "bg-gray-100 text-gray-500 dark:bg-gray-800 dark:text-gray-400",
  ACTIVE: "bg-success-50 text-success-700 dark:bg-success-500/10 dark:text-success-400",
  INACTIVE: "bg-error-50 text-error-600 dark:bg-error-500/10 dark:text-error-400",
};

export const TemplatesTable: React.FC<TemplatesTableProps> = ({
  items,
  isAdmin,
  onPreview,
  onSend,
  onEdit,
  onDelete,
}) => {
  if (items.length === 0) {
    return (
      <p className="py-12 text-center text-sm text-gray-400 dark:text-gray-500">
        No hay plantillas registradas.
      </p>
    );
  }

  return (
    <div className="overflow-x-auto rounded-xl border border-gray-200 dark:border-gray-800">
      <Table>
        <TableHeader>
          <TableRow className="border-b border-gray-200 dark:border-gray-800">
            {["Nombre", "Canal", "Estado", "Asunto", ""].map((h) => (
              <TableCell
                key={h}
                isHeader
                className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wide text-gray-500 dark:text-gray-400"
              >
                {h}
              </TableCell>
            ))}
          </TableRow>
        </TableHeader>
        <TableBody>
          {items.map((item) => (
            <TableRow key={item.id} className="border-b border-gray-100 last:border-0 dark:border-gray-800">
              <TableCell className="px-4 py-3 text-sm font-medium text-gray-800 dark:text-white/90">
                {item.name}
              </TableCell>
              <TableCell className="px-4 py-3">
                <span className="inline-flex items-center rounded-full bg-gray-100 px-2.5 py-0.5 text-xs font-medium text-gray-600 dark:bg-gray-800 dark:text-gray-300">
                  {item.channel}
                </span>
              </TableCell>
              <TableCell className="px-4 py-3">
                <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${STATUS_COLORS[item.status]}`}>
                  {STATUS_LABELS[item.status]}
                </span>
              </TableCell>
              <TableCell className="px-4 py-3 text-sm text-gray-600 dark:text-gray-400">
                {item.subject ?? "—"}
              </TableCell>
              <TableCell className="px-4 py-3">
                <div className="flex items-center gap-1">
                  <button onClick={() => onPreview(item)} title="Vista previa" className="rounded p-1.5 text-gray-400 hover:bg-gray-100 hover:text-brand-500 dark:hover:bg-gray-800">
                    <Eye size={14} />
                  </button>
                  {item.channel === "EMAIL" && item.status === "ACTIVE" && (
                    <button onClick={() => onSend(item)} title="Enviar" className="rounded p-1.5 text-gray-400 hover:bg-gray-100 hover:text-brand-500 dark:hover:bg-gray-800">
                      <Mail size={14} />
                    </button>
                  )}
                  {isAdmin && (
                    <>
                      <button onClick={() => onEdit(item)} title="Editar" className="rounded p-1.5 text-gray-400 hover:bg-gray-100 hover:text-gray-600 dark:hover:bg-gray-800">
                        <Pencil size={14} />
                      </button>
                      <button onClick={() => onDelete(item)} title="Eliminar" className="rounded p-1.5 text-gray-400 hover:bg-error-50 hover:text-error-500">
                        <Trash2 size={14} />
                      </button>
                    </>
                  )}
                </div>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
};
