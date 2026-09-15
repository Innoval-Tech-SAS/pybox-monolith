import { useState } from "react";
import { Input } from "@/ui/components/inputs/input";
import { Label } from "@/ui/components/inputs/label";
import { Select } from "@/ui/components/inputs/select";
import { useForgotPassword } from "../hooks/use-forgot-password";
import { useDocumentTypes } from "@/hooks/use-document-types";
import type { ForgotPasswordStep1Props } from "@/auth/types/props/forgot-password-step-1-props";

export const ForgotPasswordStep1: React.FC<ForgotPasswordStep1Props> = ({ onNext, loading }) => {
  const { lookup } = useForgotPassword();
  const { groups: documentTypeGroups } = useDocumentTypes();
  const [documentType, setDocumentType] = useState("CC");
  const [documentNumber, setDocumentNumber] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const result = await lookup(documentType, documentNumber);
    // La respuesta es uniforme exista o no la cuenta (evita usarla como oráculo de
    // enumeración): siempre avanzamos, y el paso 2 muestra un mensaje neutral si no
    // hay ningún canal disponible.
    if (result) onNext(documentType, documentNumber, result);
  };

  return (
    <form onSubmit={handleSubmit}>
      <div className="space-y-5">
        <div>
          {/* El componente Select compartido no expone `id`, por lo que no es posible
              enlazar este label vía htmlFor sin modificar ui/components/inputs/select.tsx
              (fuera de alcance). Se deja como label visual asociado por proximidad. */}
          <Label className="text-gray-500">
            Tipo de documento <span className="text-error-500">*</span>
          </Label>
          <Select
            groups={documentTypeGroups}
            value={documentType}
            placeholder="Seleccionar tipo"
            onChange={setDocumentType}
          />
        </div>
        <div>
          <Label htmlFor="forgot-password-doc-number" className="text-gray-500">
            Número de documento <span className="text-error-500">*</span>
          </Label>
          <Input
            id="forgot-password-doc-number"
            type="text"
            placeholder="Número de documento"
            value={documentNumber}
            onChange={(e) => setDocumentNumber(e.target.value)}
            required
          />
        </div>
        <button
          type="submit"
          disabled={loading || !documentNumber}
          className="flex w-full items-center justify-center rounded-lg bg-brand-500 px-4 py-3 text-sm font-medium text-white transition hover:bg-brand-600 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? "Buscando..." : "Continuar"}
        </button>
      </div>
    </form>
  );
};
