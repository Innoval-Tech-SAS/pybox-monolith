import React, { useEffect, useState } from "react";
import type { ChatAvailableUser } from "../../types/chat/chat-types";

interface AvailableUsersPanelProps {
  users: ChatAvailableUser[];
  onSelect: (user: ChatAvailableUser) => void;
  onClose: () => void;
}

export const AvailableUsersPanel: React.FC<AvailableUsersPanelProps> = ({
  users,
  onSelect,
  onClose,
}) => {
  const [search, setSearch] = useState("");

  const filtered = users.filter((u) =>
    u.fullName.toLowerCase().includes(search.toLowerCase()),
  );

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      const target = e.target as Element;
      if (!target.closest("[data-chat-panel]")) onClose();
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, [onClose]);

  return (
    <div
      data-chat-panel
      className="absolute bottom-16 right-0 w-64 bg-white dark:bg-boxdark border border-stroke dark:border-strokedark rounded-xl shadow-xl z-50 flex flex-col overflow-hidden"
    >
      <div className="px-3 py-2 border-b border-stroke dark:border-strokedark">
        <p className="text-xs font-semibold text-black dark:text-white mb-1">
          Nueva conversación
        </p>
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Buscar usuario..."
          className="w-full text-xs bg-gray-2 dark:bg-meta-4 rounded-md px-2 py-1.5 focus:outline-none text-black dark:text-white placeholder:text-gray-400"
          autoFocus
        />
      </div>

      <div className="overflow-y-auto max-h-60">
        {filtered.length === 0 ? (
          <p className="text-xs text-gray-400 text-center py-4">
            Sin resultados
          </p>
        ) : (
          filtered.map((user) => (
            <button
              key={user.id}
              onClick={() => onSelect(user)}
              className="w-full flex items-center gap-2 px-3 py-2 hover:bg-gray-2 dark:hover:bg-meta-4 transition-colors text-left"
            >
              {user.profilePhotoUrl ? (
                <img
                  src={user.profilePhotoUrl}
                  alt={user.fullName}
                  className="w-8 h-8 rounded-full object-cover flex-shrink-0"
                />
              ) : (
                <span className="w-8 h-8 rounded-full bg-brand-500 text-white text-xs font-semibold flex items-center justify-center flex-shrink-0">
                  {user.fullName.charAt(0).toUpperCase()}
                </span>
              )}
              <span className="text-sm text-black dark:text-white truncate">
                {user.fullName}
              </span>
            </button>
          ))
        )}
      </div>
    </div>
  );
};
