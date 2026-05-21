import React, { useRef, useState } from "react";
import { DropZoneProps } from "@/types/props/drop-zone-props";

const ALLOWED = ["application/pdf", "image/png"];

export const DropZone: React.FC<DropZoneProps> = ({ label, file, onChange, error }) => {
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragging, setDragging] = useState(false);

  const accept = (f: File) => {
    if (!ALLOWED.includes(f.type)) return;
    onChange(f);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragging(false);
    const f = e.dataTransfer.files[0];
    if (f) accept(f);
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    if (f) accept(f);
  };

  const borderClass = error
    ? "border-error-500"
    : dragging
      ? "border-brand-400 bg-brand-50 dark:bg-brand-900/20"
      : "border-gray-300 dark:border-gray-700";

  return (
    <div className="space-y-1.5">
      <span className="text-sm font-medium text-gray-700 dark:text-gray-300">{label}</span>
      <div
        className={`flex flex-col items-center justify-center gap-2 rounded-xl border-2 border-dashed px-4 py-6 cursor-pointer transition-colors ${borderClass}`}
        onClick={() => inputRef.current?.click()}
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
      >
        {file ? (
          <div className="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <polyline points="14 2 14 8 20 8"/>
            </svg>
            <span className="truncate max-w-[200px]">{file.name}</span>
            <button
              type="button"
              onClick={(e) => { e.stopPropagation(); onChange(null); }}
              className="ml-1 text-gray-400 hover:text-error-500"
            >
              ✕
            </button>
          </div>
        ) : (
          <>
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="text-gray-400">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
              <polyline points="17 8 12 3 7 8"/>
              <line x1="12" y1="3" x2="12" y2="15"/>
            </svg>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              Arrastra aquí o <span className="text-brand-500 font-medium">selecciona un archivo</span>
            </p>
            <p className="text-xs text-gray-400">PDF o PNG · máx. 5 MB</p>
          </>
        )}
      </div>
      {error && <p className="text-xs text-error-500">{error}</p>}
      <input
        ref={inputRef}
        type="file"
        accept=".pdf,.png"
        className="hidden"
        onChange={handleChange}
      />
    </div>
  );
};
