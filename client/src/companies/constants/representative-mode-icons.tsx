import { User, UserPlus, Users } from "lucide-react";

export const REPRESENTATIVE_MODE_ICONS: Record<"user" | "users" | "user-plus", React.ReactNode> = {
  user: <User size={16} />,
  users: <Users size={16} />,
  "user-plus": <UserPlus size={16} />,
};
