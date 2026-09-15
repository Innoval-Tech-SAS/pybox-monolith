import React from "react";
import { ModuleBase } from "@/ui/components/common/module-base";
import { Loader } from "@/ui/components/loader/loader";
import { UserCard } from "../components/user-card";
import { useProfileDetail } from "../hooks/use-profile-detail";

export const ProfilePage: React.FC = () => {
  const { data, loading } = useProfileDetail();

  return (
    <ModuleBase pageTitle="Perfil">
      {loading || !data ? (
        <Loader variant="section" />
      ) : (
        <UserCard data={data} isOwnProfile />
      )}
    </ModuleBase>
  );
};
