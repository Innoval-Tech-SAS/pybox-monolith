import { AdminGlobalHome } from "./admin-global-home";
import { AdminOrganizationHome } from "./admin-organization-home";
import { CustomerServiceHome } from "./customer-service-home";
import { DefaultHome } from "./default-home";
import { OrganizationUserHome } from "./organization-user-home";
import { SelfUserHome } from "./self-user-home";
import type { RoleScopeHomeProps } from "@/types/props/home-props";
import { normalizeAccessValue } from "../utils/access-utils";

export const RoleScopeHome: React.FC<RoleScopeHomeProps> = ({
  role,
  scope,
}) => {
  const normalizedRole = normalizeAccessValue(role);
  const normalizedScope = normalizeAccessValue(scope);

  if (normalizedRole === "ADMINISTRADOR" && normalizedScope === "GLOBAL") {
    return <AdminGlobalHome />;
  }

  if (
    normalizedRole === "ADMINISTRADOR" &&
    normalizedScope === "ORGANIZATION"
  ) {
    return <AdminOrganizationHome />;
  }

  if (normalizedRole === "ATENCION AL CLIENTE") {
    return <CustomerServiceHome />;
  }

  if (
    normalizedRole === "USUARIO ORGANIZACION" ||
    normalizedScope === "ORGANIZATION"
  ) {
    return <OrganizationUserHome />;
  }

  if (normalizedRole === "USUARIO" || normalizedScope === "SELF") {
    return <SelfUserHome />;
  }

  return <DefaultHome />;
};
