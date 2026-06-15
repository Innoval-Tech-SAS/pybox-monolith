import { useEffect, useRef } from "react";
import grapesjs, { type Editor } from "grapesjs";
import newsletterPlugin from "grapesjs-preset-newsletter";
import "grapesjs/dist/css/grapes.min.css";

interface TemplateEditorProps {
  value: string;
  onChange: (html: string) => void;
  channel?: "EMAIL" | "SMS";
}

export const TemplateEditor: React.FC<TemplateEditorProps> = ({
  value,
  onChange,
  channel = "EMAIL",
}) => {
  const editorRef = useRef<Editor | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const initializedRef = useRef(false);

  useEffect(() => {
    if (!containerRef.current || initializedRef.current) return;
    initializedRef.current = true;

    const editor = grapesjs.init({
      container: containerRef.current,
      height: "560px",
      storageManager: false,
      plugins: channel === "EMAIL" ? [newsletterPlugin] : [],
      pluginsOpts: {
        [newsletterPlugin as unknown as string]: {
          modalLabelImport: "Pegar código HTML",
          modalLabelExport: "Ver código HTML",
          codeViewerTheme: "material",
          importPlaceholder: "<table>...</table>",
          inlineCss: true,
          cellStyle: {
            "font-size": "13px",
            "font-weight": 300,
            "vertical-align": "top",
            color: "rgb(111, 119, 125)",
            margin: 0,
            padding: 0,
          },
        },
      },
      components: value || "",
    });

    // Bloque personalizado: Variable NRS360
    editor.BlockManager.add("nrs360-variable", {
      label: `<div style="font-size:11px;line-height:1.3;">📌<br/>Variable</div>`,
      category: "NRS360",
      content: `<span
        data-gjs-type="text"
        style="background:#dbeafe;color:#1d4ed8;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:13px;display:inline-block;"
      >{variable}</span>`,
      attributes: { title: "Bloque de variable dinámica" },
    });

    const emitChange = () => {
      const html = editor.getHtml();
      const css = editor.getCss({ avoidProtected: true }) ?? "";
      const full = css
        ? `<style>${css}</style>\n${html}`
        : html;
      onChange(full);
    };

    editor.on("component:update", emitChange);
    editor.on("component:add", emitChange);
    editor.on("component:remove", emitChange);
    editor.on("style:update", emitChange);

    editorRef.current = editor;

    return () => {
      editor.destroy();
      editorRef.current = null;
      initializedRef.current = false;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Cargar contenido externo (modo edición) solo una vez después de init
  useEffect(() => {
    if (!editorRef.current || !value) return;
    const current = editorRef.current.getHtml();
    if (current === value || current === "<body></body>") return;
    editorRef.current.setComponents(value);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="overflow-hidden rounded-xl border border-gray-200 dark:border-gray-700">
      <div className="flex items-center gap-2 border-b border-gray-200 bg-gray-50 px-4 py-2 dark:border-gray-700 dark:bg-gray-800">
        <span className="text-xs text-gray-500 dark:text-gray-400">
          Usa el bloque{" "}
          <span className="rounded bg-blue-100 px-1.5 py-0.5 font-mono text-xs text-blue-700 dark:bg-blue-900/40 dark:text-blue-300">
            Variable
          </span>{" "}
          del panel izquierdo o escribe{" "}
          <span className="rounded bg-gray-100 px-1.5 py-0.5 font-mono text-xs dark:bg-gray-700">
            {"{nombre_variable}"}
          </span>{" "}
          directamente en cualquier texto.
          {" "}NRS360 reemplaza las variables al enviar.
        </span>
      </div>
      <div ref={containerRef} />
    </div>
  );
};
