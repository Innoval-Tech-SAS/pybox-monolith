export interface RegisterRequest {
  firstname: string;
  lastname: string;
  email: string;
  password: string;
  phone_number: string;
  nationality: string;
}

export interface RegisterResponse {
  id: string;
  email: string;
}

export interface RoleAssignment {
  role?: string;
  scope?: string;
}

export interface User {
  id?: number;
  email: string;
  firstname?: string;
  lastname?: string;
  fullname?: string;
  phoneNumber?: string;
  authProvider?: string;
  nationality?: string;
  documentType?: string;
  documentNumber?: string;
  isActive?: boolean;
  profilePhoto?: string;
  role?: string;
  scope?: string;
  userRole?: string;
  userScope?: string;
  roles?: RoleAssignment[];
  roleAssignments?: RoleAssignment[];
}
