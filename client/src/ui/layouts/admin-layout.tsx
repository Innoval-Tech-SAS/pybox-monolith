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
import { signInNavbarItems, otherSignInItems, selfNavbarItems, supportNavItems } from "../../config/navbar/sign-in-navbar-items";
import { Backdrop } from "../components/menu/backdrop";
import { useSession } from "../../auth/hooks/use-session";
import { Role, Scope } from "../../types/auth/role";
import { useHasAnyPermission } from "../../auth/hooks/use-has-any-permission";
import { useSidebarLogo } from "../../companies/hooks/use-sidebar-logo";

const LayoutContent: React.FC = () => {
  const location = useLocation();
  const { isExpanded, isHovered, isMobileOpen } = useSidebar();
  const { role, scope } = useSession();
  const { logoUrl } = useSidebarLogo();
  const hasAnyPermission = useHasAnyPermission;

  const isOrgOrGlobal = scope === Scope.ORG || scope === Scope.GLOBAL;
  // SELF (titular): Inicio (calendario) + Mis Créditos. ORG/GLOBAL: nav completo.
  const navItems = isOrgOrGlobal ? signInNavbarItems : [signInNavbarItems[0], ...selfNavbarItems];
  const othersItems = isOrgOrGlobal
    ? otherSignInItems.filter((item) => {
        if (item.adminGlobalOnly) return scope === Scope.GLOBAL && role === Role.ADMIN;
        if (item.globalOnly) return scope === Scope.GLOBAL;
        if (item.hiddenForGlobalCs && scope === Scope.GLOBAL && role === Role.CS) return false;
        return !item.permission || hasAnyPermission(item.permission);
      })
    : [];

  return (
    <OnboardingGuard>
      <MfaGuard>
        <div className="h-screen overflow-hidden flex flex-col xl:flex-row">
          <div>
            <AsideMenu navItems={navItems} othersItems={othersItems} othersLabel="Administración" supportItems={supportNavItems} supportLabel="Soporte" logoUrl={logoUrl} />
            <Backdrop />
          </div>
          <div
            className={`flex flex-col flex-1 min-h-0 min-w-0 transition-all duration-300 ease-in-out ${
              isExpanded || isHovered ? "lg:ml-72.5" : "lg:ml-22.5"
            } ${isMobileOpen ? "ml-0" : ""}`}
          >
            <NavbarMenu logoUrl={logoUrl} />
            <main
              id="main-content"
              className="flex flex-col flex-1 overflow-hidden p-4 mx-auto w-full max-w-(--breakpoint-2xl) md:p-6"
            >
              <OrgModuleProvider>
                <Outlet />
              </OrgModuleProvider>
            </main>
          </div>
          {location.pathname !== "/chats" && <ChatBubblesContainer />}
        </div>
      </MfaGuard>
    </OnboardingGuard>
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
