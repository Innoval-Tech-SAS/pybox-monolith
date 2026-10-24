export enum Role {
  ADMIN = "ADMINISTRADOR",
  CS = "ATENCION_AL_CLIENTE",
  USER = "USUARIO",
}

export enum Scope {
  GLOBAL = "GLOBAL",
  ORG = "ORGANIZACION",
  SELF = "PROPIO",
}

export type RoleScope =
  | { role: Role.ADMIN;    scope: Scope.GLOBAL }
  | { role: Role.CS;       scope: Scope.GLOBAL }
  | { role: Role.ADMIN;    scope: Scope.ORG }
  | { role: Role.CS;       scope: Scope.ORG }
  | { role: Role.USER;     scope: Scope.ORG }
  | { role: Role.USER;     scope: Scope.SELF };

export const DEFAULT_ROLE_SCOPE: RoleScope = { role: Role.USER, scope: Scope.SELF };
