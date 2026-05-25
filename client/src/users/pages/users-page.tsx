import { useSearchParams } from "react-router";
import { ModuleBase } from "@/ui/components/common/module-base";
import { UsersDataTable } from "../components/users-data-table";
import { useUsers } from "../hooks/use-users";
import { useUpdateUser } from "../hooks/use-update-user";
import { useDeleteUser } from "../hooks/use-delete-user";

export const UsersPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const orgId = searchParams.get("org_id") ?? undefined;
  const { users, setUsers, loading, refetch } = useUsers(orgId);
  const { updateUser } = useUpdateUser();
  const { deleteUser } = useDeleteUser();

  const handleToggleStatus = async (userId: number, isActive: boolean) => {
    setUsers((prev) => prev.map((u) => (u.id === userId ? { ...u, isActive } : u)));
    const result = await updateUser(userId, { isActive });
    if (!result) {
      setUsers((prev) => prev.map((u) => (u.id === userId ? { ...u, isActive: !isActive } : u)));
    }
  };

  const handleDelete = async (userId: number) => {
    const ok = await deleteUser(userId);
    if (ok) refetch();
  };

  return (
    <ModuleBase pageTitle={orgId ? "Usuarios de la organización" : "Usuarios"}>
      <UsersDataTable
        users={users}
        loading={loading}
        onToggleStatus={handleToggleStatus}
        onDelete={handleDelete}
      />
    </ModuleBase>
  );
};
