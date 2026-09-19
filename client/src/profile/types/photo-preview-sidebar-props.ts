import type { useImageCropper } from "@/profile/hooks/use-image-cropper";

export interface PhotoPreviewSidebarProps {
  cropper: ReturnType<typeof useImageCropper>;
}
