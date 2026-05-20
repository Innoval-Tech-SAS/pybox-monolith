import React from "react";

import DefaultLayoutProps from "@types/interfaces/layouts/DefaultLayoutProps";

export const DefaultLayout: React.FC<DefaultLayoutProps> = ({ children }) => {
  return <>{children}</>;
};
