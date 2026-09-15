import { useState } from "react";
import { Pencil, Settings } from "lucide-react";
import { PageMeta } from "@/ui/pages/page-meta";
import { ModuleBase } from "@/ui/components/common/module-base";
import { Card, CardTitle } from "@/ui/components/card";
import { Loader } from "@/ui/components/loader/loader";
import { Input } from "@/ui/components/inputs/input";
import { Label } from "@/ui/components/inputs/label";
import { CountrySelect } from "@/ui/components/inputs/country-select";
import { Select } from "@/ui/components/inputs/select";
import { Textarea } from "@/ui/components/inputs/textarea";
import { Button } from "@/ui/components/button/button";
import { InfoRow } from "@/companies/components/info-row";
import { DocFileRow } from "@/companies/components/doc-file-row";
import { LogoUploadCard } from "@/companies/components/logo-upload-card";
import { useOrgSettings } from "../hooks/use-org-settings";
import { useEntitySectors } from "../hooks/use-entity-sectors";
import { useOrgModule } from "../hooks/use-org-module";
import { useRequireOrg } from "../hooks/use-require-org";
import { useBreadcrumb } from "../hooks/use-breadcrumb";
import { FISCAL_DOC_OPTIONS, MERCANTILE_DOC_OPTIONS } from "@/companies/constants/org-settings-form";
import { ORG_VERIFICATION_STYLES as VERIFICATION_STYLES } from "@/companies/constants/org-verification-styles";
import { formatShortDate as fmt } from "@/profile/utils/format-date";

const VerificationBadge: React.FC<{ status?: string | null }> = ({ status }) => {
  if (!status) return null;
  const cfg = VERIFICATION_STYLES[status] ?? { label: status, classes: "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400" };
  return (
    <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${cfg.classes}`}>
      {cfg.label}
    </span>
  );
};

export const OrgSettingsPage: React.FC = () => {
  useRequireOrg();
  const { orgId } = useOrgModule();
  const { build } = useBreadcrumb();

  const { org, loading, saving, updateInfo, uploadDocument, requestVerification } = useOrgSettings(orgId);
  const { sectors, loading: loadingSectors } = useEntitySectors();

  const [isEditing, setIsEditing] = useState(false);
  const [form, setForm] = useState({
    name: "",
    sector: "",
    description: "",
    country: "",
    fiscalDocumentType: "",
    fiscalDocumentNumber: "",
    mercantileDocumentType: "",
  });

  const startEdit = () => {
    setForm({
      name: org?.name ?? "",
      sector: org?.sector ?? "",
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
      sector: form.sector || undefined,
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
        pageIcon={Settings}
        breadcrumbItems={build()}
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
                      <Label htmlFor="org-settings-name">
                        Nombre <span className="text-error-500" aria-hidden="true">*</span>
                      </Label>
                      <Input
                        id="org-settings-name"
                        value={form.name}
                        onChange={(e) => setForm((p) => ({ ...p, name: e.target.value }))}
                        placeholder="Nombre de la organización"
                        required
                        aria-required="true"
                      />
                    </div>
                    <div>
                      <Label>
                        <span className="mb-1.5 block">
                          Sector <span className="text-error-500" aria-hidden="true">*</span>
                        </span>
                        <Select
                          options={sectors}
                          value={form.sector}
                          onChange={(v) => setForm((p) => ({ ...p, sector: v }))}
                          disabled={loadingSectors}
                          placeholder={loadingSectors ? "Cargando sectores..." : "Selecciona el sector"}
                        />
                      </Label>
                    </div>
                    <div>
                      <Label>
                        <span className="mb-1.5 block">País</span>
                        <CountrySelect
                          mode="NAME"
                          value={form.country}
                          onChange={(v) => setForm((p) => ({ ...p, country: v }))}
                          disabled={!!org?.country}
                        />
                      </Label>
                      {org?.country && (
                        <p className="mt-1.5 text-xs text-gray-400 dark:text-gray-500">
                          El país no puede modificarse una vez asignado.
                        </p>
                      )}
                    </div>
                    <div className="sm:col-span-2">
                      <Label htmlFor="org-settings-description">Descripción</Label>
                      <Textarea
                        id="org-settings-description"
                        value={form.description}
                        onChange={(e) => setForm((p) => ({ ...p, description: e.target.value }))}
                        placeholder="Descripción opcional"
                        rows={3}
                      />
                    </div>
                  </div>

                  <div className="border-t border-gray-100 pt-5 dark:border-gray-800">
                    <p className="mb-4 text-sm font-medium text-gray-700 dark:text-gray-300">Documentos</p>
                    <div className="grid grid-cols-1 gap-5 sm:grid-cols-2">
                      <div>
                        <Label>
                          <span className="mb-1.5 block">Tipo documento fiscal</span>
                          <Select
                            options={FISCAL_DOC_OPTIONS}
                            value={form.fiscalDocumentType}
                            onChange={(v) => setForm((p) => ({ ...p, fiscalDocumentType: v }))}
                            placeholder="Seleccionar"
                          />
                        </Label>
                      </div>
                      <div>
                        <Label htmlFor="org-settings-fiscal-doc-number">N° documento fiscal</Label>
                        <Input
                          id="org-settings-fiscal-doc-number"
                          value={form.fiscalDocumentNumber}
                          onChange={(e) => setForm((p) => ({ ...p, fiscalDocumentNumber: e.target.value }))}
                          placeholder="Número de documento"
                        />
                      </div>
                      <div className="sm:col-span-2">
                        <Label>
                          <span className="mb-1.5 block">Tipo documento mercantil</span>
                          <Select
                            options={MERCANTILE_DOC_OPTIONS}
                            value={form.mercantileDocumentType}
                            onChange={(v) => setForm((p) => ({ ...p, mercantileDocumentType: v }))}
                            placeholder="Seleccionar"
                          />
                        </Label>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center justify-end gap-3">
                    <Button type="button" size="sm" variant="outline" onClick={() => setIsEditing(false)}>
                      Cancelar
                    </Button>
                    <Button type="submit" size="sm" loading={saving} loadingText="Guardando...">
                      Guardar cambios
                    </Button>
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
                    {org?.verificationStatus === "DENEGADO" && (
                      <button
                        type="button"
                        onClick={requestVerification}
                        disabled={saving}
                        className="inline-flex items-center justify-center gap-2 rounded-full border border-error-300 bg-error-50 px-4 py-2.5 text-sm font-medium text-error-700 hover:bg-error-100 disabled:opacity-50 dark:border-error-700 dark:bg-error-500/10 dark:text-error-400"
                      >
                        Volver a solicitar verificación
                      </button>
                    )}
                    <button
                      type="button"
                      onClick={startEdit}
                      className="inline-flex items-center justify-center gap-2 rounded-full border border-gray-300 bg-white px-4 py-2.5 text-sm font-medium text-gray-700 shadow-theme-xs hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-white/5"
                    >
                      <Pencil size={16} />
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

            {/* ── Logo ── */}
            <Card>
              <CardTitle>Logo</CardTitle>
              <LogoUploadCard
                logoUrl={org?.logoUrl}
                saving={saving}
                onUpload={(file) => uploadDocument("logo", file)}
              />
            </Card>

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
