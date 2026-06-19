import { useSession } from "@/auth/hooks/use-session";
import type { HomeContext } from "@/types/home/home-types";
import { getFirstAssignment, hasSessionAccess } from "../utils/home-session-utils";

export const useHomeContext = (): HomeContext => {
  const { user, role, scope, loading } = useSession();
  const firstAssignment = getFirstAssignment(user);

  return {
    role,
    scope,
    user,
    source: hasSessionAccess(user, firstAssignment) ? "session" : "default",
    status: loading ? "loading" : "ready",
  };
};
