import { Link } from "react-router";
import { useModal } from "@/hooks/use-modal";
import { Modal } from "@/ui/components/modal/modal";
import { Button } from "@/ui/components/button/button";
import { Input } from "@/ui/components/inputs/input";
import { ProfileMetaCardProps } from "@/types/props/profile-meta-card-props";
import { getRoleHierarchy } from "@/constants/profile/role-hierarchy";
import { EditIcon, CameraIcon } from "./profile-icons";

export const ProfileMetaCard: React.FC<ProfileMetaCardProps> = ({ fullName, role, scope, avatarUrl }) => {
  const { isOpen, openModal, closeModal } = useModal();

  const hierarchy = getRoleHierarchy(role, scope);

  const initials = fullName
    .split(" ")
    .slice(0, 2)
    .map((w) => w[0] ?? "")
    .join("")
    .toUpperCase();

  return (
    <>
      <div className="p-5 border border-gray-200 rounded-2xl dark:border-gray-800 lg:p-6">
        <div className="flex flex-col gap-5 xl:flex-row xl:items-center xl:justify-between">
          <div className="flex flex-col items-center w-full gap-6 xl:flex-row">
            <div className="relative shrink-0">
              <div className="w-20 h-20 overflow-hidden border border-gray-200 rounded-full dark:border-gray-800">
                {avatarUrl ? (
                  <img
                    src={avatarUrl}
                    alt="avatar"
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center bg-brand-500 text-white text-xl font-semibold">
                    {initials}
                  </div>
                )}
              </div>
              <Link
                to="/profile/photo"
                title="Cambiar foto"
                className="absolute bottom-0 right-0 flex h-7 w-7 items-center justify-center rounded-full bg-brand-500 text-white shadow-sm hover:bg-brand-600"
              >
                <CameraIcon />
              </Link>
            </div>

            <div className="order-3 xl:order-2 text-center xl:text-left">
              <div className="flex items-center justify-center xl:justify-start gap-2 mb-1">
                <h4 className="text-lg font-semibold text-gray-800 dark:text-white/90">
                  {fullName}
                </h4>
                {hierarchy && (
                  <span
                    title={`Nivel ${hierarchy.tier} de 6`}
                    className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-semibold ${hierarchy.containerClass}`}
                  >
                    <span className={hierarchy.iconClass}>{hierarchy.icon}</span>
                    <span className={hierarchy.textClass}>{hierarchy.label}</span>
                  </span>
                )}
              </div>
              {hierarchy && (
                <div className="flex items-center justify-center xl:justify-start gap-1.5">
                  {Array.from({ length: 6 }, (_, i) => (
                    <span
                      key={i}
                      className={`h-1.5 w-4 rounded-full transition-colors ${
                        i < (7 - hierarchy.tier) ? hierarchy.dotClass : "bg-gray-200 dark:bg-gray-700"
                      }`}
                    />
                  ))}
                </div>
              )}
            </div>
          </div>

          <button
            onClick={openModal}
            className="flex w-full items-center justify-center gap-2 rounded-full border border-gray-300 bg-white px-4 py-3 text-sm font-medium text-gray-700 shadow-theme-xs hover:bg-gray-50 hover:text-gray-800 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-400 dark:hover:bg-white/3 dark:hover:text-gray-200 lg:inline-flex lg:w-auto"
          >
            <EditIcon />
            Editar
          </button>
        </div>
      </div>

      <Modal isOpen={isOpen} onClose={closeModal} className="max-w-175 m-4">
        <div className="no-scrollbar relative w-full max-w-175 overflow-y-auto rounded-3xl bg-white p-4 dark:bg-gray-900 lg:p-11">
          <div className="px-2 pr-14">
            <h4 className="mb-2 text-2xl font-semibold text-gray-800 dark:text-white/90">
              Editar perfil
            </h4>
            <p className="mb-6 text-sm text-gray-500 dark:text-gray-400 lg:mb-7">
              Actualiza tu información personal.
            </p>
          </div>
          <form className="flex flex-col">
            <div className="custom-scrollbar overflow-y-auto px-2 pb-3">
              <div>
                <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
                  Nombre completo
                </label>
                <Input defaultValue={fullName} placeholder="Nombre completo" />
              </div>
            </div>
            <div className="flex items-center gap-3 px-2 mt-6 lg:justify-end">
              <Button size="sm" variant="outline" onClick={closeModal}>
                Cerrar
              </Button>
              <Button size="sm" onClick={closeModal}>
                Guardar cambios
              </Button>
            </div>
          </form>
        </div>
      </Modal>
    </>
  );
};
