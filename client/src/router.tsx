import { AuthPage } from "./auth/pages/auth-page";
import { NotFound } from "./ui/pages/not-found";

export const noAuthRouter = [
  {
    path: "/admin/sign-in",
    element: <AuthPage />,
  },
  {
    path: "*",
    element: <NotFound />,
  },
];
