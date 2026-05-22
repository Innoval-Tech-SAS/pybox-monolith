import { Outlet } from "react-router";
import { useSidebar } from "../../hooks/use-sidebar";
import { AsideMenu } from "../components/menu/aside-menu";
import { NavbarMenu } from "../components/menu/navbar-menu";
import { SidebarProvider } from "../contexts/providers/sidebar-provider";
import { signInNavbarItems, otherSignInItems } from "../../config/navbar/sign-in-navbar-items";
import { Backdrop } from "../components/menu/backdrop";

const LayoutContent: React.FC = () => {
  const { isExpanded, isHovered, isMobileOpen } = useSidebar();

  return (
    <div className="h-screen overflow-hidden xl:flex">
      <div>
        <AsideMenu navItems={signInNavbarItems} othersItems={otherSignInItems} />
        <Backdrop />
      </div>
      <div
        className={`flex flex-col flex-1 transition-all duration-300 ease-in-out ${
          isExpanded || isHovered ? "lg:ml-72.5" : "lg:ml-22.5"
        } ${isMobileOpen ? "ml-0" : ""}`}
      >
        <NavbarMenu />
        <div className="flex-1 overflow-y-auto p-4 mx-auto w-full max-w-(--breakpoint-2xl) md:p-6">
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
