import { Outlet, useLocation } from "react-router";
import { ChatBubblesContainer } from "../../chat/components/chat-bubbles-container";
import { useSidebar } from "../../hooks/use-sidebar";
import { AsideMenu } from "../components/menu/aside-menu";
import { NavbarMenu } from "../components/menu/navbar-menu";
import { SidebarProvider } from "../contexts/providers/sidebar-provider";
import { OrgModuleProvider } from "../../companies/contexts/providers/org-module-provider";
import { SessionProvider } from "../../auth/contexts/providers/session-provider";
import { OnboardingGuard } from "../../onboarding/onboarding-guard";
import { MfaGuard } from "../../auth/components/mfa-guard";
import { signInNavbarItems, otherSignInItems, supportNavItems } from "../../config/navbar/sign-in-navbar-items";
import { Backdrop } from "../components/menu/backdrop";
import { useSession } from "../../auth/hooks/use-session";
import { Scope } from "../../types/auth/role";
import { useHasAnyPermission } from "../../auth/hooks/use-has-any-permission";

const LayoutContent: React.FC = () => {
  const location = useLocation();
  const { isExpanded, isHovered, isMobileOpen } = useSidebar();
  const { scope } = useSession();
  const hasAnyPermission = useHasAnyPermission;

  const isOrgOrGlobal = scope === Scope.ORG || scope === Scope.GLOBAL;
  const navItems = isOrgOrGlobal ? signInNavbarItems : signInNavbarItems.slice(0, 1);
  const othersItems = isOrgOrGlobal
    ? otherSignInItems.filter((item) => {
        if (item.globalOnly) return scope === Scope.GLOBAL;
        return !item.permission || hasAnyPermission(item.permission);
      })
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
          <OnboardingGuard>
            <MfaGuard>
              <OrgModuleProvider>
                <Outlet />
              </OrgModuleProvider>
            </MfaGuard>
          </OnboardingGuard>
        </div>
      </div>
      {location.pathname !== "/chats" && <ChatBubblesContainer />}
    </div>
  );
};

export const AdminLayout: React.FC = () => {
  return (
    <SidebarProvider>
      <SessionProvider>
        <LayoutContent />
      </SessionProvider>
    </SidebarProvider>
  );
};
