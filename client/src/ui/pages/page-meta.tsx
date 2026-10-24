import { useEffect } from "react";
import { Helmet } from "react-helmet-async";
import type { PageMetaProps } from "@/types/props/page-meta-props";

export const PageMeta = ({
  title,
  description,
}: PageMetaProps) => {
  useEffect(() => {
    document.title = title;
  }, [title]);

  return (
    <Helmet>
      <title>{title}</title>
      <meta name="description" content={description} />
    </Helmet>
  );
};
