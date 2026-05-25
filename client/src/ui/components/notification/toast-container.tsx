import React from "react";
import { useToast } from "@/context/toast-context";
import { Notification } from "./notification";

export const ToastContainer: React.FC = () => {
  const { toasts, dismiss } = useToast();

  if (toasts.length === 0) return null;

  return (
    <div className="fixed bottom-5 right-5 z-9999 flex flex-col gap-3 items-end">
      {toasts.map((toast) => (
        <Notification key={toast.id} {...toast} onClose={dismiss} />
      ))}
    </div>
  );
};
