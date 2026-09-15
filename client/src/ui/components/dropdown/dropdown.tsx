import { useEffect, useRef } from "react";
import { createPortal } from "react-dom";

import { usePortalDropdown } from "@/hooks/use-portal-dropdown";
import { DropdownProps } from "@/types/props/dropdown-props";

export const Dropdown: React.FC<DropdownProps> = ({
  isOpen,
  onClose,
  children,
  className = "",
  triggerRef,
  align = "right",
}) => {
  const portalMode = !!triggerRef;

  // Modo portal: el panel cuelga de document.body con position: fixed anclado al
  // disparador, evitando que ancestros con overflow lo recorten. El hook gestiona
  // el reposicionamiento y el click-outside.
  const { dropdownRef, dropdownStyle } = usePortalDropdown<HTMLElement, HTMLDivElement>({
    open: isOpen && portalMode,
    onClose,
    align,
    matchWidth: false,
    triggerRef,
  });

  // Modo inline (heredado): click-outside vía el hermano .dropdown-toggle.
  const inlineRef = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (portalMode) return;
    const handleClickOutside = (event: MouseEvent) => {
      if (
        inlineRef.current &&
        !inlineRef.current.contains(event.target as Node) &&
        !(event.target as HTMLElement).closest(".dropdown-toggle")
      ) {
        onClose();
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [onClose, portalMode]);

  useEffect(() => {
    if (!isOpen) return;

    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        event.stopPropagation();
        onClose();
        (triggerRef?.current as HTMLElement | null)?.focus();
      }
    };

    document.addEventListener("keydown", handleEscape);
    return () => document.removeEventListener("keydown", handleEscape);
  }, [isOpen, onClose, triggerRef]);

  if (!isOpen) return null;

  if (portalMode) {
    if (!dropdownStyle) return null;
    return createPortal(
      <div
        ref={dropdownRef}
        role="menu"
        style={dropdownStyle}
        className={`rounded-xl border border-gray-200 bg-white shadow-theme-lg dark:border-gray-800 dark:bg-gray-dark ${className}`}
      >
        {children}
      </div>,
      document.body,
    );
  }

  return (
    <div
      ref={inlineRef}
      role="menu"
      className={`absolute z-40  right-0 mt-2  rounded-xl border border-gray-200 bg-white  shadow-theme-lg dark:border-gray-800 dark:bg-gray-dark ${className}`}
    >
      {children}
    </div>
  );
};
