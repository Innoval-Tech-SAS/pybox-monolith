import { Navigate } from "react-router";
import { AuthPage } from "./auth/pages/auth-page";
import { SignUpPage } from "./auth/pages/sign-up-page";
import { MyCompaniesPage } from "./companies/pages/my-companies-page";
import { CreateOrgPage } from "./companies/pages/create-org-page";
import { CreatePortfolioPage } from "./companies/pages/create-portfolio-page";
import { MyPortfoliosPage } from "./companies/pages/my-portfolios-page";
import { HomePage } from "./home/pages/home-page";
import { ProfilePage } from "./profile/pages/profile-page";
import { UsersPage } from "./users/pages/users-page";
import { UserDetailPage } from "./users/pages/user-detail-page";
import { UserEditPage } from "./users/pages/user-edit-page";
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
  {
    path: "/my-companies",
    element: <MyCompaniesPage />,
  },
  {
    path: "/my-companies/add",
    element: <CreateOrgPage />,
  },
  {
    path: "/my-companies/portfolios",
    element: <MyPortfoliosPage />,
  },
  {
    path: "/my-companies/add-portfolio",
    element: <CreatePortfolioPage />,
  },
  {
    path: "/my-users",
    element: <UsersPage />,
  },
  {
    path: "/my-users/:id",
    element: <UserDetailPage />,
  },
  {
    path: "/my-users/:id/edit",
    element: <UserEditPage />,
  },
];
