import { useMemo } from "react";

import type { HomeContext } from "@/types/home/home-types";
import {
  DEFAULT_HOME_ROLE,
  DEFAULT_HOME_SCOPE,
  getFirstAssignment,
  hasSessionAccess,
  readSessionUser,
} from "../utils/home-session-utils";

export const useHomeContext = (): HomeContext => {
  return useMemo(() => {
    const sessionUser = readSessionUser();
    const firstAssignment = getFirstAssignment(sessionUser);

    const role =
      sessionUser?.userRole ??
      sessionUser?.role ??
      firstAssignment?.role ??
      DEFAULT_HOME_ROLE;
    const scope =
      sessionUser?.userScope ??
      sessionUser?.scope ??
      firstAssignment?.scope ??
      DEFAULT_HOME_SCOPE;

    return {
      role,
      scope,
      user: sessionUser,
      source: hasSessionAccess(sessionUser, firstAssignment)
        ? "session"
        : "default",
    };
  }, []);
};
