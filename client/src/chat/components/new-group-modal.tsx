import { useState } from "react";
import { Users } from "lucide-react";
import { Modal } from "@/ui/components/modal/modal";
import { Input } from "@/ui/components/inputs/input";
import { Button } from "@/ui/components/button/button";
import EmptyState from "@/ui/components/common/empty-state";
import type { NewGroupModalProps } from "../types/new-group-modal-props";

export const NewGroupModal: React.FC<NewGroupModalProps> = ({
  isOpen,
  onClose,
  availableUsers,
  onCreate,
}) => {
  const [title, setTitle] = useState("");
  const [selected, setSelected] = useState<string[]>([]);
  const [submitting, setSubmitting] = useState(false);

  const toggle = (id: string) => {
    setSelected((prev) => (prev.includes(id) ? prev.filter((s) => s !== id) : [...prev, id]));
  };

  const close = () => {
    setTitle("");
    setSelected([]);
    onClose();
  };

  const submit = async () => {
    if (!title.trim() || selected.length === 0 || submitting) return;
    setSubmitting(true);
    try {
      await onCreate(title.trim(), selected);
      close();
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={close} className="max-w-md p-6" ariaLabel="Crear grupo nuevo">
      <h3 className="mb-4 text-lg font-semibold text-gray-800 dark:text-white/90">Nuevo grupo</h3>

      <Input
        label="Nombre del grupo"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        placeholder="Ej. Equipo de cobranza"
        maxLength={255}
      />

      <p className="mt-4 mb-1.5 text-sm font-medium text-gray-700 dark:text-gray-400">Miembros</p>
      <div className="max-h-56 overflow-y-auto custom-scrollbar rounded-lg border border-gray-200 dark:border-gray-800">
        {availableUsers.length === 0 ? (
          <EmptyState icon={Users} title="Sin usuarios disponibles" className="py-4" />
        ) : (
          availableUsers.map((u) => {
            const isChecked = selected.includes(u.id);
            return (
              <label
                key={u.id}
                className="flex items-center gap-2.5 px-3 py-2 cursor-pointer hover:bg-gray-50 dark:hover:bg-white/5 border-b border-gray-100 dark:border-gray-800 last:border-b-0"
              >
                <input
                  type="checkbox"
                  checked={isChecked}
                  onChange={() => toggle(u.id)}
                  className="h-4 w-4 rounded border-gray-300 text-brand-500 focus:ring-brand-500/30 dark:border-gray-700 dark:bg-gray-900"
                />
                {u.profilePhotoUrl ? (
                  <img src={u.profilePhotoUrl} alt={u.fullName} className="w-7 h-7 rounded-full object-cover shrink-0" />
                ) : (
                  <span className="w-7 h-7 rounded-full bg-brand-500 text-white text-xs font-semibold flex items-center justify-center shrink-0">
                    {u.fullName.charAt(0).toUpperCase()}
                  </span>
                )}
                <span className="text-sm text-gray-800 dark:text-white/90 truncate">{u.fullName}</span>
              </label>
            );
          })
        )}
      </div>

      <div className="mt-5 flex justify-end gap-3">
        <Button variant="outline" onClick={close}>
          Cancelar
        </Button>
        <Button
          onClick={submit}
          disabled={!title.trim() || selected.length === 0}
          loading={submitting}
          loadingText="Creando..."
        >
          Crear grupo
        </Button>
      </div>
    </Modal>
  );
};
