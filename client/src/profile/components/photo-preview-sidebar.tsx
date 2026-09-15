import { Camera, RotateCcw, Save, Upload } from "lucide-react";
import { OUTPUT_SIZE, PREVIEW_SIZE, VIEW_SIZE } from "@/profile/constants/photo-cropper";
import type { PhotoPreviewSidebarProps } from "@/profile/types/photo-preview-sidebar-props";

const previewScale = PREVIEW_SIZE / VIEW_SIZE;

export const PhotoPreviewSidebar: React.FC<PhotoPreviewSidebarProps> = ({ cropper }) => {
  const { sourceImage, metrics, loading, handleSave, resetCrop } = cropper;

  return (
    <aside className="rounded-2xl border border-gray-200 p-5 dark:border-gray-800 lg:p-6">
      <h3 className="mb-4 text-sm font-semibold text-gray-800 dark:text-white/90">
        Vista final
      </h3>
      <div className="flex items-center gap-4">
        <div
          className="relative overflow-hidden rounded-full border border-gray-200 bg-gray-100 dark:border-gray-700 dark:bg-gray-800"
          style={{ width: PREVIEW_SIZE, height: PREVIEW_SIZE }}
        >
          {sourceImage && metrics ? (
            <img
              src={sourceImage.url}
              alt="Vista previa"
              draggable={false}
              className="absolute left-0 top-0 max-w-none select-none"
              style={{
                width: metrics.renderedWidth * previewScale,
                height: metrics.renderedHeight * previewScale,
                transform: `translate(${metrics.topLeftX * previewScale}px, ${metrics.topLeftY * previewScale}px)`,
              }}
            />
          ) : (
            <div className="flex h-full w-full items-center justify-center text-gray-400">
              <Camera size={24} />
            </div>
          )}
        </div>
        <div className="min-w-0">
          <p className="text-sm font-medium text-gray-800 dark:text-white/90">
            Avatar circular
          </p>
          <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
            Salida real: {OUTPUT_SIZE} x {OUTPUT_SIZE} px.
          </p>
        </div>
      </div>

      <div className="mt-6 space-y-3">
        <button
          type="button"
          onClick={resetCrop}
          disabled={!sourceImage || loading}
          className="inline-flex w-full items-center justify-center gap-2 rounded-lg border border-gray-300 bg-white px-4 py-3 text-sm font-medium text-gray-700 shadow-theme-xs transition hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-50 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-white/3"
        >
          <RotateCcw size={17} />
          Restablecer recorte
        </button>
        <button
          id="tour-photo-upload"
          type="button"
          onClick={handleSave}
          disabled={!sourceImage || loading}
          className="inline-flex w-full items-center justify-center gap-2 rounded-lg bg-brand-500 px-4 py-3 text-sm font-medium text-white shadow-theme-xs transition hover:bg-brand-600 disabled:cursor-not-allowed disabled:bg-brand-300"
        >
          {loading ? <Upload size={17} /> : <Save size={17} />}
          {loading ? "Subiendo" : "Recortar y guardar"}
        </button>
      </div>
    </aside>
  );
};
