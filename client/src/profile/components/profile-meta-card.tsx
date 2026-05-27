import React from "react";
import { Link } from "react-router";
import { useModal } from "@/hooks/use-modal";
import { Modal } from "@/ui/components/modal/modal";
import { Button } from "@/ui/components/button/button";
import { Input } from "@/ui/components/inputs/input";
import { ProfileMetaCardProps } from "@/types/props/profile-meta-card-props";
import { getRoleHierarchy } from "@/constants/profile/role-hierarchy";

const EditIcon: React.FC = () => (
  <svg className="fill-current" width="18" height="18" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path fillRule="evenodd" clipRule="evenodd" d="M15.0911 2.78206C14.2125 1.90338 12.7878 1.90338 11.9092 2.78206L4.57524 10.116C4.26682 10.4244 4.0547 10.8158 3.96468 11.2426L3.31231 14.3352C3.25997 14.5833 3.33653 14.841 3.51583 15.0203C3.69512 15.1996 3.95286 15.2761 4.20096 15.2238L7.29355 14.5714C7.72031 14.4814 8.11172 14.2693 8.42013 13.9609L15.7541 6.62695C16.6327 5.74827 16.6327 4.32365 15.7541 3.44497L15.0911 2.78206ZM12.9698 3.84272C13.2627 3.54982 13.7376 3.54982 14.0305 3.84272L14.6934 4.50563C14.9863 4.79852 14.9863 5.2734 14.6934 5.56629L14.044 6.21573L12.3204 4.49215L12.9698 3.84272ZM11.2597 5.55281L5.6359 11.1766C5.53309 11.2794 5.46238 11.4099 5.43238 11.5522L5.01758 13.5185L6.98394 13.1037C7.1262 13.0737 7.25666 13.003 7.35947 12.9002L12.9833 7.27639L11.2597 5.55281Z" fill="" />
  </svg>
);

const CameraIcon: React.FC = () => (
  <svg className="fill-current" width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path fillRule="evenodd" clipRule="evenodd" d="M7.75 2.5C7.41848 2.5 7.10054 2.6317 6.86612 2.86612L5.73223 4H3.5C2.67157 4 2 4.67157 2 5.5V15.5C2 16.3284 2.67157 17 3.5 17H16.5C17.3284 17 18 16.3284 18 15.5V5.5C18 4.67157 17.3284 4 16.5 4H14.2678L13.1339 2.86612C12.8995 2.6317 12.5815 2.5 12.25 2.5H7.75ZM10 7.5C8.61929 7.5 7.5 8.61929 7.5 10C7.5 11.3807 8.61929 12.5 10 12.5C11.3807 12.5 12.5 11.3807 12.5 10C12.5 8.61929 11.3807 7.5 10 7.5ZM6 10C6 7.79086 7.79086 6 10 6C12.2091 6 14 7.79086 14 10C14 12.2091 12.2091 14 10 14C7.79086 14 6 12.2091 6 10Z" fill="" />
  </svg>
);

export const ProfileMetaCard: React.FC<ProfileMetaCardProps> = ({ fullName, role, scope, avatarUrl }) => {
  const { isOpen, openModal, closeModal } = useModal();
  console.log("[profile-photo] meta render", { fullName, avatarUrl });

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
                    onLoad={() => console.log("[profile-photo] avatar image loaded", { avatarUrl })}
                    onError={(event) => console.log("[profile-photo] avatar image error", {
                      avatarUrl,
                      currentSrc: event.currentTarget.currentSrc,
                    })}
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
