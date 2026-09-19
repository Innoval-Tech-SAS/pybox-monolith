export interface LoginCredentials {
  email: string;
  password: string;
}

export interface OAuthRegisterRequest {
  provider: string;
  token: string;
  phoneNumber?: string;
  nationality?: string;
}

export interface AuthTokenResponse {
  accessToken: string;
  refreshToken?: string;
  tokenType?: string;
  authProvider?: string;
}
