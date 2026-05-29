import { Navigate } from "react-router";
import { AuthPage } from "./auth/pages/auth-page";
import { SignUpPage } from "./auth/pages/sign-up-page";
import { MyCompaniesPage } from "./companies/pages/my-companies-page";
import { CreateOrgPage } from "./companies/pages/create-org-page";
import { CreatePortfolioPage } from "./companies/pages/create-portfolio-page";
import { EditPortfolioPage } from "./companies/pages/edit-portfolio-page";
import { MyPortfoliosPage } from "./companies/pages/my-portfolios-page";
import { PortfolioDebtorsPage } from "./companies/pages/portfolio-debtors-page";
import { PortfolioSettingsPage } from "./companies/pages/portfolio-settings-page";
import { HomePage } from "./home/pages/home-page";
import { NotificationDetailPage } from "./notifications/pages/notification-detail-page";
import { NotificationsPage } from "./notifications/pages/notifications-page";
import { ProfilePhotoPage } from "./profile/pages/profile-photo-page";
import { ProfilePage } from "./profile/pages/profile-page";
import { ProfileEditPage } from "./profile/pages/profile-edit-page";
import { TicketDetailPage } from "./support/pages/ticket-detail-page";
import { TicketsPage } from "./support/pages/tickets-page";
import { FileViewerPage } from "./support/pages/file-viewer-page";
import { UsersPage } from "./users/pages/users-page";
import { UserDetailPage } from "./users/pages/user-detail-page";
import { UserEditPage } from "./users/pages/user-edit-page";
import { UserSettingsPage } from "./users/pages/user-settings-page";
import { UserPortfoliosPage } from "./users/pages/user-portfolios-page";
import { CreateUserPage } from "./users/pages/create-user-page";
import { ChatPage } from "./chat/pages/chat-page";
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
    element: <Navigate to="/home" replace />,
  },
  {
    path: "/home",
    element: <HomePage />,
  },
  {
    path: "/profile",
    element: <ProfilePage />,
  },
  {
    path: "/profile/edit",
    element: <ProfileEditPage />,
  },
  {
    path: "/profile/photo",
    element: <ProfilePhotoPage />,
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
    path: "/my-companies/portfolios/upload/append",
    element: <EditPortfolioPage />,
  },
  {
    path: "/my-companies/portfolios/upload/update",
    element: <EditPortfolioPage />,
  },
  {
    path: "/my-companies/portfolios/debtors",
    element: <PortfolioDebtorsPage />,
  },
  {
    path: "/my-companies/portfolios/settings",
    element: <PortfolioSettingsPage />,
  },
  {
    path: "/my-users",
    element: <UsersPage />,
  },
  {
    path: "/my-companies/users",
    element: <UsersPage />,
  },
  {
    path: "/my-users/add",
    element: <CreateUserPage />,
  },
  {
    path: "/my-users/:id",
    element: <UserDetailPage />,
  },
  {
    path: "/my-users/:id/edit",
    element: <UserEditPage />,
  },
  {
    path: "/my-users/:id/settings",
    element: <UserSettingsPage />,
  },
  {
    path: "/my-users/:id/portfolios",
    element: <UserPortfoliosPage />,
  },
  {
    path: "/notifications",
    element: <NotificationsPage />,
  },
  {
    path: "/notifications/:id",
    element: <NotificationDetailPage />,
  },
  {
    path: "/chats",
    element: <ChatPage />,
  },
  {
    path: "/cs/tickets",
    element: <TicketsPage />,
  },
  {
    path: "/cs/tickets/:id",
    element: <TicketDetailPage />,
  },
  {
    path: "/files/viewer",
    element: <FileViewerPage />,
  },
];
