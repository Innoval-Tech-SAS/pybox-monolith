import { Camera, ImagePlus, ZoomIn } from "lucide-react";
import { OUTPUT_SIZE, VIEW_SIZE, MIN_ZOOM, MAX_ZOOM, formatFileSize } from "@/profile/constants/photo-cropper";
import type { PhotoEditorCardProps } from "@/profile/types/photo-editor-card-props";

export const PhotoEditorCard: React.FC<PhotoEditorCardProps> = ({ cropper }) => {
  const {
    fileInputRef,
    imageRef,
    sourceImage,
    metrics,
    zoom,
    localError,
    error,
    handleFileChange,
    handleZoomChange,
    handlePointerDown,
    handlePointerMove,
    stopDragging,
  } = cropper;

  return (
    <section className="rounded-2xl border border-gray-200 p-5 dark:border-gray-800 lg:p-6">
      <div className="mb-5 flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <h3 className="text-lg font-semibold text-gray-800 dark:text-white/90">
            Ajusta tu imagen
          </h3>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Recomendado: {OUTPUT_SIZE} px de ancho x {OUTPUT_SIZE} px de alto.
          </p>
        </div>
        <button
          id="tour-photo-select"
          type="button"
          onClick={() => fileInputRef.current?.click()}
          className="inline-flex items-center justify-center gap-2 rounded-lg border border-gray-300 bg-white px-4 py-3 text-sm font-medium text-gray-700 shadow-theme-xs transition hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-white/3"
        >
          <ImagePlus size={18} />
          Elegir foto
        </button>
        <input
          ref={fileInputRef}
          type="file"
          accept="image/jpeg,image/png,image/webp"
          className="hidden"
          onChange={handleFileChange}
        />
      </div>

      <div className="flex flex-col gap-6 lg:flex-row lg:items-start">
        <div
          id="tour-photo-editor"
          role={sourceImage ? "presentation" : "button"}
          tabIndex={sourceImage ? undefined : 0}
          onClick={() => { if (!sourceImage) fileInputRef.current?.click(); }}
          onKeyDown={(e) => { if (!sourceImage && (e.key === "Enter" || e.key === " ")) fileInputRef.current?.click(); }}
          onPointerDown={handlePointerDown}
          onPointerMove={handlePointerMove}
          onPointerUp={stopDragging}
          onPointerCancel={stopDragging}
          className={`relative mx-auto overflow-hidden rounded-2xl border border-gray-200 bg-gray-950 shadow-theme-sm touch-none dark:border-gray-800 lg:mx-0${!sourceImage ? " cursor-pointer" : ""}`}
          style={{ width: VIEW_SIZE, height: VIEW_SIZE }}
        >
          {sourceImage && metrics ? (
            <img
              ref={imageRef}
              src={sourceImage.url}
              alt="Foto seleccionada"
              draggable={false}
              className="absolute left-0 top-0 max-w-none select-none"
              style={{
                width: metrics.renderedWidth,
                height: metrics.renderedHeight,
                transform: `translate(${metrics.topLeftX}px, ${metrics.topLeftY}px)`,
              }}
            />
          ) : (
            <div className="flex h-full w-full flex-col items-center justify-center gap-3 text-gray-400">
              <Camera size={34} />
              <span className="text-sm">Sin foto seleccionada</span>
            </div>
          )}
          <div className="pointer-events-none absolute inset-4 rounded-full border-2 border-white/90 shadow-[0_0_0_999px_rgba(16,24,40,0.42)]" />
        </div>

        <div className="min-w-0 flex-1 space-y-5">
          <div id="tour-photo-zoom" className="rounded-xl border border-gray-200 p-4 dark:border-gray-800">
            <div className="mb-3 flex items-center justify-between gap-3">
              <label className="flex items-center gap-2 text-sm font-medium text-gray-700 dark:text-gray-300">
                <ZoomIn size={16} />
                Zoom
              </label>
              <span className="text-xs font-medium text-gray-500 dark:text-gray-400">
                {Math.round(zoom * 100)}%
              </span>
            </div>
            <input
              type="range"
              min={MIN_ZOOM}
              max={MAX_ZOOM}
              step="0.01"
              value={zoom}
              onChange={handleZoomChange}
              disabled={!sourceImage}
              className="h-2 w-full accent-brand-500"
            />
          </div>

          {sourceImage ? (
            <div className="grid gap-3 text-sm text-gray-600 dark:text-gray-400 sm:grid-cols-3">
              <div className="rounded-lg bg-gray-50 p-3 dark:bg-white/3">
                <span className="block text-xs text-gray-400">Archivo</span>
                <span className="block truncate font-medium text-gray-800 dark:text-white/90">
                  {sourceImage.name}
                </span>
              </div>
              <div className="rounded-lg bg-gray-50 p-3 dark:bg-white/3">
                <span className="block text-xs text-gray-400">Original</span>
                <span className="font-medium text-gray-800 dark:text-white/90">
                  {sourceImage.width} x {sourceImage.height} px
                </span>
              </div>
              <div className="rounded-lg bg-gray-50 p-3 dark:bg-white/3">
                <span className="block text-xs text-gray-400">Tamaño</span>
                <span className="font-medium text-gray-800 dark:text-white/90">
                  {formatFileSize(sourceImage.size)}
                </span>
              </div>
            </div>
          ) : (
            <div className="rounded-xl border border-dashed border-gray-300 p-4 text-sm text-gray-500 dark:border-gray-700 dark:text-gray-400">
              JPG, PNG o WebP. Máximo 5 MB.
            </div>
          )}

          {(localError || error) && (
            <p className="rounded-lg bg-error-50 px-3 py-2 text-sm text-error-600 dark:bg-error-500/10 dark:text-error-400">
              {localError ?? error}
            </p>
          )}
        </div>
      </div>
    </section>
  );
};
