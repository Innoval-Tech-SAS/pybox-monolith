import { AuthPage } from "./auth/pages/auth-page";
import { SignUpPage } from "./auth/pages/sign-up-page";
import { NotFound } from "./ui/pages/not-found";

export const noAuthRouter = [
  {
    path: "/admin/sign-in",
    element: <AuthPage />,
  },
  {
    path: "/admin/sign-up",
    element: <SignUpPage />,
  },
  {
    path: "*",
    element: <NotFound />,
  },
];
