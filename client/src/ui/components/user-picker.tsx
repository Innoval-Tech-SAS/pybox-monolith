import React, { useState } from "react";
import { Search, UserCheck } from "lucide-react";
import { useAccessibleUsers } from "@/hooks/use-accessible-users";
import type { UserPickerProps } from "@/types/props/user-picker-props";

export const UserPicker: React.FC<UserPickerProps> = ({ value, onChange }) => {
  const { users, loading } = useAccessibleUsers();
  const [search, setSearch] = useState("");

  const filtered = users.filter(
    (u) =>
      u.fullName.toLowerCase().includes(search.toLowerCase()) ||
      u.email.toLowerCase().includes(search.toLowerCase()),
  );

  if (loading) {
    return <p className="text-sm text-gray-400">Cargando usuarios...</p>;
  }

  return (
    <div className="space-y-3">
      <div className="relative">
        <span className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">
          <Search size={16} />
        </span>
        <input
          type="text"
          placeholder="Buscar por nombre o correo..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="h-10 w-full rounded-lg border border-gray-300 bg-transparent pl-9 pr-4 text-sm text-gray-800 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/20 dark:border-gray-700 dark:text-white/90"
        />
      </div>
      <div className="max-h-52 overflow-y-auto custom-scrollbar space-y-1 rounded-xl border border-gray-200 p-2 dark:border-gray-700">
        {filtered.length === 0 && (
          <p className="py-4 text-center text-sm text-gray-400">Sin resultados</p>
        )}
        {filtered.map((u) => (
          <button
            key={u.id}
            type="button"
            onClick={() => onChange(value === u.id ? null : u)}
            className={`flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-left text-sm transition ${
              value === u.id
                ? "bg-brand-50 text-brand-700 dark:bg-brand-500/10 dark:text-brand-400"
                : "hover:bg-gray-50 text-gray-700 dark:text-gray-300 dark:hover:bg-white/5"
            }`}
          >
            <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-gray-100 dark:bg-gray-800">
              {value === u.id ? (
                <UserCheck size={14} className="text-brand-600 dark:text-brand-400" />
              ) : (
                <span className="text-xs font-semibold text-gray-500">
                  {u.fullName.charAt(0).toUpperCase()}
                </span>
              )}
            </div>
            <div className="min-w-0">
              <p className="truncate font-medium">{u.fullName}</p>
              <p className="truncate text-xs text-gray-400">{u.email}</p>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
};
