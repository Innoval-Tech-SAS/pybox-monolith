export interface AppNotification {
  id: number;
  title: string;
  body: string;
  category: string;
  isRead: boolean;
  createdAt: string;
  link?: string;
}
