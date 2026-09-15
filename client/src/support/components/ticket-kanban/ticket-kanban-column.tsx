import { useRef, useState } from "react";
import { useDrop } from "react-dnd";
import { Dropdown } from "@/ui/components/dropdown/dropdown";
import { DropdownItem } from "@/ui/components/dropdown/dropdown-item";
import { HorizontaLDots } from "@/ui/icons";
import { Badge } from "@/ui/components/badge";
import type { TicketKanbanColumnProps } from "@/types/props/ticket-kanban-column-props";
import type { TicketKanbanDragItem, TicketKanbanDropResult } from "@/types/support/ticket-kanban-types";
import { getStatusBadgeColor } from "@/support/utils/ticket-kanban-utils";
import TicketKanbanItem from "./ticket-kanban-item";

export const TicketKanbanColumn: React.FC<TicketKanbanColumnProps> = ({
  title,
  tickets,
  status,
  getTicketIndex,
  moveTicket,
  changeTicketStatus,
  onOpenTicket,
  isTerminalColumn = false,
}) => {
  const columnRef = useRef<HTMLDivElement>(null);
  const [isOpen, setIsOpen] = useState(false);

  const [, dropColumn] = useDrop<TicketKanbanDragItem, TicketKanbanDropResult, {}>({
    accept: "ticket",
    drop: () => ({ name: status }),
    collect: () => ({}),
  });

  dropColumn(columnRef);

  const toggleDropdown = () => setIsOpen((current) => !current);
  const closeDropdown = () => setIsOpen(false);

  return (
    <div ref={columnRef} className="flex flex-col gap-5 p-4 swim-lane xl:p-6">
      <div className="mb-1 flex items-center justify-between">
        <h3 className="flex items-center gap-3 text-base font-medium text-gray-800 dark:text-white/90">
          {title}
          <Badge size="sm" color={getStatusBadgeColor(status)}>{tickets.length}</Badge>
        </h3>
        <div className="relative">
          <button
            type="button"
            onClick={toggleDropdown}
            className="dropdown-toggle"
          >
            <HorizontaLDots className="size-6 text-gray-400 hover:text-gray-700 dark:hover:text-gray-300" />
          </button>
          <Dropdown
            isOpen={isOpen}
            onClose={closeDropdown}
            className="w-37.5 space-y-1 rounded-2xl border border-gray-200 bg-white p-2 shadow-theme-md dark:border-gray-800 dark:bg-gray-dark"
          >
            <DropdownItem
              onItemClick={closeDropdown}
              className="flex w-full rounded-lg text-left font-normal text-gray-500 hover:bg-gray-100 hover:text-gray-700 dark:text-gray-400 dark:hover:bg-white/5 dark:hover:text-gray-300"
            >
              Ver columna
            </DropdownItem>
            <DropdownItem
              onItemClick={closeDropdown}
              className="flex w-full rounded-lg text-left font-normal text-gray-500 hover:bg-gray-100 hover:text-gray-700 dark:text-gray-400 dark:hover:bg-white/5 dark:hover:text-gray-300"
            >
              Ordenar
            </DropdownItem>
            <DropdownItem
              onItemClick={closeDropdown}
              className="flex w-full rounded-lg text-left font-normal text-gray-500 hover:bg-gray-100 hover:text-gray-700 dark:text-gray-400 dark:hover:bg-white/5 dark:hover:text-gray-300"
            >
              Limpiar
            </DropdownItem>
          </Dropdown>
        </div>
      </div>
      {tickets.map((ticket) => (
        <TicketKanbanItem
          key={ticket.id}
          ticket={ticket}
          index={getTicketIndex(ticket.id)}
          moveTicket={moveTicket}
          changeTicketStatus={changeTicketStatus}
          onOpenTicket={onOpenTicket}
          isTerminal={isTerminalColumn}
        />
      ))}
    </div>
  );
};
