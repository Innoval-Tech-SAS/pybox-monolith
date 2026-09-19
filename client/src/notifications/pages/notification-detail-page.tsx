import { useParams } from "react-router";
import { BellOff } from "lucide-react";
import { ModuleBase } from "@/ui/components/common/module-base";
import { NotificationDetailView } from "@/notifications/components/notification-detail-view";
import { useNotificationDetail } from "@/notifications/hooks/use-notification-detail";
import { Loader } from "@/ui/components/loader/loader";
import EmptyState from "@/ui/components/common/empty-state";

export const NotificationDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { notification, loading, notFound } = useNotificationDetail(id);

  const breadcrumb = [{ label: "Notificaciones", path: "/notifications" }];

  if (loading) {
    return (
      <ModuleBase pageTitle="Notificación" breadcrumbItems={breadcrumb}>
        <Loader variant="section" />
      </ModuleBase>
    );
  }

  if (notFound || !notification) {
    return (
      <ModuleBase pageTitle="No encontrada" breadcrumbItems={breadcrumb}>
        <EmptyState icon={BellOff} title="Notificación no encontrada" className="py-20" />
      </ModuleBase>
    );
  }

  return (
    <ModuleBase pageTitle={notification.title} breadcrumbItems={breadcrumb}>
      <NotificationDetailView notification={notification} />
    </ModuleBase>
  );
};
