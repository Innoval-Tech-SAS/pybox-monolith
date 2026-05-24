export interface AppNotification {
  id: string;
  title: string;
  body: string;
  category: string;
  isRead: boolean;
  createdAt: string;
  link?: string;
}
