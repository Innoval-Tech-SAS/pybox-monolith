import { useState } from "react";

export const useDeleteWithConfirm = <T extends { id: string }>(
  deleteFn: (id: string) => Promise<unknown>,
) => {
  const [deleting, setDeleting] = useState<T | null>(null);
  const [deletingInProgress, setDeletingInProgress] = useState(false);

  const confirmDelete = async () => {
    if (!deleting) return;
    setDeletingInProgress(true);
    try {
      await deleteFn(deleting.id);
      setDeleting(null);
    } finally {
      setDeletingInProgress(false);
    }
  };

  return { deleting, setDeleting, confirmDelete, deletingInProgress };
};
