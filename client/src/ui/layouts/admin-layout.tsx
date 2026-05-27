import { useEffect, useState } from "react";
import { Outlet, useLocation } from "react-router";
import { ChatBubblesContainer } from "../../chat/components/chat-bubbles-container";
import { useSidebar } from "../../hooks/use-sidebar";
import { AsideMenu } from "../components/menu/aside-menu";
import { NavbarMenu } from "../components/menu/navbar-menu";
import { SidebarProvider } from "../contexts/providers/sidebar-provider";
import { signInNavbarItems, otherSignInItems, supportNavItems } from "../../config/navbar/sign-in-navbar-items";
import { Backdrop } from "../components/menu/backdrop";
import { useAuth } from "../../hooks/use-auth";
import { Scope } from "../../types/auth/role";
import { setSessionUser } from "../../auth/utils/auth-session-utils";
import { useHasAnyPermission } from "../../auth/hooks/use-has-any-permission";

const LayoutContent: React.FC = () => {
  useLocation(); // suscribe al router context → re-render en cada navegación
  const [, forceUpdate] = useState(0);
  const { isExpanded, isHovered, isMobileOpen } = useSidebar();
  const { getRoleScope, fetchMe } = useAuth();

  useEffect(() => {
    // Garantiza que la sesión esté actualizada al montar el layout por primera vez
    fetchMe()
      .then((me) => { setSessionUser(me); forceUpdate((n) => n + 1); })
      .catch(() => {});
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const { scope } = getRoleScope();
  const hasAnyPermission = useHasAnyPermission;

  const isOrgOrGlobal = scope === Scope.ORG || scope === Scope.GLOBAL;
  const navItems = isOrgOrGlobal ? signInNavbarItems : signInNavbarItems.slice(0, 1);
  const othersItems = isOrgOrGlobal
    ? otherSignInItems.filter((item) => !item.permission || hasAnyPermission(item.permission))
    : [];

  return (
    <div className="h-screen overflow-hidden flex flex-col xl:flex-row">
      <div>
        <AsideMenu navItems={navItems} othersItems={othersItems} othersLabel="Administración" supportItems={supportNavItems} supportLabel="Soporte" />
        <Backdrop />
      </div>
      <div
        className={`flex flex-col flex-1 transition-all duration-300 ease-in-out ${
          isExpanded || isHovered ? "lg:ml-72.5" : "lg:ml-22.5"
        } ${isMobileOpen ? "ml-0" : ""}`}
      >
        <NavbarMenu />
        <div className="flex flex-col flex-1 overflow-hidden p-4 mx-auto w-full max-w-(--breakpoint-2xl) md:p-6">
          <Outlet />
        </div>
      </div>
      <ChatBubblesContainer />
    </div>
  );
};

export const AdminLayout: React.FC = () => {
  return (
    <SidebarProvider>
      <LayoutContent />
    </SidebarProvider>
  );
};
