import { useState } from "react";
import { useNavigate, useSearchParams } from "react-router";
import { Pause, Pencil, Play, Plus, Trash2 } from "lucide-react";
import { PageMeta } from "@/ui/pages/page-meta";
import { ModuleBase } from "@/ui/components/common/module-base";
import { Loader } from "@/ui/components/loader/loader";
import {
  Table,
  TableBody,
  TableCell,
  TableHeader,
  TableRow,
} from "@/ui/components/table/table";
import { getSession } from "@/auth/utils/auth-session-utils";
import { useCampaigns } from "../hooks/use-campaigns";
import { STATUS_LABELS, STATUS_COLORS, formatSchedule } from "../utils/campaign-utils";

export const CampaignsPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const orgId = searchParams.get("org") ?? "";
  const navigate = useNavigate();

  const { items, loading, saving, remove, activate, pause } = useCampaigns(orgId);

  const user = getSession();
  const isAdmin = user?.scope === "GLOBAL" || user?.orgs?.[orgId]?.role === "ADMINISTRADOR";

  const [confirmId, setConfirmId] = useState<string | null>(null);

  const handleDelete = async (id: string) => {
    await remove(id);
    setConfirmId(null);
  };

  return (
    <>
      <PageMeta title="Campañas" description="Gestión de campañas de SMS y correo automáticas" />
      <ModuleBase
        pageTitle="Campañas"
        breadcrumbItems={[
          { label: "Mis Empresas", path: "/my-companies" },
          ...(orgId ? [{ label: "Empresa", path: `/my-companies?org=${orgId}` }] : []),
        ]}
      >
        {loading ? (
          <div className="py-20"><Loader loaderText="Cargando campañas..." /></div>
        ) : (
          <div className="flex flex-col gap-5">
            {isAdmin && (
              <div className="flex justify-end">
                <button
                  onClick={() => navigate(`/my-companies/campaigns/new?org=${orgId}`)}
                  className="inline-flex items-center gap-2 rounded-lg bg-brand-500 px-4 py-2.5 text-sm font-medium text-white shadow-theme-xs hover:bg-brand-600"
                >
                  <Plus size={16} />
                  Nueva campaña
                </button>
              </div>
            )}

            {items.length === 0 ? (
              <p className="py-12 text-center text-sm text-gray-400 dark:text-gray-500">
                No hay campañas registradas.
              </p>
            ) : (
              <div className="overflow-x-auto rounded-xl border border-gray-200 dark:border-gray-800">
                <Table>
                  <TableHeader>
                    <TableRow className="border-b border-gray-200 dark:border-gray-800">
                      {["Nombre", "Canal", "Estado", "Programación", "Destinatarios", ""].map((h) => (
                        <TableCell key={h} isHeader className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wide text-gray-500 dark:text-gray-400">
                          {h}
                        </TableCell>
                      ))}
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {items.map((item) => (
                      <TableRow key={item.id} className="border-b border-gray-100 last:border-0 dark:border-gray-800">
                        <TableCell className="px-4 py-3">
                          <p className="text-sm font-medium text-gray-800 dark:text-white/90">{item.name}</p>
                          {item.description && (
                            <p className="text-xs text-gray-400 dark:text-gray-500">{item.description}</p>
                          )}
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
                          {formatSchedule(item)}
                        </TableCell>
                        <TableCell className="px-4 py-3 text-sm text-gray-600 dark:text-gray-400">
                          {item.totalRecipients}
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
                              {isAdmin && (item.status === "borrador" || item.status === "pausada") && (
                                <button onClick={() => activate(item.id)} disabled={saving} title="Activar" className="rounded p-1.5 text-gray-400 hover:bg-success-50 hover:text-success-600 disabled:opacity-50">
                                  <Play size={14} />
                                </button>
                              )}
                              {isAdmin && item.status === "programada" && (
                                <button onClick={() => pause(item.id)} disabled={saving} title="Pausar" className="rounded p-1.5 text-gray-400 hover:bg-orange-50 hover:text-orange-600 disabled:opacity-50">
                                  <Pause size={14} />
                                </button>
                              )}
                              {isAdmin && (item.status === "borrador" || item.status === "pausada") && (
                                <button
                                  onClick={() => navigate(`/my-companies/campaigns/${item.id}/edit?org=${orgId}`)}
                                  title="Editar"
                                  className="rounded p-1.5 text-gray-400 hover:bg-gray-100 hover:text-gray-600 dark:hover:bg-gray-800"
                                >
                                  <Pencil size={14} />
                                </button>
                              )}
                              {isAdmin && (
                                <button onClick={() => setConfirmId(item.id)} title="Eliminar" className="rounded p-1.5 text-gray-400 hover:bg-error-50 hover:text-error-500">
                                  <Trash2 size={14} />
                                </button>
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
    </>
  );
};
