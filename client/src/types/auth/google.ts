export interface GooglePayload {
  email: string;
  givenName?: string;
  familyName?: string;
}

export interface GoogleCredentialResponse {
  credential: string;
}

declare global {
  interface Window {
    google?: {
      accounts: {
        id: {
          initialize: (config: {
            client_id: string;
            callback: (res: GoogleCredentialResponse) => void;
          }) => void;
          prompt: () => void;
          cancel: () => void;
          renderButton: (
            container: HTMLElement,
            config: {
              type?: "standard" | "icon";
              theme?: "outline" | "filled_blue" | "filled_black";
              size?: "large" | "medium" | "small";
              width?: number;
            },
          ) => void;
        };
      };
    };
  }
}
