import { useState } from "react";
import { useSearchParams } from "react-router";
import { Users } from "lucide-react";
import { ModuleBase } from "@/ui/components/common/module-base";
import { useBreadcrumb } from "@/companies/hooks/use-breadcrumb";
import { ConfirmModal } from "@/ui/components/modal/confirm-modal";
import { Switch } from "@/ui/components/switch";
import { UsersDataTable } from "../components/users-data-table";
import { AddUserButton } from "../components/add-user-button";
import { useUsers } from "../hooks/use-users";
import { useUpdateUser } from "../hooks/use-update-user";
import { useDeleteUser } from "../hooks/use-delete-user";
import { useRestoreUser } from "../hooks/use-restore-user";
import { useIsGlobalAdmin } from "@/auth/hooks/use-is-global-admin";
import type { UserSummary } from "@/types/users/user-types";

export const UsersPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const orgId = searchParams.get("org") ?? undefined;
  const { build } = useBreadcrumb();
  const isGlobalAdmin = useIsGlobalAdmin();
  const [showDeleted, setShowDeleted] = useState(false);
  const { users, setUsers, loading, refetch } = useUsers(orgId, isGlobalAdmin && showDeleted);
  const { updateUser } = useUpdateUser();
  const { deleteUser, loading: deleting } = useDeleteUser();
  const { restoreUser } = useRestoreUser();

  const [userToDelete, setUserToDelete] = useState<UserSummary | null>(null);
  const [userToDeactivate, setUserToDeactivate] = useState<UserSummary | null>(null);
  const [deactivating, setDeactivating] = useState(false);

  const applyToggleStatus = async (userId: string, isActive: boolean) => {
    setUsers((prev) =>
      prev.map((u) => (u.id === userId ? { ...u, isActive } : u)),
    );
    const result = await updateUser(userId, { isActive });
    if (!result) {
      setUsers((prev) =>
        prev.map((u) => (u.id === userId ? { ...u, isActive: !isActive } : u)),
      );
    }
  };

  const handleToggleStatus = (userId: string, isActive: boolean) => {
    // Activar no pide confirmación; desactivar sí, porque le corta el acceso a la
    // plataforma a alguien que puede seguir trabajando en ese momento.
    if (!isActive) {
      const user = users.find((u) => u.id === userId);
      if (user) {
        setUserToDeactivate(user);
        return;
      }
    }
    void applyToggleStatus(userId, isActive);
  };

  const confirmDeactivate = async () => {
    if (!userToDeactivate) return;
    const id = userToDeactivate.id;
    setDeactivating(true);
    try {
      await applyToggleStatus(id, false);
    } finally {
      setDeactivating(false);
      setUserToDeactivate(null);
    }
  };

  const confirmDelete = async () => {
    if (!userToDelete) return;
    const ok = await deleteUser(userToDelete.id);
    setUserToDelete(null);
    if (ok) refetch();
  };

  const handleRestore = async (user: UserSummary) => {
    const ok = await restoreUser(user.id);
    if (ok) refetch();
  };

  return (
    <ModuleBase
      pageTitle={"Usuarios"}
      pageIcon={Users}
      breadcrumbItems={build()}
      showBack
    >
      <div className="shrink-0 flex items-center justify-end gap-4 mb-4">
        {isGlobalAdmin && (
          <Switch
            checked={showDeleted}
            onChange={setShowDeleted}
            label="Mostrar eliminados"
          />
        )}
        <AddUserButton orgId={orgId} />
      </div>
      <UsersDataTable
        users={users}
        loading={loading}
        orgId={orgId}
        onToggleStatus={handleToggleStatus}
        onDelete={setUserToDelete}
        onRestore={isGlobalAdmin ? handleRestore : undefined}
      />

      <ConfirmModal
        isOpen={!!userToDelete}
        onClose={() => setUserToDelete(null)}
        onConfirm={confirmDelete}
        title="Eliminar usuario"
        message={`¿Seguro que deseas eliminar al usuario "${userToDelete?.fullName}"? Esta acción no se puede deshacer.`}
        loading={deleting}
      />

      <ConfirmModal
        isOpen={!!userToDeactivate}
        onClose={() => setUserToDeactivate(null)}
        onConfirm={confirmDeactivate}
        title="Desactivar usuario"
        message={`¿Seguro que deseas desactivar a "${userToDeactivate?.fullName}"? Perderá acceso a la plataforma de inmediato.`}
        confirmLabel="Desactivar"
        loading={deactivating}
      />
    </ModuleBase>
  );
};
