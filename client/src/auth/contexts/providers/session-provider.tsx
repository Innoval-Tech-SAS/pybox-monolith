import { useCallback, useEffect, useState } from "react";
import { useAuth } from "@/hooks/use-auth";
import { setSessionUser } from "@/auth/utils/auth-session-utils";
import type { User } from "@/types/auth/user";
import type { ChildrenProps } from "@/types/props/provider-props";
import { SessionContext } from "../session-context";

export const SessionProvider: React.FC<ChildrenProps> = ({ children }) => {
  const { user: sessionUser, getRoleScope, fetchMe } = useAuth();
  const [user, setUser] = useState<User | null>(sessionUser);
  const [loading, setLoading] = useState(true);

  const refetch = useCallback(async () => {
    setLoading(true);
    try {
      const me = await fetchMe();
      setSessionUser(me);
      setUser(me);
    } catch {
      // keep whatever is already in session storage
    } finally {
      setLoading(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    refetch();
  }, [refetch]);

  const { role, scope } = getRoleScope();

  return (
    <SessionContext.Provider value={{ user, role, scope, loading, refetch }}>
      {children}
    </SessionContext.Provider>
  );
};
