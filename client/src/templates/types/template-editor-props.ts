export interface TemplateEditorProps {
  value: string;
  onChange: (html: string) => void;
  channel?: "EMAIL" | "SMS";
}
