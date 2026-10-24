export interface ManagedUserCreate {
  firstname: string;
  lastname: string;
  email: string;
  phoneNumber: string;
  password: string;
  role: "ADMINISTRADOR" | "ATENCION_AL_CLIENTE" | "USUARIO";
}

export interface ManagedUserResponse {
  id: string;
  fullName: string;
  email: string;
  phoneNumber: string;
  role: string;
  scope: string;
}
