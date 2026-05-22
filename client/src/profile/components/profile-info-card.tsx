import React, { useState } from "react";
import { useModal } from "@/hooks/use-modal";
import { Modal } from "@/ui/components/modal/modal";
import { Button } from "@/ui/components/button/button";
import { Input } from "@/ui/components/inputs/input";
import { ProfileInfoCardProps } from "@/types/props/profile-info-card-props";

const EditIcon: React.FC = () => (
  <svg className="fill-current" width="18" height="18" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path fillRule="evenodd" clipRule="evenodd" d="M15.0911 2.78206C14.2125 1.90338 12.7878 1.90338 11.9092 2.78206L4.57524 10.116C4.26682 10.4244 4.0547 10.8158 3.96468 11.2426L3.31231 14.3352C3.25997 14.5833 3.33653 14.841 3.51583 15.0203C3.69512 15.1996 3.95286 15.2761 4.20096 15.2238L7.29355 14.5714C7.72031 14.4814 8.11172 14.2693 8.42013 13.9609L15.7541 6.62695C16.6327 5.74827 16.6327 4.32365 15.7541 3.44497L15.0911 2.78206ZM12.9698 3.84272C13.2627 3.54982 13.7376 3.54982 14.0305 3.84272L14.6934 4.50563C14.9863 4.79852 14.9863 5.2734 14.6934 5.56629L14.044 6.21573L12.3204 4.49215L12.9698 3.84272ZM11.2597 5.55281L5.6359 11.1766C5.53309 11.2794 5.46238 11.4099 5.43238 11.5522L5.01758 13.5185L6.98394 13.1037C7.1262 13.0737 7.25666 13.003 7.35947 12.9002L12.9833 7.27639L11.2597 5.55281Z" fill="" />
  </svg>
);

interface Field {
  label: string;
  value: string;
  key: string;
  colSpan?: boolean;
}

export const ProfileInfoCard: React.FC<ProfileInfoCardProps> = ({
  email,
  phone = "",
  nationality = "",
  documentType = "",
  documentNumber = "",
}) => {
  const { isOpen, openModal, closeModal } = useModal();
  const [form, setForm] = useState({ email, phone, nationality, documentType, documentNumber });

  const fields: Field[] = [
    { label: "Correo electrónico", value: form.email, key: "email" },
    { label: "Teléfono", value: form.phone, key: "phone" },
    { label: "Nacionalidad", value: form.nationality, key: "nationality" },
    { label: "Tipo de documento", value: form.documentType, key: "documentType" },
    { label: "Número de documento", value: form.documentNumber, key: "documentNumber", colSpan: true },
  ];

  return (
    <>
      <div className="p-5 border border-gray-200 rounded-2xl dark:border-gray-800 lg:p-6">
        <div className="flex flex-col gap-6 lg:flex-row lg:items-start lg:justify-between">
          <div>
            <h4 className="mb-4 text-lg font-semibold text-gray-800 dark:text-white/90 lg:mb-6">
              Información personal
            </h4>
            <div className="grid grid-cols-1 gap-4 lg:grid-cols-2 lg:gap-7 2xl:gap-x-32">
              {fields.map((field) => (
                field.value && (
                  <div key={field.key} className={field.colSpan ? "col-span-2 lg:col-span-1" : ""}>
                    <p className="mb-2 text-xs leading-normal text-gray-500 dark:text-gray-400">
                      {field.label}
                    </p>
                    <p className="text-sm font-medium text-gray-800 dark:text-white/90">
                      {field.value}
                    </p>
                  </div>
                )
              ))}
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
              Editar información personal
            </h4>
            <p className="mb-6 text-sm text-gray-500 dark:text-gray-400 lg:mb-7">
              Mantén tus datos actualizados.
            </p>
          </div>
          <form className="flex flex-col">
            <div className="custom-scrollbar h-100 overflow-y-auto px-2 pb-3">
              <div className="grid grid-cols-1 gap-x-6 gap-y-5 lg:grid-cols-2">
                <div className="col-span-2 lg:col-span-1">
                  <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
                    Correo electrónico
                  </label>
                  <Input
                    value={form.email}
                    onChange={(e) => setForm((f) => ({ ...f, email: e.target.value }))}
                    placeholder="correo@ejemplo.com"
                  />
                </div>
                <div className="col-span-2 lg:col-span-1">
                  <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
                    Teléfono
                  </label>
                  <Input
                    value={form.phone}
                    onChange={(e) => setForm((f) => ({ ...f, phone: e.target.value }))}
                    placeholder="+58 412 0000000"
                  />
                </div>
                <div className="col-span-2 lg:col-span-1">
                  <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
                    Nacionalidad
                  </label>
                  <Input
                    value={form.nationality}
                    onChange={(e) => setForm((f) => ({ ...f, nationality: e.target.value }))}
                    placeholder="Venezuela"
                  />
                </div>
                <div className="col-span-2 lg:col-span-1">
                  <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
                    Tipo de documento
                  </label>
                  <Input
                    value={form.documentType}
                    onChange={(e) => setForm((f) => ({ ...f, documentType: e.target.value }))}
                    placeholder="Cédula"
                  />
                </div>
                <div className="col-span-2">
                  <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
                    Número de documento
                  </label>
                  <Input
                    value={form.documentNumber}
                    onChange={(e) => setForm((f) => ({ ...f, documentNumber: e.target.value }))}
                    placeholder="V-12345678"
                  />
                </div>
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
