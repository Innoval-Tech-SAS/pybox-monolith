export interface PermissionCatalogEntry {
  name: string;
  label: string | null;
  description: string | null;
}

export interface UserPermissionEntry {
  name: string;
  effect: "OTORGAR" | "REVOCAR";
}

export interface UserPermissionList {
  permissions: UserPermissionEntry[];
}
