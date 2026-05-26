export interface ManagedUserCreate {
  firstname: string;
  lastname: string;
  email: string;
  phoneNumber: string;
  password: string;
  role: "ADMINISTRADOR" | "ATENCION AL CLIENTE";
}

export interface ManagedUserResponse {
  id: number;
  fullName: string;
  email: string;
  phoneNumber: string;
  role: string;
  scope: string;
}
