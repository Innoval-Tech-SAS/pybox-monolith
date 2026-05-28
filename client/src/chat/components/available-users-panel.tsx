import React, { useEffect, useState } from "react";
import { Link } from "react-router";
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
      className="absolute bottom-16 right-0 w-64 bg-white dark:bg-gray-dark border border-gray-200 dark:border-gray-800 rounded-xl shadow-xl z-50 flex flex-col overflow-hidden"
    >
      <div className="px-3 py-2 border-b border-gray-200 dark:border-gray-800">
        <p className="text-xs font-semibold text-gray-800 dark:text-white/90 mb-1">
          Nueva conversación
        </p>
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Buscar usuario..."
          className="w-full text-xs bg-gray-50 dark:bg-gray-900 rounded-md px-2 py-1.5 focus:outline-none text-gray-800 dark:text-white/90 placeholder:text-gray-400 dark:placeholder:text-white/30"
          autoFocus
        />
      </div>

      <div className="overflow-y-auto custom-scrollbar max-h-60">
        {filtered.length === 0 ? (
          <p className="text-xs text-gray-400 text-center py-4">
            Sin resultados
          </p>
        ) : (
          filtered.map((user) => (
            <button
              key={user.id}
              onClick={() => onSelect(user)}
              className="w-full flex items-center gap-2 px-3 py-2 hover:bg-gray-50 dark:hover:bg-white/5 transition-colors text-left"
            >
              <div className="relative shrink-0">
                {user.profilePhotoUrl ? (
                  <img
                    src={user.profilePhotoUrl}
                    alt={user.fullName}
                    className="w-8 h-8 rounded-full object-cover"
                  />
                ) : (
                  <span className="w-8 h-8 rounded-full bg-brand-500 text-white text-xs font-semibold flex items-center justify-center">
                    {user.fullName.charAt(0).toUpperCase()}
                  </span>
                )}
                <span
                  className={`absolute bottom-0 right-0 w-2.5 h-2.5 rounded-full border-2 border-white dark:border-gray-dark ${
                    user.isOnline ? "bg-success-500" : "bg-gray-400"
                  }`}
                />
              </div>
              <span className="text-sm text-gray-800 dark:text-white/90 truncate">
                {user.fullName}
              </span>
            </button>
          ))
        )}
      </div>

      <div className="px-3 py-2 border-t border-gray-200 dark:border-gray-800">
        <Link
          to="/chats"
          onClick={onClose}
          className="block rounded-lg border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 px-4 py-2 text-center text-sm font-medium text-gray-800 dark:text-white/90 hover:bg-gray-50 dark:hover:bg-white/5 transition-colors"
        >
          Ver todos los chats
        </Link>
      </div>
    </div>
  );
};
