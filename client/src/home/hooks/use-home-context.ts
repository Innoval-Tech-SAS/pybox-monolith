import { useEffect, useState } from "react";
import { useAuth } from "@/hooks/use-auth";
import { setSessionUser } from "@/auth/utils/auth-session-utils";
import type { HomeContext } from "@/types/home/home-types";
import { getFirstAssignment, hasSessionAccess, readSessionUser } from "../utils/home-session-utils";

export const useHomeContext = (): HomeContext => {
  const { getRoleScope, fetchMe } = useAuth();
  const [, refresh] = useState(0);

  useEffect(() => {
    fetchMe()
      .then((me) => {
        if (!me) return;
        setSessionUser(me);
        refresh((n) => n + 1);
      })
      .catch(() => {});
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const { role, scope } = getRoleScope();
  const sessionUser = readSessionUser();
  const firstAssignment = getFirstAssignment(sessionUser);

  return {
    role,
    scope,
    user: sessionUser,
    source: hasSessionAccess(sessionUser, firstAssignment) ? "session" : "default",
  };
};
