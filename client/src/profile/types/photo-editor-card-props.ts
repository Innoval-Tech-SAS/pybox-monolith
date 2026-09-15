import type { useImageCropper } from "@/profile/hooks/use-image-cropper";

export interface PhotoEditorCardProps {
  cropper: ReturnType<typeof useImageCropper>;
}
