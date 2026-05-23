import React from "react";
import { Breadcrumb } from "./breadcrumb";
import { BreadcrumbItem } from "@/types/props/breadcrumb-props";

interface ModuleBaseProps {
  pageTitle: string;
  sectionTitle?: string;
  breadcrumbItems?: BreadcrumbItem[];
  children: React.ReactNode;
}

export const ModuleBase: React.FC<ModuleBaseProps> = ({
  pageTitle,
  sectionTitle,
  breadcrumbItems,
  children,
}) => (
  <div className="flex flex-col flex-1 overflow-hidden">
    <Breadcrumb pageTitle={pageTitle} items={breadcrumbItems} />
    <div className="flex-1 overflow-y-auto rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-white/3 lg:p-6">
      {sectionTitle && (
        <h3 className="mb-5 text-lg font-semibold text-gray-800 dark:text-white/90 lg:mb-7">
          {sectionTitle}
        </h3>
      )}
      {children}
    </div>
  </div>
);
