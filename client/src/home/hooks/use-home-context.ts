import { useMemo } from "react";
import { useAuth } from "@/hooks/use-auth";
import type { HomeContext } from "@/types/home/home-types";
import { getFirstAssignment, hasSessionAccess, readSessionUser } from "../utils/home-session-utils";

export const useHomeContext = (): HomeContext => {
  const { getRoleScope } = useAuth();

  return useMemo(() => {
    const { role, scope } = getRoleScope();
    const sessionUser = readSessionUser();
    const firstAssignment = getFirstAssignment(sessionUser);

    return {
      role,
      scope,
      user: sessionUser,
      source: hasSessionAccess(sessionUser, firstAssignment) ? "session" : "default",
    };
  }, []);
};
