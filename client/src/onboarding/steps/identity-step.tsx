import { useState } from "react";
import { DropZone } from "@/ui/components/inputs/drop-zone";
import { Button } from "@/ui/components/button/button";
import { useSubmitIdentityDocument } from "@/hooks/use-submit-identity-document";
import type { StepDoneProps } from "@/types/props/onboarding-props";

export const IdentityStep: React.FC<StepDoneProps> = ({ onDone }) => {
  const { submit, loading, error, clearError } = useSubmitIdentityDocument();
  const [file, setFile] = useState<File | null>(null);

  const handleChange = (f: File | null) => {
    clearError();
    setFile(f);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;
    const ok = await submit(file);
    if (ok) onDone();
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      <div>
        <h2 className="text-lg font-semibold text-gray-800 dark:text-white/90">Verifica tu identidad</h2>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Sube una foto o PDF de tu documento de identidad. Un agente de Atención al Cliente lo
          revisará y, una vez aprobado, podrás ver tu información crediticia.
        </p>
      </div>

      <DropZone
        label="Documento de identidad"
        file={file}
        onChange={handleChange}
        error={error ?? undefined}
        allowed={["application/pdf", "image/png", "image/jpeg"]}
        hint="PDF, PNG o JPG · máx. 10 MB"
      />

      <Button type="submit" className="w-full" disabled={!file} loading={loading} loadingText="Enviando...">
        Enviar para validación
      </Button>
    </form>
  );
};
