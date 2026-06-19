import { useRef, useState } from "react";
import { Check, Copy, ExternalLink, Upload } from "lucide-react";
import { PageMeta } from "@/ui/pages/page-meta";
import { ModuleBase } from "@/ui/components/common/module-base";
import { Card, CardTitle } from "@/ui/components/card";
import { Loader } from "@/ui/components/loader/loader";
import { Input } from "@/ui/components/inputs/input";
import { Label } from "@/ui/components/inputs/label";
import { CountrySelect } from "@/ui/components/inputs/country-select";
import { API_URL } from "@/hooks/use-api-client";
import { useOrgSettings } from "../hooks/use-org-settings";
import { useOrgModule } from "../hooks/use-org-module";
import type { DocType, DocFileRowProps } from "@/companies/types/doc-file-row-props";

const FISCAL_DOC_OPTIONS = [
  { value: "NIT", label: "NIT – Número de Identificación Tributaria" },
  { value: "RFC", label: "RFC – Registro Federal de Contribuyentes" },
  { value: "CUIT", label: "CUIT – Código Único de Identificación Tributaria" },
  { value: "RUC", label: "RUC – Registro Único de Contribuyentes" },
  { value: "RIF", label: "RIF – Registro de Información Fiscal" },
];

const MERCANTILE_DOC_OPTIONS = [
  { value: "CAMARA_COMERCIO", label: "Cámara de Comercio" },
  { value: "REGISTRO_PUBLICO_COMERCIO", label: "Registro Público de Comercio" },
  { value: "INSCRIPCION_IGJ", label: "Inscripción en el IGJ" },
  { value: "PARTIDA_SUNARP", label: "Partida Registral SUNARP" },
  { value: "REGISTRO_MERCANTIL", label: "Registro Mercantil" },
];

const fmt = (iso: string | null | undefined) =>
  iso
    ? new Date(iso).toLocaleDateString("es-CO", { day: "2-digit", month: "short", year: "numeric" })
    : "—";

const selectClass = "w-full rounded-lg border border-gray-300 bg-transparent px-3 py-2.5 text-sm text-gray-800 shadow-theme-xs outline-none transition focus:border-brand-300 focus:ring-3 focus:ring-brand-500/20 disabled:opacity-40 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:focus:border-brand-800";

const InfoRow = ({ label, value, copyable = false }: { label: string; value?: string | null; copyable?: boolean }) => {
  const [copied, setCopied] = useState(false);
  return (
    <div>
      <p className="mb-1 text-xs text-gray-500 dark:text-gray-400">{label}</p>
      <p className="flex items-center gap-1 text-sm font-medium text-gray-800 dark:text-white/90">
        <span className={copyable ? "font-mono text-xs" : ""}>{value || "—"}</span>
        {copyable && value && (
          <button
            onClick={() => { navigator.clipboard.writeText(value); setCopied(true); setTimeout(() => setCopied(false), 2000); }}
            className="ml-0.5 inline-flex items-center rounded p-0.5 text-gray-400 hover:bg-gray-100 hover:text-gray-600 dark:hover:bg-gray-700 dark:hover:text-gray-300"
          >
            {copied ? <Check size={12} /> : <Copy size={12} />}
          </button>
        )}
      </p>
    </div>
  );
};

const resolveFileUrl = (path: string | null | undefined): string | null => {
  if (!path) return null;
  if (/^https?:\/\//i.test(path)) return path;
  if (path.startsWith("/files/")) {
    try { return `${new URL(API_URL).origin}${path}`; } catch { return path; }
  }
  return path;
};

const fileNameFromUrl = (url: string) => url.split("/").pop() ?? url;

const DocFileRow: React.FC<DocFileRowProps> = ({ label, fileUrl, docType, saving, onUpload }) => {
  const inputRef = useRef<HTMLInputElement>(null);
  const resolved = resolveFileUrl(fileUrl);

  return (
    <div className="flex items-center justify-between gap-4 rounded-xl border border-gray-200 p-4 dark:border-gray-800">
      <div className="min-w-0">
        <p className="mb-0.5 text-xs text-gray-500 dark:text-gray-400">{label}</p>
        {resolved ? (
          <p className="truncate text-sm font-medium text-gray-800 dark:text-white/90">
            {fileNameFromUrl(resolved)}
          </p>
        ) : (
          <p className="text-sm text-gray-400 dark:text-gray-500">Sin documento</p>
        )}
      </div>
      <div className="flex shrink-0 items-center gap-2">
        {resolved && (
          <a
            href={resolved}
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center gap-1.5 rounded-lg border border-gray-300 bg-white px-3 py-1.5 text-xs font-medium text-gray-700 hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-300"
          >
            <ExternalLink size={12} />
            Ver
          </a>
        )}
        <input
          ref={inputRef}
          type="file"
          accept=".pdf,.jpg,.jpeg,.png"
          className="hidden"
          onChange={(e) => {
            const file = e.target.files?.[0];
            if (file) { onUpload(docType, file); e.target.value = ""; }
          }}
        />
        <button
          onClick={() => inputRef.current?.click()}
          disabled={saving}
          className="inline-flex items-center gap-1.5 rounded-lg border border-gray-300 bg-white px-3 py-1.5 text-xs font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-300"
        >
          <Upload size={12} />
          {resolved ? "Reemplazar" : "Subir"}
        </button>
      </div>
    </div>
  );
};

const VERIFICATION_STYLES: Record<string, { label: string; classes: string }> = {
  pending:  { label: "Verificación pendiente", classes: "bg-warning-50 text-warning-700 dark:bg-warning-500/10 dark:text-warning-400" },
  approved: { label: "Verificada",             classes: "bg-success-50 text-success-700 dark:bg-success-500/10 dark:text-success-400" },
  denied:   { label: "Verificación denegada",  classes: "bg-error-50 text-error-700 dark:bg-error-500/10 dark:text-error-400" },
};

const VerificationBadge: React.FC<{ status?: string | null }> = ({ status }) => {
  if (!status) return null;
  const cfg = VERIFICATION_STYLES[status] ?? { label: status, classes: "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400" };
  return (
    <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${cfg.classes}`}>
      {cfg.label}
    </span>
  );
};

const EditIcon = () => (
  <svg className="fill-current" width="16" height="16" viewBox="0 0 18 18" fill="none">
    <path fillRule="evenodd" clipRule="evenodd" d="M15.0911 2.78206C14.2125 1.90338 12.7878 1.90338 11.9092 2.78206L4.57524 10.116C4.26682 10.4244 4.0547 10.8158 3.96468 11.2426L3.31231 14.3352C3.25997 14.5833 3.33653 14.841 3.51583 15.0203C3.69512 15.1996 3.95286 15.2761 4.20096 15.2238L7.29355 14.5714C7.72031 14.4814 8.11172 14.2693 8.42013 13.9609L15.7541 6.62695C16.6327 5.74827 16.6327 4.32365 15.7541 3.44497L15.0911 2.78206ZM12.9698 3.84272C13.2627 3.54982 13.7376 3.54982 14.0305 3.84272L14.6934 4.50563C14.9863 4.79852 14.9863 5.2734 14.6934 5.56629L14.044 6.21573L12.3204 4.49215L12.9698 3.84272ZM11.2597 5.55281L5.6359 11.1766C5.53309 11.2794 5.46238 11.4099 5.43238 11.5522L5.01758 13.5185L6.98394 13.1037C7.1262 13.0737 7.25666 13.003 7.35947 12.9002L12.9833 7.27639L11.2597 5.55281Z" fill="" />
  </svg>
);

export const OrgSettingsPage: React.FC = () => {
  const { orgId, orgName, buildOrgPath } = useOrgModule();

  const { org, loading, saving, updateInfo, uploadDocument, requestVerification } = useOrgSettings(orgId);

  const [isEditing, setIsEditing] = useState(false);
  const [form, setForm] = useState({
    name: "",
    description: "",
    country: "",
    fiscalDocumentType: "",
    fiscalDocumentNumber: "",
    mercantileDocumentType: "",
  });

  const startEdit = () => {
    setForm({
      name: org?.name ?? "",
      description: org?.description ?? "",
      country: org?.country ?? "",
      fiscalDocumentType: org?.fiscalDocumentType ?? "",
      fiscalDocumentNumber: org?.fiscalDocumentNumber ?? "",
      mercantileDocumentType: org?.mercantileDocumentType ?? "",
    });
    setIsEditing(true);
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    await updateInfo({
      name: form.name || undefined,
      description: form.description || undefined,
      country: form.country || undefined,
      fiscalDocumentType: form.fiscalDocumentType || undefined,
      fiscalDocumentNumber: form.fiscalDocumentNumber || undefined,
      mercantileDocumentType: form.mercantileDocumentType || undefined,
    });
    setIsEditing(false);
  };

  const fiscalLabel = FISCAL_DOC_OPTIONS.find((o) => o.value === org?.fiscalDocumentType)?.label ?? org?.fiscalDocumentType;
  const mercantileLabel = MERCANTILE_DOC_OPTIONS.find((o) => o.value === org?.mercantileDocumentType)?.label ?? org?.mercantileDocumentType;

  return (
    <>
      <PageMeta title="Configuración" description="Configuración de la organización" />
      <ModuleBase
        pageTitle="Configuración"
        breadcrumbItems={[
          { label: "Mis Empresas", path: "/my-companies" },
          ...(orgId ? [{ label: orgName || "Empresa", path: buildOrgPath("/my-companies") }] : []),
        ]}
      >
        {loading ? (
          <div className="py-20">
            <Loader />
          </div>
        ) : (
          <div className="flex flex-col gap-5">
            {/* ── Header ── */}
            <div className="rounded-2xl border border-gray-200 p-5 dark:border-gray-800 lg:p-6">
              {isEditing ? (
                <form onSubmit={handleSave} className="space-y-5">
                  <div className="grid grid-cols-1 gap-5 sm:grid-cols-2">
                    <div>
                      <Label>Nombre <span className="text-error-500">*</span></Label>
                      <Input
                        value={form.name}
                        onChange={(e) => setForm((p) => ({ ...p, name: e.target.value }))}
                        placeholder="Nombre de la organización"
                        required
                      />
                    </div>
                    <div>
                      <Label>País</Label>
                      <CountrySelect
                        mode="NAME"
                        value={form.country}
                        onChange={(v) => setForm((p) => ({ ...p, country: v }))}
                        disabled={!!org?.country}
                      />
                      {org?.country && (
                        <p className="mt-1.5 text-xs text-gray-400 dark:text-gray-500">
                          El país no puede modificarse una vez asignado.
                        </p>
                      )}
                    </div>
                    <div className="sm:col-span-2">
                      <Label>Descripción</Label>
                      <textarea
                        value={form.description}
                        onChange={(e) => setForm((p) => ({ ...p, description: e.target.value }))}
                        placeholder="Descripción opcional"
                        rows={3}
                        className="w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/20 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:placeholder:text-white/30 dark:focus:border-brand-800"
                      />
                    </div>
                  </div>

                  <div className="border-t border-gray-100 pt-5 dark:border-gray-800">
                    <p className="mb-4 text-sm font-medium text-gray-700 dark:text-gray-300">Documentos</p>
                    <div className="grid grid-cols-1 gap-5 sm:grid-cols-2">
                      <div>
                        <Label>Tipo documento fiscal</Label>
                        <select
                          value={form.fiscalDocumentType}
                          onChange={(e) => setForm((p) => ({ ...p, fiscalDocumentType: e.target.value }))}
                          className={selectClass}
                        >
                          <option value="">Seleccionar</option>
                          {FISCAL_DOC_OPTIONS.map((o) => (
                            <option key={o.value} value={o.value}>{o.label}</option>
                          ))}
                        </select>
                      </div>
                      <div>
                        <Label>N° documento fiscal</Label>
                        <Input
                          value={form.fiscalDocumentNumber}
                          onChange={(e) => setForm((p) => ({ ...p, fiscalDocumentNumber: e.target.value }))}
                          placeholder="Número de documento"
                        />
                      </div>
                      <div className="sm:col-span-2">
                        <Label>Tipo documento mercantil</Label>
                        <select
                          value={form.mercantileDocumentType}
                          onChange={(e) => setForm((p) => ({ ...p, mercantileDocumentType: e.target.value }))}
                          className={selectClass}
                        >
                          <option value="">Seleccionar</option>
                          {MERCANTILE_DOC_OPTIONS.map((o) => (
                            <option key={o.value} value={o.value}>{o.label}</option>
                          ))}
                        </select>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center justify-end gap-3">
                    <button
                      type="button"
                      onClick={() => setIsEditing(false)}
                      className="rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm font-medium text-gray-700 shadow-theme-xs hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-300"
                    >
                      Cancelar
                    </button>
                    <button
                      type="submit"
                      disabled={saving}
                      className="rounded-lg bg-brand-500 px-4 py-2.5 text-sm font-medium text-white shadow-theme-xs hover:bg-brand-600 disabled:opacity-50"
                    >
                      {saving ? "Guardando..." : "Guardar cambios"}
                    </button>
                  </div>
                </form>
              ) : (
                <div className="flex flex-col gap-4 xl:flex-row xl:items-start xl:justify-between">
                  <div>
                    <div className="mb-1 flex flex-wrap items-center gap-2">
                      <h4 className="text-lg font-semibold text-gray-800 dark:text-white/90">
                        {org?.name}
                      </h4>
                      <VerificationBadge status={org?.verificationStatus} />
                    </div>
                    {org?.description && (
                      <p className="text-sm text-gray-500 dark:text-gray-400">{org.description}</p>
                    )}
                    <p className="mt-2 text-xs text-gray-400 dark:text-gray-500">
                      Creado: {fmt(org?.createdAt)}
                      {org?.updatedAt && ` · Actualizado: ${fmt(org.updatedAt)}`}
                    </p>
                  </div>
                  <div className="flex shrink-0 flex-wrap items-center gap-2">
                    {org?.verificationStatus === "denied" && (
                      <button
                        onClick={requestVerification}
                        disabled={saving}
                        className="inline-flex items-center justify-center gap-2 rounded-full border border-error-300 bg-error-50 px-4 py-2.5 text-sm font-medium text-error-700 hover:bg-error-100 disabled:opacity-50 dark:border-error-700 dark:bg-error-500/10 dark:text-error-400"
                      >
                        Volver a solicitar verificación
                      </button>
                    )}
                    <button
                      onClick={startEdit}
                      className="inline-flex items-center justify-center gap-2 rounded-full border border-gray-300 bg-white px-4 py-2.5 text-sm font-medium text-gray-700 shadow-theme-xs hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-white/5"
                    >
                      <EditIcon />
                      Editar
                    </button>
                  </div>
                </div>
              )}
            </div>

            {/* ── Info ── */}
            <div className="grid grid-cols-1 gap-5 lg:grid-cols-2">
              <Card>
                <CardTitle>Información</CardTitle>
                <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                  <InfoRow label="ID" value={org?.id} copyable />
                  <InfoRow label="País" value={org?.country} />
                  <InfoRow label="Registrado" value={fmt(org?.createdAt)} />
                  <InfoRow label="Actualizado" value={fmt(org?.updatedAt)} />
                </div>
              </Card>

              <Card>
                <CardTitle>Documentos</CardTitle>
                <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                  <InfoRow label="Tipo fiscal" value={fiscalLabel} />
                  <InfoRow label="N° fiscal" value={org?.fiscalDocumentNumber} />
                  <div className="sm:col-span-2">
                    <InfoRow label="Tipo mercantil" value={mercantileLabel} />
                  </div>
                </div>
              </Card>
            </div>

            {/* ── Archivos ── */}
            <Card>
              <CardTitle>Archivos</CardTitle>
              <div className="flex flex-col gap-3">
                <DocFileRow
                  label="Documento fiscal"
                  fileUrl={org?.fiscalDocumentFile}
                  docType="fiscal"
                  saving={saving}
                  onUpload={uploadDocument}
                />
                <DocFileRow
                  label="Documento mercantil"
                  fileUrl={org?.mercantileDocumentFile}
                  docType="mercantil"
                  saving={saving}
                  onUpload={uploadDocument}
                />
                <DocFileRow
                  label="Documento representante legal"
                  fileUrl={org?.representativeDocumentFile}
                  docType="representante"
                  saving={saving}
                  onUpload={uploadDocument}
                />
              </div>
            </Card>
          </div>
        )}
      </ModuleBase>
    </>
  );
};
