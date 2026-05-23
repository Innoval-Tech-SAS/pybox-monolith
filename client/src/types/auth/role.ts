export enum Role {
  ADMIN = "ADMINISTRADOR",
  CS = "ATENCION AL CLIENTE",
  USER_ORG = "USUARIO ORGANIZACIÓN",
  USER = "USUARIO",
}

export enum Scope {
  GLOBAL = "GLOBAL",
  ORG = "ORGANIZATION",
  SELF = "SELF",
}

export type RoleScope =
  | { role: Role.ADMIN;    scope: Scope.GLOBAL }
  | { role: Role.CS;       scope: Scope.GLOBAL }
  | { role: Role.ADMIN;    scope: Scope.ORG }
  | { role: Role.CS;       scope: Scope.ORG }
  | { role: Role.USER_ORG; scope: Scope.ORG }
  | { role: Role.USER;     scope: Scope.SELF };

export const DEFAULT_ROLE_SCOPE: RoleScope = { role: Role.USER, scope: Scope.SELF };
