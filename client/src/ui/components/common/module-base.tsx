import React from "react";
import { ArrowLeft } from "lucide-react";
import { useNavigate } from "react-router";
import { Breadcrumb } from "./breadcrumb";
import type { ModuleBaseProps } from "@/types/props/module-base-props";

export const ModuleBase: React.FC<ModuleBaseProps> = ({
  pageTitle,
  pageIcon,
  breadcrumbItems,
  showBack,
  children,
}) => {
  const navigate = useNavigate();
  const hasBack = showBack ?? !!breadcrumbItems?.length;

  return (
    <div className="flex flex-col flex-1 overflow-hidden">
      <Breadcrumb pageTitle={pageTitle} pageIcon={pageIcon} items={breadcrumbItems} />
      {/* pb-24: dentro de este scroll el botón flotante de chats (fixed bottom-6
          right-6, siempre encima) puede tapar el CTA final de un wizard/form corto
          si no hay suficiente aire debajo. */}
      <div className="flex flex-col flex-1 min-h-0 overflow-y-auto custom-scrollbar rounded-2xl border border-gray-200 bg-white p-5 pb-24 dark:border-gray-800 dark:bg-white/3 lg:p-6 lg:pb-24">
        {hasBack && (
          <button
            id="tour-back-btn"
            onClick={() => navigate(-1)}
            className="mb-5 flex items-center gap-2 text-sm text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
          >
            <ArrowLeft size={16} />
            Volver
          </button>
        )}
        {children}
      </div>
    </div>
  );
};
