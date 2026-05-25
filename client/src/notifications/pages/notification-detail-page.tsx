import { useCallback, useEffect, useState } from "react";
import { useParams } from "react-router";
import { ModuleBase } from "@/ui/components/common/module-base";
import { useApiClient } from "@/hooks/use-api-client";
import type { AppNotification } from "@/types/notifications/notification";
import { NotificationDetailView } from "@/notifications/components/notification-detail-view";

export const NotificationDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { apiClient } = useApiClient();
  const [notification, setNotification] = useState<AppNotification | null>(null);
  const [loading, setLoading] = useState(true);
  const [notFound, setNotFound] = useState(false);

  const fetchData = useCallback(async () => {
    if (!id) return;
    setLoading(true);
    try {
      const data: AppNotification = await apiClient(`/notifications/${id}`);
      setNotification(data);
    } catch {
      setNotFound(true);
    } finally {
      setLoading(false);
    }
  }, [id, apiClient]);

  useEffect(() => { fetchData(); }, [fetchData]);

  const breadcrumb = [{ label: "Notificaciones", path: "/notifications" }];

  if (loading) {
    return (
      <ModuleBase pageTitle="Notificación" breadcrumbItems={breadcrumb}>
        <div className="flex items-center justify-center py-20 text-gray-400">Cargando...</div>
      </ModuleBase>
    );
  }

  if (notFound || !notification) {
    return (
      <ModuleBase pageTitle="No encontrada" breadcrumbItems={breadcrumb}>
        <div className="flex flex-col items-center justify-center py-20 gap-3">
          <p className="text-gray-500">Notificación no encontrada.</p>
        </div>
      </ModuleBase>
    );
  }

  return (
    <ModuleBase pageTitle={notification.title} breadcrumbItems={breadcrumb}>
      <NotificationDetailView notification={notification} />
    </ModuleBase>
  );
};
