import { Navigate } from "react-router";
import { AuthPage } from "./auth/pages/auth-page";
import { SignUpPage } from "./auth/pages/sign-up-page";
import { HomePage } from "./home/pages/home-page";
import { ProfilePage } from "./profile/pages/profile-page";
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

export const authRouter = [
  {
    path: "/",
    element: <Navigate to="/dashboard" replace />,
  },
  {
    path: "/dashboard",
    element: <HomePage />,
  },
  {
    path: "/profile",
    element: <ProfilePage />,
  },
];
