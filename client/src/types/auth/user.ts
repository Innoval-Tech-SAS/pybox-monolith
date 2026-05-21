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

export interface User {
  id?: number;
  fullname: string;
  profilePhoto: string;
  user: string;
  email: string;
  role: string;
  state: string;
}
