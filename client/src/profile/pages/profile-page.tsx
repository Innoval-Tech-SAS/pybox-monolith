import React from "react";
import { Breadcrumb } from "@/ui/components/common/breadcrumb";
import { ProfileMetaCard } from "../components/profile-meta-card";
import { ProfileInfoCard } from "../components/profile-info-card";

const getUser = () => {
  try {
    return JSON.parse(sessionStorage.getItem("user") ?? "{}");
  } catch {
    return {};
  }
};

export const ProfilePage: React.FC = () => {
  const user = getUser();

  return (
    <>
      <Breadcrumb pageTitle="Perfil" />
      <div className="rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-white/3 lg:p-6">
        <h3 className="mb-5 text-lg font-semibold text-gray-800 dark:text-white/90 lg:mb-7">
          Mi perfil
        </h3>
        <div className="space-y-6">
          <ProfileMetaCard
            firstname={user.firstname ?? ""}
            lastname={user.lastname ?? ""}
            role={user.role}
          />
          <ProfileInfoCard
            email={user.email ?? ""}
            phone={user.phone}
            nationality={user.nationality}
            documentType={user.documentType}
            documentNumber={user.documentNumber}
          />
        </div>
      </div>
    </>
  );
};
