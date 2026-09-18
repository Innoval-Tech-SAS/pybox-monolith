import { useState } from "react";
import { UserPlus, Users, X } from "lucide-react";
import EmptyState from "@/ui/components/common/empty-state";
import { CHAT_MEMBER_ROLE_ADMIN, CHAT_MEMBER_ROLE_OWNER } from "@/types/chat/chat-types";
import type { GroupMembersPanelProps } from "../types/group-members-panel-props";

const ROLE_LABELS: Record<number, string> = {
  [CHAT_MEMBER_ROLE_OWNER]: "Propietario",
  [CHAT_MEMBER_ROLE_ADMIN]: "Admin",
};

export const GroupMembersPanel: React.FC<GroupMembersPanelProps> = ({
  isOpen,
  onClose,
  members,
  availableUsers,
  currentUserId,
  onAddMember,
  onRemoveMember,
}) => {
  const [showAdd, setShowAdd] = useState(false);

  if (!isOpen) return null;

  const me = members.find((m) => m.userId === currentUserId);
  const canManage = me ? me.role >= CHAT_MEMBER_ROLE_ADMIN : false;
  const memberIds = new Set(members.map((m) => m.userId));
  const candidates = availableUsers.filter((u) => !memberIds.has(u.id));

  return (
    <div className="absolute right-3 top-14 z-20 w-72 rounded-2xl border border-gray-200 bg-white shadow-theme-lg dark:border-gray-800 dark:bg-gray-dark">
      <div className="flex items-center justify-between px-4 py-3 border-b border-gray-200 dark:border-gray-800">
        <span className="text-sm font-semibold text-gray-800 dark:text-white/90">
          Miembros ({members.length})
        </span>
        <button
          type="button"
          onClick={onClose}
          aria-label="Cerrar panel de miembros"
          className="text-gray-400 hover:text-gray-700 dark:hover:text-white/80"
        >
          <X size={16} />
        </button>
      </div>

      <div className="max-h-64 overflow-y-auto custom-scrollbar">
        {members.map((m) => (
          <div
            key={m.userId}
            className="flex items-center gap-2.5 px-4 py-2 hover:bg-gray-50 dark:hover:bg-white/5"
          >
            {m.profilePhotoUrl ? (
              <img src={m.profilePhotoUrl} alt={m.fullName} className="w-7 h-7 rounded-full object-cover shrink-0" />
            ) : (
              <span className="w-7 h-7 rounded-full bg-brand-500 text-white text-xs font-semibold flex items-center justify-center shrink-0">
                {m.fullName.charAt(0).toUpperCase()}
              </span>
            )}
            <div className="flex-1 min-w-0">
              <p className="text-sm text-gray-800 dark:text-white/90 truncate">{m.fullName}</p>
              {ROLE_LABELS[m.role] && (
                <p className="text-xs text-gray-400">{ROLE_LABELS[m.role]}</p>
              )}
            </div>
            {canManage && m.userId !== currentUserId && m.role !== CHAT_MEMBER_ROLE_OWNER && (
              <button
                type="button"
                onClick={() => onRemoveMember(m.userId)}
                aria-label={`Quitar a ${m.fullName} del grupo`}
                className="shrink-0 text-gray-400 hover:text-error-500"
              >
                <X size={14} />
              </button>
            )}
          </div>
        ))}
      </div>

      {canManage && (
        <div className="border-t border-gray-200 dark:border-gray-800">
          {!showAdd ? (
            <button
              type="button"
              onClick={() => setShowAdd(true)}
              className="flex items-center gap-2 w-full px-4 py-2.5 text-sm text-brand-500 hover:bg-gray-50 dark:hover:bg-white/5"
            >
              <UserPlus size={16} />
              Agregar miembro
            </button>
          ) : (
            <div className="max-h-40 overflow-y-auto custom-scrollbar">
              {candidates.length === 0 ? (
                <EmptyState icon={Users} title="Sin candidatos" className="py-3" />
              ) : (
                candidates.map((u) => (
                  <button
                    key={u.id}
                    type="button"
                    onClick={() => onAddMember(u.id)}
                    className="flex items-center gap-2.5 w-full px-4 py-2 text-left hover:bg-gray-50 dark:hover:bg-white/5"
                  >
                    {u.profilePhotoUrl ? (
                      <img src={u.profilePhotoUrl} alt={u.fullName} className="w-7 h-7 rounded-full object-cover shrink-0" />
                    ) : (
                      <span className="w-7 h-7 rounded-full bg-brand-500 text-white text-xs font-semibold flex items-center justify-center shrink-0">
                        {u.fullName.charAt(0).toUpperCase()}
                      </span>
                    )}
                    <span className="text-sm text-gray-800 dark:text-white/90 truncate">{u.fullName}</span>
                  </button>
                ))
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
