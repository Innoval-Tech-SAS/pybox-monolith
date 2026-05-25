import { Outlet } from "react-router";
import { useSidebar } from "../../hooks/use-sidebar";
import { AsideMenu } from "../components/menu/aside-menu";
import { NavbarMenu } from "../components/menu/navbar-menu";
import { SidebarProvider } from "../contexts/providers/sidebar-provider";
import { signInNavbarItems, otherSignInItems } from "../../config/navbar/sign-in-navbar-items";
import { Backdrop } from "../components/menu/backdrop";
import { useAuth } from "../../hooks/use-auth";
import { Scope } from "../../types/auth/role";

const LayoutContent: React.FC = () => {
  const { isExpanded, isHovered, isMobileOpen } = useSidebar();
  const { getRoleScope } = useAuth();
  const { scope } = getRoleScope();

  const isOrgOrGlobal = scope === Scope.ORG || scope === Scope.GLOBAL;
  const navItems = isOrgOrGlobal ? signInNavbarItems : signInNavbarItems.slice(0, 1);
  const othersItems = isOrgOrGlobal ? otherSignInItems : [];

  return (
    <div className="h-screen overflow-hidden flex flex-col xl:flex-row">
      <div>
        <AsideMenu navItems={navItems} othersItems={othersItems} othersLabel="Administración" />
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
