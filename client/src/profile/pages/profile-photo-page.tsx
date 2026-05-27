import React, { useEffect, useMemo, useRef, useState } from "react";
import { Camera, ImagePlus, RotateCcw, Save, Upload, ZoomIn } from "lucide-react";
import { useNavigate } from "react-router";
import { PageMeta } from "@/ui/pages/page-meta";
import { ModuleBase } from "@/ui/components/common/module-base";
import { useUpdateProfilePhoto } from "../hooks/use-update-profile-photo";
import { useProfilePhotoTour } from "../hooks/use-profile-photo-tour";

const OUTPUT_SIZE = 512;
const VIEW_SIZE = 288;
const PREVIEW_SIZE = 96;
const MIN_ZOOM = 1;
const MAX_ZOOM = 3;
const ACCEPTED_TYPES = new Set(["image/jpeg", "image/png", "image/webp"]);

interface SelectedImage {
  url: string;
  name: string;
  size: number;
  width: number;
  height: number;
}

interface Point {
  x: number;
  y: number;
}

const clamp = (value: number, min: number, max: number) => Math.min(Math.max(value, min), max);

const formatFileSize = (bytes: number) => {
  if (bytes < 1024 * 1024) return `${Math.max(1, Math.round(bytes / 1024))} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
};

const getBaseScale = (image: SelectedImage) => VIEW_SIZE / Math.min(image.width, image.height);

export const ProfilePhotoPage: React.FC = () => {
  const navigate = useNavigate();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const imageRef = useRef<HTMLImageElement>(null);
  const dragRef = useRef<{ start: Point; origin: Point } | null>(null);
  const [sourceImage, setSourceImage] = useState<SelectedImage | null>(null);
  const [position, setPosition] = useState<Point>({ x: 0, y: 0 });
  const [zoom, setZoom] = useState(MIN_ZOOM);
  const [localError, setLocalError] = useState<string | null>(null);
  const { updateProfilePhoto, loading, error } = useUpdateProfilePhoto();

  useProfilePhotoTour(true);

  useEffect(() => {
    return () => {
      if (sourceImage) URL.revokeObjectURL(sourceImage.url);
    };
  }, [sourceImage]);

  const metrics = useMemo(() => {
    if (!sourceImage) return null;
    const scale = getBaseScale(sourceImage) * zoom;
    const renderedWidth = sourceImage.width * scale;
    const renderedHeight = sourceImage.height * scale;
    const topLeftX = (VIEW_SIZE - renderedWidth) / 2 + position.x;
    const topLeftY = (VIEW_SIZE - renderedHeight) / 2 + position.y;
    return { scale, renderedWidth, renderedHeight, topLeftX, topLeftY };
  }, [sourceImage, position, zoom]);

  const clampPosition = (next: Point, nextZoom = zoom, image = sourceImage): Point => {
    if (!image) return { x: 0, y: 0 };
    const scale = getBaseScale(image) * nextZoom;
    const limitX = Math.max(0, (image.width * scale - VIEW_SIZE) / 2);
    const limitY = Math.max(0, (image.height * scale - VIEW_SIZE) / 2);
    return {
      x: clamp(next.x, -limitX, limitX),
      y: clamp(next.y, -limitY, limitY),
    };
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    event.target.value = "";
    if (!file) return;
    console.log("[profile-photo] selected file", {
      name: file.name,
      size: file.size,
      type: file.type,
    });

    if (!ACCEPTED_TYPES.has(file.type)) {
      console.log("[profile-photo] selected file rejected", { type: file.type });
      setLocalError("Usa una imagen JPG, PNG o WebP.");
      return;
    }

    const url = URL.createObjectURL(file);
    const probe = new Image();
    probe.onload = () => {
      console.log("[profile-photo] selected file loaded", {
        naturalWidth: probe.naturalWidth,
        naturalHeight: probe.naturalHeight,
      });
      setSourceImage({
        url,
        name: file.name,
        size: file.size,
        width: probe.naturalWidth,
        height: probe.naturalHeight,
      });
      setZoom(MIN_ZOOM);
      setPosition({ x: 0, y: 0 });
      setLocalError(null);
    };
    probe.onerror = () => {
      console.log("[profile-photo] selected file load error", { name: file.name });
      URL.revokeObjectURL(url);
      setLocalError("No se pudo leer la imagen.");
    };
    probe.src = url;
  };

  const handleZoomChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const nextZoom = Number(event.target.value);
    setZoom(nextZoom);
    setPosition((current) => clampPosition(current, nextZoom));
  };

  const handlePointerDown = (event: React.PointerEvent<HTMLDivElement>) => {
    if (!sourceImage) return;
    event.currentTarget.setPointerCapture(event.pointerId);
    dragRef.current = {
      start: { x: event.clientX, y: event.clientY },
      origin: position,
    };
  };

  const handlePointerMove = (event: React.PointerEvent<HTMLDivElement>) => {
    if (!dragRef.current) return;
    const next = {
      x: dragRef.current.origin.x + event.clientX - dragRef.current.start.x,
      y: dragRef.current.origin.y + event.clientY - dragRef.current.start.y,
    };
    setPosition(clampPosition(next));
  };

  const stopDragging = () => {
    dragRef.current = null;
  };

  const createCroppedBlob = () =>
    new Promise<Blob>((resolve, reject) => {
      if (!sourceImage || !metrics || !imageRef.current) {
        console.log("[profile-photo] crop skipped", { hasSourceImage: !!sourceImage, hasMetrics: !!metrics });
        reject(new Error("Selecciona una foto antes de guardar."));
        return;
      }

      const canvas = document.createElement("canvas");
      canvas.width = OUTPUT_SIZE;
      canvas.height = OUTPUT_SIZE;
      const context = canvas.getContext("2d");
      if (!context) {
        reject(new Error("No se pudo preparar el recorte."));
        return;
      }

      const sourceX = Math.max(0, -metrics.topLeftX / metrics.scale);
      const sourceY = Math.max(0, -metrics.topLeftY / metrics.scale);
      const sourceSize = VIEW_SIZE / metrics.scale;
      console.log("[profile-photo] crop metrics", {
        sourceX,
        sourceY,
        sourceSize,
        outputSize: OUTPUT_SIZE,
        metrics,
      });
      context.imageSmoothingEnabled = true;
      context.imageSmoothingQuality = "high";
      context.drawImage(
        imageRef.current,
        sourceX,
        sourceY,
        sourceSize,
        sourceSize,
        0,
        0,
        OUTPUT_SIZE,
        OUTPUT_SIZE,
      );
      canvas.toBlob((blob) => {
        if (blob) {
          console.log("[profile-photo] crop blob ready", { size: blob.size, type: blob.type });
          resolve(blob);
        } else {
          console.log("[profile-photo] crop blob error");
          reject(new Error("No se pudo generar la imagen recortada."));
        }
      }, "image/png");
    });

  const handleSave = async () => {
    setLocalError(null);
    console.log("[profile-photo] save clicked", { hasSourceImage: !!sourceImage });
    try {
      const blob = await createCroppedBlob();
      const profilePhotoUrl = await updateProfilePhoto(blob);
      console.log("[profile-photo] save success", { profilePhotoUrl });
      navigate("/profile");
    } catch (e) {
      console.log("[profile-photo] save error", e);
      setLocalError(e instanceof Error ? e.message : "Error al guardar la foto.");
    }
  };

  const resetCrop = () => {
    setZoom(MIN_ZOOM);
    setPosition({ x: 0, y: 0 });
  };

  const previewScale = PREVIEW_SIZE / VIEW_SIZE;

  return (
    <>
      <PageMeta title="Foto de perfil" description="Actualiza tu foto de perfil" />
      <ModuleBase pageTitle="Foto de perfil" breadcrumbItems={[{ label: "Perfil", path: "/profile" }]}>
        <div className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_320px]">
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
        </div>
      </ModuleBase>
    </>
  );
};
