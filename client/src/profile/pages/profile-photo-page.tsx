import { PageMeta } from "@/ui/pages/page-meta";
import { ModuleBase } from "@/ui/components/common/module-base";
import { useImageCropper } from "../hooks/use-image-cropper";
import { useProfilePhotoTour } from "../hooks/use-profile-photo-tour";
import { PhotoEditorCard } from "../components/photo-editor-card";
import { PhotoPreviewSidebar } from "../components/photo-preview-sidebar";

export const ProfilePhotoPage: React.FC = () => {
  const cropper = useImageCropper();
  useProfilePhotoTour(true);

  return (
    <>
      <PageMeta title="Foto de perfil" description="Actualiza tu foto de perfil" />
      <ModuleBase pageTitle="Foto de perfil" breadcrumbItems={[{ label: "Perfil", path: "/profile" }]}>
        <div className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_320px]">
          <PhotoEditorCard cropper={cropper} />
          <PhotoPreviewSidebar cropper={cropper} />
        </div>
      </ModuleBase>
    </>
  );
};
