import { useState } from "react";
import { ShieldCheck, ShieldAlert } from "lucide-react";
import { DropZone } from "@/ui/components/inputs/drop-zone";
import { getSession } from "@/auth/utils/auth-session-utils";
import { useSubmitIdentityDocument } from "@/hooks/use-submit-identity-document";
import type { IdentityVerificationNoticeProps } from "@/credits/types/identity-verification-notice-props";

/**
 * Reemplaza la vista de créditos/extractos/notificaciones cuando el titular todavía
 * no tiene la identidad aprobada (ver IdentityVerificationStatus). NOT_SUBMITTED no
 * debería verse en la práctica (el onboarding ya exige subir el documento), pero se
 * cubre por si la cuenta es anterior a esta funcionalidad.
 */
export const IdentityVerificationNotice: React.FC<IdentityVerificationNoticeProps> = ({ className }) => {
  const status = getSession()?.identityVerificationStatus ?? "NO_ENVIADO";
  const { submit, loading, error, clearError } = useSubmitIdentityDocument();
  const [file, setFile] = useState<File | null>(null);
  const [sent, setSent] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;
    const ok = await submit(file);
    if (ok) setSent(true);
  };

  if (status === "PENDIENTE" || sent) {
    return (
      <div className={`flex flex-col items-center justify-center gap-3 py-20 text-center ${className ?? ""}`}>
        <ShieldCheck size={48} strokeWidth={1.5} className="text-brand-500" />
        <p className="text-sm font-medium text-gray-700 dark:text-gray-300">Tu identidad está en revisión</p>
        <p className="max-w-sm text-sm text-gray-400 dark:text-gray-500">
          Un agente de Atención al Cliente está validando tu documento. Te avisaremos cuando esté aprobado.
        </p>
      </div>
    );
  }

  return (
    <div className={`mx-auto flex max-w-md flex-col items-center gap-4 py-16 text-center ${className ?? ""}`}>
      <ShieldAlert size={48} strokeWidth={1.5} className="text-warning-500" />
      <div>
        <p className="text-sm font-medium text-gray-700 dark:text-gray-300">
          {status === "DENEGADO" ? "No pudimos verificar tu identidad" : "Verifica tu identidad"}
        </p>
        <p className="mt-1 text-sm text-gray-400 dark:text-gray-500">
          {status === "DENEGADO"
            ? "El documento enviado fue rechazado. Sube uno nuevo para intentarlo otra vez."
            : "Sube tu documento de identidad para acceder a tu información crediticia."}
        </p>
      </div>
      <form onSubmit={handleSubmit} className="w-full space-y-4 text-left">
        <DropZone
          label="Documento de identidad"
          file={file}
          onChange={(f) => { clearError(); setFile(f); }}
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
    </div>
  );
};
