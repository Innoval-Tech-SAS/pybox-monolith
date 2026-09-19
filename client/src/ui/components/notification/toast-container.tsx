import React, { useState } from "react";
import { useToast } from "@/context/toast-context";
import { Notification } from "./notification";
import {
  TOAST_FRONT_HEIGHT,
  TOAST_MAX_VISIBLE,
  TOAST_STACK_OFFSET,
  TOAST_STACK_SCALE,
} from "@/constants/notifications/toast-container";

export const ToastContainer: React.FC = () => {
  const { toasts, dismiss } = useToast();
  const [expanded, setExpanded] = useState(false);

  if (toasts.length === 0) return null;

  const reversed = [...toasts].reverse();
  const visible = reversed.slice(0, TOAST_MAX_VISIBLE);

  const collapsedHeight = TOAST_FRONT_HEIGHT + (visible.length - 1) * TOAST_STACK_OFFSET;

  return (
    <div
      className="fixed bottom-5 right-5 z-100000 w-80"
      style={{ height: expanded ? "auto" : collapsedHeight }}
      onMouseEnter={() => setExpanded(true)}
      onMouseLeave={() => setExpanded(false)}
    >
      <div className={expanded ? "flex flex-col gap-2" : "relative"}>
        {visible.map((toast, i) => {
          const style: React.CSSProperties = expanded
            ? { transition: "all 0.25s ease" }
            : {
                position: "absolute",
                bottom: 0,
                left: 0,
                right: 0,
                transform: `translateY(-${i * TOAST_STACK_OFFSET}px) scaleX(${1 - i * TOAST_STACK_SCALE})`,
                zIndex: TOAST_MAX_VISIBLE - i,
                opacity: i === 2 ? 0.6 : 1,
                transition: "all 0.25s ease",
              };

          return (
            <Notification
              key={toast.id}
              {...toast}
              onClose={dismiss}
              style={style}
              className={!expanded && i > 0 ? "pointer-events-none" : ""}
            />
          );
        })}
      </div>
    </div>
  );
};
