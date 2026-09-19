import { useRef, useState } from "react";
import EmailEditor, { type EditorRef } from "react-email-editor";
import type { JSONTemplate } from "@unlayer/types";
import { Maximize2, Minimize2 } from "lucide-react";
import { Modal } from "@/ui/components/modal/modal";
import type { TemplateEditorProps } from "@/templates/types/template-editor-props";

export const TemplateEditor: React.FC<TemplateEditorProps> = ({
  value,
  design,
  onChange,
  variables = [],
  loadingVariables = false,
}) => {
  const editorRef = useRef<EditorRef>(null);
  const [isFullscreen, setIsFullscreen] = useState(false);

  const mergeTags = variables.reduce<Record<string, { name: string; value: string }>>(
    (acc, v) => {
      acc[v.key] = { name: v.label, value: `{${v.key}}` };
      return acc;
    },
    {},
  );

  const emitChange = () => {
    editorRef.current?.editor?.exportHtml(({ html, design: exportedDesign }) => {
      onChange(html, JSON.stringify(exportedDesign));
    });
  };

  const handleReady = () => {
    const editor = editorRef.current?.editor;
    if (!editor) return;
    if (design) {
      try {
        editor.loadDesign(JSON.parse(design) as JSONTemplate);
      } catch {
        // diseño inválido: se inicia en blanco en lugar de romper el editor
      }
    }
    editor.addEventListener("design:updated", emitChange);
  };

  const isLegacyTemplate = !design && !!value;

  const editorContent = (
    <div
      className={
        isFullscreen
          ? "flex h-full flex-col"
          : "overflow-y-auto rounded-xl border border-gray-200 dark:border-gray-700"
      }
    >
      <div className="flex items-center justify-between gap-3 border-b border-gray-200 bg-gray-50 px-4 py-2 dark:border-gray-700 dark:bg-gray-800">
        <p className="text-xs text-gray-500 dark:text-gray-400">
          Diseña el contenido arrastrando bloques desde el panel derecho.
        </p>
        <button
          type="button"
          onClick={() => setIsFullscreen((v) => !v)}
          className="flex shrink-0 items-center gap-1.5 rounded-lg border border-gray-300 px-3 py-1.5 text-xs font-medium text-gray-600 transition hover:bg-gray-100 dark:border-gray-700 dark:text-gray-300 dark:hover:bg-gray-700"
        >
          {isFullscreen ? <Minimize2 size={14} /> : <Maximize2 size={14} />}
          {isFullscreen ? "Salir de pantalla completa" : "Pantalla completa"}
        </button>
      </div>
      {isLegacyTemplate && (
        <div className="border-b border-gray-200 bg-warning-50 px-4 py-2 text-xs text-warning-700 dark:border-gray-700 dark:bg-warning-500/15 dark:text-orange-400">
          Esta plantilla se creó con el editor anterior y no tiene un diseño visual guardado. Si
          la guardas sin volver a diseñarla en este editor, se perderá el contenido anterior.
        </div>
      )}
      {!loadingVariables && variables.length > 0 && (
        <div className="border-b border-gray-200 bg-gray-50 px-4 py-3 dark:border-gray-700 dark:bg-gray-800">
          <p className="mb-2 text-xs text-gray-500 dark:text-gray-400">
            Selecciona un bloque de texto y usa el icono de variable en su barra de herramientas
            para insertar una de estas.
          </p>
          <div className="flex flex-wrap gap-1.5">
            {variables.map((v) => (
              <span
                key={v.key}
                title={v.label}
                className="rounded-md bg-brand-50 px-2 py-0.5 font-mono text-[11px] text-brand-600 dark:bg-brand-500/10 dark:text-brand-400"
              >
                {`{${v.key}}`}
              </span>
            ))}
          </div>
        </div>
      )}
      <EmailEditor
        ref={editorRef}
        onReady={handleReady}
        minHeight={isFullscreen ? "100%" : "600px"}
        style={isFullscreen ? { flex: 1 } : undefined}
        options={{ mergeTags }}
      />
    </div>
  );

  if (isFullscreen) {
    return (
      <Modal
        isOpen
        onClose={() => setIsFullscreen(false)}
        isFullscreen
        showCloseButton={false}
        className="bg-white dark:bg-gray-900"
      >
        {editorContent}
      </Modal>
    );
  }

  return editorContent;
};
