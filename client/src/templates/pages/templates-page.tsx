import { useState } from "react";
import { useNavigate, useSearchParams } from "react-router";
import { Eye, Mail, Pencil, Plus, Trash2 } from "lucide-react";
import { PageMeta } from "@/ui/pages/page-meta";
import { ModuleBase } from "@/ui/components/common/module-base";
import { Loader } from "@/ui/components/loader/loader";
import { Modal } from "@/ui/components/modal/modal";
import { Input } from "@/ui/components/inputs/input";
import { Label } from "@/ui/components/inputs/label";
import {
  Table,
  TableBody,
  TableCell,
  TableHeader,
  TableRow,
} from "@/ui/components/table/table";
import { getSession } from "@/auth/utils/auth-session-utils";
import { useTemplates } from "../hooks/use-templates";
import type {
  Template,
  TemplatePreviewResponse,
  TemplateStatus,
} from "@/types/templates/template-types";
import type { PreviewModalProps, SendModalProps } from "@/templates/types/templates-page-props";

// ─── helpers ──────────────────────────────────────────────────────────────────

const STATUS_LABELS: Record<TemplateStatus, string> = {
  DRAFT: "Borrador",
  ACTIVE: "Activa",
  INACTIVE: "Inactiva",
};

const STATUS_COLORS: Record<TemplateStatus, string> = {
  DRAFT: "bg-gray-100 text-gray-500 dark:bg-gray-800 dark:text-gray-400",
  ACTIVE: "bg-success-50 text-success-700 dark:bg-success-500/10 dark:text-success-400",
  INACTIVE: "bg-error-50 text-error-600 dark:bg-error-500/10 dark:text-error-400",
};

function extractVariables(source: string): string[] {
  const matches = [...source.matchAll(/\{(\w+)\}/g)];
  return [...new Set(matches.map((m) => m[1]))];
}

// ─── preview modal ─────────────────────────────────────────────────────────────

const TemplatePreviewModal: React.FC<PreviewModalProps> = ({ isOpen, template, onClose, onPreview }) => {
  const variables = template
    ? extractVariables((template.body ?? "") + " " + (template.subject ?? ""))
    : [];
  const [sub, setSub] = useState<Record<string, string>>({});
  const [result, setResult] = useState<TemplatePreviewResponse | null>(null);
  const [loading, setLoading] = useState(false);

  const handlePreview = async () => {
    if (!template) return;
    setLoading(true);
    const res = await onPreview(template.id, sub);
    setResult(res);
    setLoading(false);
  };

  const handleClose = () => {
    setResult(null);
    setSub({});
    onClose();
  };

  return (
    <Modal isOpen={isOpen} onClose={handleClose} className="max-w-3xl mx-4 p-6 sm:p-8">
      <h2 className="mb-4 text-lg font-semibold text-gray-800 dark:text-white/90">
        Vista previa — {template?.name}
      </h2>

      {variables.length > 0 && (
        <div className="mb-4">
          <p className="mb-2 text-xs font-medium uppercase tracking-wide text-gray-500 dark:text-gray-400">
            Variables detectadas
          </p>
          <div className="grid grid-cols-2 gap-3">
            {variables.map((v) => (
              <div key={v}>
                <Label htmlFor={`prev-${v}`}>{`{ ${v} }`}</Label>
                <Input
                  id={`prev-${v}`}
                  value={sub[v] ?? ""}
                  placeholder={`Valor para ${v}`}
                  onChange={(e) => setSub((prev) => ({ ...prev, [v]: e.target.value }))}
                />
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="mb-4 flex justify-end">
        <button
          onClick={handlePreview}
          disabled={loading}
          className="rounded-lg bg-brand-500 px-4 py-2.5 text-sm font-medium text-white hover:bg-brand-600 disabled:opacity-50"
        >
          {loading ? "Renderizando…" : "Renderizar"}
        </button>
      </div>

      {result && (
        <div className="rounded-xl border border-gray-200 dark:border-gray-700">
          {result.subject && (
            <div className="border-b border-gray-200 px-4 py-2.5 dark:border-gray-700">
              <span className="text-xs font-medium text-gray-500 dark:text-gray-400">Asunto: </span>
              <span className="text-sm text-gray-800 dark:text-white/90">{result.subject}</span>
            </div>
          )}
          <iframe
            srcDoc={result.html}
            title="Preview"
            className="h-96 w-full rounded-b-xl"
            sandbox="allow-same-origin"
          />
        </div>
      )}
    </Modal>
  );
};

// ─── send modal ────────────────────────────────────────────────────────────────

const TemplateSendModal: React.FC<SendModalProps> = ({ isOpen, template, saving, onClose, onSend }) => {
  const variables = template
    ? extractVariables((template.body ?? "") + " " + (template.subject ?? ""))
    : [];
  const [to, setTo] = useState("");
  const [subject, setSubject] = useState("");
  const [sub, setSub] = useState<Record<string, string>>({});

  const handleClose = () => {
    setTo(""); setSubject(""); setSub({});
    onClose();
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!template) return;
    await onSend(template.id, to, subject, sub);
    handleClose();
  };

  return (
    <Modal isOpen={isOpen} onClose={handleClose} className="max-w-lg mx-4 p-6 sm:p-8">
      <h2 className="mb-4 text-lg font-semibold text-gray-800 dark:text-white/90">
        Enviar email — {template?.name}
      </h2>
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <div>
          <Label htmlFor="send-to">Destinatario</Label>
          <Input id="send-to" type="email" value={to} onChange={(e) => setTo(e.target.value)} placeholder="destinatario@email.com" required />
        </div>
        <div>
          <Label htmlFor="send-subject">
            Asunto personalizado{" "}
            <span className="text-xs font-normal text-gray-400">(opcional)</span>
          </Label>
          <Input id="send-subject" value={subject} onChange={(e) => setSubject(e.target.value)} placeholder={template?.subject ?? ""} />
        </div>

        {variables.length > 0 && (
          <div>
            <p className="mb-2 text-xs font-medium uppercase tracking-wide text-gray-500 dark:text-gray-400">
              Variables
            </p>
            <div className="flex flex-col gap-3">
              {variables.map((v) => (
                <div key={v}>
                  <Label htmlFor={`send-${v}`}>{`{ ${v} }`}</Label>
                  <Input
                    id={`send-${v}`}
                    value={sub[v] ?? ""}
                    placeholder={`Valor para ${v}`}
                    onChange={(e) => setSub((prev) => ({ ...prev, [v]: e.target.value }))}
                    required
                  />
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="flex justify-end gap-3 pt-2">
          <button type="button" onClick={handleClose} className="rounded-lg border border-gray-300 px-4 py-2.5 text-sm font-medium text-gray-600 hover:bg-gray-50 dark:border-gray-700 dark:text-gray-400 dark:hover:bg-gray-800">
            Cancelar
          </button>
          <button type="submit" disabled={saving} className="inline-flex items-center gap-2 rounded-lg bg-brand-500 px-4 py-2.5 text-sm font-medium text-white hover:bg-brand-600 disabled:opacity-50">
            <Mail size={14} />
            {saving ? "Enviando…" : "Enviar"}
          </button>
        </div>
      </form>
    </Modal>
  );
};

// ─── main page ─────────────────────────────────────────────────────────────────

export const TemplatesPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const orgId = searchParams.get("org") ?? "";
  const navigate = useNavigate();

  const { items, loading, saving, remove, preview, send } = useTemplates(orgId);

  const user = getSession();
  const isAdmin = user?.scope === "GLOBAL" || user?.orgs?.[orgId]?.role === "ADMINISTRADOR";

  const [previewTarget, setPreviewTarget] = useState<Template | null>(null);
  const [sendTarget, setSendTarget] = useState<Template | null>(null);
  const [confirmId, setConfirmId] = useState<string | null>(null);

  const handleDelete = async (id: string) => {
    await remove(id);
    setConfirmId(null);
  };

  const handleSend = async (id: string, to: string, subject: string, sub: Record<string, string>) => {
    await send(id, { to, subject: subject || null, sub });
  };

  return (
    <>
      <PageMeta title="Plantillas" description="Gestión de plantillas de correo y SMS" />
      <ModuleBase
        pageTitle="Plantillas"
        breadcrumbItems={[
          { label: "Mis Empresas", path: "/my-companies" },
          ...(orgId ? [{ label: "Empresa", path: `/my-companies?org=${orgId}` }] : []),
        ]}
      >
        {loading ? (
          <div className="py-20"><Loader loaderText="Cargando plantillas..." /></div>
        ) : (
          <div className="flex flex-col gap-5">
            {isAdmin && (
              <div className="flex justify-end">
                <button
                  onClick={() => navigate(`/my-companies/templates/new?org=${orgId}`)}
                  className="inline-flex items-center gap-2 rounded-lg bg-brand-500 px-4 py-2.5 text-sm font-medium text-white shadow-theme-xs hover:bg-brand-600"
                >
                  <Plus size={16} />
                  Nueva plantilla
                </button>
              </div>
            )}

            {items.length === 0 ? (
              <p className="py-12 text-center text-sm text-gray-400 dark:text-gray-500">
                No hay plantillas registradas.
              </p>
            ) : (
              <div className="overflow-x-auto rounded-xl border border-gray-200 dark:border-gray-800">
                <Table>
                  <TableHeader>
                    <TableRow className="border-b border-gray-200 dark:border-gray-800">
                      {["Nombre", "Canal", "Estado", "Asunto", ""].map((h) => (
                        <TableCell key={h} isHeader className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wide text-gray-500 dark:text-gray-400">
                          {h}
                        </TableCell>
                      ))}
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {items.map((item) => (
                      <TableRow key={item.id} className="border-b border-gray-100 last:border-0 dark:border-gray-800">
                        <TableCell className="px-4 py-3 text-sm font-medium text-gray-800 dark:text-white/90">
                          {item.name}
                        </TableCell>
                        <TableCell className="px-4 py-3">
                          <span className="inline-flex items-center rounded-full bg-gray-100 px-2.5 py-0.5 text-xs font-medium text-gray-600 dark:bg-gray-800 dark:text-gray-300">
                            {item.channel}
                          </span>
                        </TableCell>
                        <TableCell className="px-4 py-3">
                          <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${STATUS_COLORS[item.status]}`}>
                            {STATUS_LABELS[item.status]}
                          </span>
                        </TableCell>
                        <TableCell className="px-4 py-3 text-sm text-gray-600 dark:text-gray-400">
                          {item.subject ?? "—"}
                        </TableCell>
                        <TableCell className="px-4 py-3">
                          {confirmId === item.id ? (
                            <div className="flex items-center gap-2">
                              <span className="text-xs text-gray-500 dark:text-gray-400">¿Eliminar?</span>
                              <button onClick={() => handleDelete(item.id)} disabled={saving} className="rounded px-2 py-1 text-xs font-medium text-error-600 hover:bg-error-50 disabled:opacity-50">Sí</button>
                              <button onClick={() => setConfirmId(null)} className="rounded px-2 py-1 text-xs font-medium text-gray-500 hover:bg-gray-100">No</button>
                            </div>
                          ) : (
                            <div className="flex items-center gap-1">
                              <button onClick={() => setPreviewTarget(item)} title="Vista previa" className="rounded p-1.5 text-gray-400 hover:bg-gray-100 hover:text-brand-500 dark:hover:bg-gray-800">
                                <Eye size={14} />
                              </button>
                              {item.channel === "EMAIL" && item.status === "ACTIVE" && (
                                <button onClick={() => setSendTarget(item)} title="Enviar" className="rounded p-1.5 text-gray-400 hover:bg-gray-100 hover:text-brand-500 dark:hover:bg-gray-800">
                                  <Mail size={14} />
                                </button>
                              )}
                              {isAdmin && (
                                <>
                                  <button
                                    onClick={() => navigate(`/my-companies/templates/${item.id}/edit?org=${orgId}`)}
                                    title="Editar"
                                    className="rounded p-1.5 text-gray-400 hover:bg-gray-100 hover:text-gray-600 dark:hover:bg-gray-800"
                                  >
                                    <Pencil size={14} />
                                  </button>
                                  <button onClick={() => setConfirmId(item.id)} title="Eliminar" className="rounded p-1.5 text-gray-400 hover:bg-error-50 hover:text-error-500">
                                    <Trash2 size={14} />
                                  </button>
                                </>
                              )}
                            </div>
                          )}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            )}
          </div>
        )}
      </ModuleBase>

      <TemplatePreviewModal
        isOpen={!!previewTarget}
        template={previewTarget}
        onClose={() => setPreviewTarget(null)}
        onPreview={preview}
      />

      <TemplateSendModal
        isOpen={!!sendTarget}
        template={sendTarget}
        saving={saving}
        onClose={() => setSendTarget(null)}
        onSend={handleSend}
      />
    </>
  );
};
