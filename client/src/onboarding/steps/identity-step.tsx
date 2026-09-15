import { useState } from "react";
import { DropZone } from "@/ui/components/inputs/drop-zone";
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

      <button
        type="submit"
        disabled={loading || !file}
        className="flex w-full items-center justify-center rounded-lg bg-brand-500 px-4 py-3 text-sm font-medium text-white transition hover:bg-brand-600 disabled:opacity-50"
      >
        {loading ? "Enviando..." : "Enviar para validación"}
      </button>
    </form>
  );
};
