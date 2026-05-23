import React, {
  createContext,
  useCallback,
  useContext,
  useRef,
  useState,
} from "react";
import type { NotificationVariant } from "@/types/props/notification-props";
import type { ToastContextValue, Toast } from "@/types/contexts/toast-context-types";
import type { ToastProviderProps } from "@/types/props/provider-props";

const ToastContext = createContext<ToastContextValue | null>(null);

const DEFAULT_DURATION = 5000;

export const ToastProvider: React.FC<ToastProviderProps> = ({
  children,
  duration = DEFAULT_DURATION,
}) => {
  const [toasts, setToasts] = useState<Toast[]>([]);
  const timers = useRef<Map<string, ReturnType<typeof setTimeout>>>(new Map());

  const dismiss = useCallback((id: string) => {
    clearTimeout(timers.current.get(id));
    timers.current.delete(id);
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const add = useCallback(
    (variant: NotificationVariant, title: string, description?: string) => {
      const id = crypto.randomUUID();
      setToasts((prev) => [...prev, { id, variant, title, description }]);
      const timer = setTimeout(() => dismiss(id), duration);
      timers.current.set(id, timer);
    },
    [dismiss, duration],
  );

  const success = useCallback(
    (t: string, d?: string) => add("success", t, d),
    [add],
  );
  const error = useCallback(
    (t: string, d?: string) => add("error", t, d),
    [add],
  );
  const info = useCallback((t: string, d?: string) => add("info", t, d), [add]);
  const warning = useCallback(
    (t: string, d?: string) => add("warning", t, d),
    [add],
  );

  return (
    <ToastContext.Provider
      value={{ toasts, dismiss, success, error, info, warning }}
    >
      {children}
    </ToastContext.Provider>
  );
};

export const useToast = (): ToastContextValue => {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error("useToast must be used inside ToastProvider");
  return ctx;
};
