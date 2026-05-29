import { useState } from "react";
import { useSearchParams } from "react-router";
import { Plus, Pencil, Trash2 } from "lucide-react";
import { PageMeta } from "@/ui/pages/page-meta";
import { ModuleBase } from "@/ui/components/common/module-base";
import { Loader } from "@/ui/components/loader/loader";
import { Modal } from "@/ui/components/modal/modal";
import { Table, TableHeader, TableBody, TableRow, TableCell } from "@/ui/components/table/table";
import { Input } from "@/ui/components/inputs/input";
import { Label } from "@/ui/components/inputs/label";
import { getSession } from "@/auth/utils/auth-session-utils";
import { PAYMENT_METHOD_TYPE_LABELS } from "@/constants/payment-methods/payment-method-labels";
import { usePaymentMethods } from "../hooks/use-payment-methods";
import { usePaymentMethodTypes } from "../hooks/use-payment-method-types";
import type { PaymentMethod, PaymentMethodCreatePayload, PaymentMethodUpdatePayload } from "@/types/payment-methods/payment-method-types";

const EMPTY_FORM = {
  name: "",
  type: "",
  description: "",
  instructions: "",
  bankName: "",
  accountType: "",
  accountNumber: "",
  paymentLink: "",
  qrImageUrl: "",
};

type FormState = typeof EMPTY_FORM;

const selectClass =
  "w-full rounded-lg border border-gray-300 bg-transparent px-3 py-2.5 text-sm text-gray-800 shadow-theme-xs outline-none transition focus:border-brand-300 focus:ring-3 focus:ring-brand-500/20 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:focus:border-brand-800";

export const PaymentMethodsPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const orgId = searchParams.get("org") ?? "";

  const { items, loading, saving, create, update, remove } = usePaymentMethods(orgId);
  const { types } = usePaymentMethodTypes();

  const user = getSession();
  const isAdmin = user?.scope === "GLOBAL" || user?.orgs?.[orgId]?.role === "ADMIN";

  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<PaymentMethod | null>(null);
  const [form, setForm] = useState<FormState>(EMPTY_FORM);
  const [confirmDeleteId, setConfirmDeleteId] = useState<number | null>(null);

  const openCreate = () => {
    setEditing(null);
    setForm(EMPTY_FORM);
    setModalOpen(true);
  };

  const openEdit = (item: PaymentMethod) => {
    setEditing(item);
    setForm({
      name: item.name,
      type: item.type,
      description: item.description ?? "",
      instructions: item.instructions ?? "",
      bankName: item.bankName ?? "",
      accountType: item.accountType ?? "",
      accountNumber: item.accountNumber ?? "",
      paymentLink: item.paymentLink ?? "",
      qrImageUrl: item.qrImageUrl ?? "",
    });
    setModalOpen(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const nullable = (v: string) => v.trim() || null;

    if (editing) {
      const payload: PaymentMethodUpdatePayload = {
        name: form.name.trim(),
        type: form.type,
        description: nullable(form.description),
        instructions: nullable(form.instructions),
        bankName: nullable(form.bankName),
        accountType: nullable(form.accountType),
        accountNumber: nullable(form.accountNumber),
        paymentLink: nullable(form.paymentLink),
        qrImageUrl: nullable(form.qrImageUrl),
      };
      const result = await update(editing.id, payload);
      if (result) setModalOpen(false);
    } else {
      const payload: PaymentMethodCreatePayload = {
        organizationId: orgId,
        name: form.name.trim(),
        type: form.type,
        description: nullable(form.description),
        instructions: nullable(form.instructions),
        bankName: nullable(form.bankName),
        accountType: nullable(form.accountType),
        accountNumber: nullable(form.accountNumber),
        paymentLink: nullable(form.paymentLink),
        qrImageUrl: nullable(form.qrImageUrl),
      };
      const result = await create(payload);
      if (result) setModalOpen(false);
    }
  };

  const handleDelete = async () => {
    if (confirmDeleteId === null) return;
    await remove(confirmDeleteId);
    setConfirmDeleteId(null);
  };

  const field = (key: keyof FormState) => (
    (e: React.ChangeEvent<HTMLInputElement>) => setForm((p) => ({ ...p, [key]: e.target.value }))
  );

  return (
    <>
      <PageMeta title="Métodos de Pago" description="Gestión de métodos de pago de la organización" />
      <ModuleBase
        pageTitle="Métodos de Pago"
        breadcrumbItems={[
          { label: "Mis Empresas", path: "/my-companies" },
          ...(orgId ? [{ label: "Empresa", path: `/my-companies?org=${orgId}` }] : []),
        ]}
      >
        {loading ? (
          <div className="py-20"><Loader /></div>
        ) : (
          <div className="flex flex-col gap-5">
            {isAdmin && (
              <div className="flex justify-end">
                <button
                  onClick={openCreate}
                  className="inline-flex items-center gap-2 rounded-lg bg-brand-500 px-4 py-2.5 text-sm font-medium text-white shadow-theme-xs hover:bg-brand-600"
                >
                  <Plus size={16} />
                  Nuevo método
                </button>
              </div>
            )}

            {items.length === 0 ? (
              <p className="py-12 text-center text-sm text-gray-400 dark:text-gray-500">
                No hay métodos de pago registrados.
              </p>
            ) : (
              <div className="overflow-x-auto rounded-xl border border-gray-200 dark:border-gray-800">
                <Table>
                  <TableHeader>
                    <TableRow className="border-b border-gray-200 dark:border-gray-800">
                      {["Nombre", "Tipo", "Banco / Cuenta", "Estado", ...(isAdmin ? [""] : [])].map((h) => (
                        <TableCell
                          key={h}
                          isHeader
                          className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wide text-gray-500 dark:text-gray-400"
                        >
                          {h}
                        </TableCell>
                      ))}
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {items.map((item) => (
                      <TableRow
                        key={item.id}
                        className="border-b border-gray-100 last:border-0 dark:border-gray-800"
                      >
                        <TableCell className="px-4 py-3 text-sm font-medium text-gray-800 dark:text-white/90">
                          {item.name}
                        </TableCell>
                        <TableCell className="px-4 py-3 text-sm text-gray-600 dark:text-gray-400">
                          {PAYMENT_METHOD_TYPE_LABELS[item.type] ?? item.type}
                        </TableCell>
                        <TableCell className="px-4 py-3 text-sm text-gray-600 dark:text-gray-400">
                          {item.bankName
                            ? `${item.bankName}${item.accountNumber ? ` · ${item.accountNumber}` : ""}`
                            : "—"}
                        </TableCell>
                        <TableCell className="px-4 py-3">
                          <span
                            className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${
                              item.isActive
                                ? "bg-success-50 text-success-700 dark:bg-success-500/10 dark:text-success-400"
                                : "bg-gray-100 text-gray-500 dark:bg-gray-800 dark:text-gray-400"
                            }`}
                          >
                            {item.isActive ? "Activo" : "Inactivo"}
                          </span>
                        </TableCell>
                        {isAdmin && (
                          <TableCell className="px-4 py-3">
                            <div className="flex items-center gap-2">
                              <button
                                onClick={() => openEdit(item)}
                                className="rounded p-1.5 text-gray-400 hover:bg-gray-100 hover:text-gray-600 dark:hover:bg-gray-800 dark:hover:text-gray-300"
                              >
                                <Pencil size={14} />
                              </button>
                              <button
                                onClick={() => setConfirmDeleteId(item.id)}
                                className="rounded p-1.5 text-gray-400 hover:bg-error-50 hover:text-error-500 dark:hover:bg-error-500/10 dark:hover:text-error-400"
                              >
                                <Trash2 size={14} />
                              </button>
                            </div>
                          </TableCell>
                        )}
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            )}
          </div>
        )}
      </ModuleBase>

      {/* ── Create / Edit modal ── */}
      <Modal isOpen={modalOpen} onClose={() => setModalOpen(false)} className="max-w-lg w-full">
        <h3 className="mb-5 text-lg font-semibold text-gray-800 dark:text-white/90">
          {editing ? "Editar método de pago" : "Nuevo método de pago"}
        </h3>
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <div>
            <Label>Nombre <span className="text-error-500">*</span></Label>
            <Input value={form.name} onChange={field("name")} placeholder="Nombre del método" required />
          </div>
          <div>
            <Label>Tipo <span className="text-error-500">*</span></Label>
            <select
              value={form.type}
              onChange={(e) => setForm((p) => ({ ...p, type: e.target.value }))}
              className={selectClass}
              required
            >
              <option value="">Seleccionar tipo</option>
              {types.map((t) => (
                <option key={t} value={t}>{PAYMENT_METHOD_TYPE_LABELS[t] ?? t}</option>
              ))}
            </select>
          </div>
          <div>
            <Label>Descripción</Label>
            <Input value={form.description} onChange={field("description")} placeholder="Descripción opcional" />
          </div>
          <div>
            <Label>Instrucciones</Label>
            <Input value={form.instructions} onChange={field("instructions")} placeholder="Instrucciones de pago" />
          </div>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div>
              <Label>Banco</Label>
              <Input value={form.bankName} onChange={field("bankName")} placeholder="Nombre del banco" />
            </div>
            <div>
              <Label>Tipo de cuenta</Label>
              <Input value={form.accountType} onChange={field("accountType")} placeholder="Ahorros / Corriente" />
            </div>
            <div className="sm:col-span-2">
              <Label>Número de cuenta</Label>
              <Input value={form.accountNumber} onChange={field("accountNumber")} placeholder="Número de cuenta" />
            </div>
          </div>
          <div>
            <Label>Enlace de pago</Label>
            <Input value={form.paymentLink} onChange={field("paymentLink")} placeholder="https://..." />
          </div>
          <div>
            <Label>URL imagen QR</Label>
            <Input value={form.qrImageUrl} onChange={field("qrImageUrl")} placeholder="https://..." />
          </div>
          <div className="flex justify-end gap-3 pt-2">
            <button
              type="button"
              onClick={() => setModalOpen(false)}
              className="rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-300"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={saving}
              className="rounded-lg bg-brand-500 px-4 py-2.5 text-sm font-medium text-white hover:bg-brand-600 disabled:opacity-50"
            >
              {saving ? "Guardando..." : editing ? "Guardar cambios" : "Crear"}
            </button>
          </div>
        </form>
      </Modal>

      {/* ── Confirm delete modal ── */}
      <Modal isOpen={confirmDeleteId !== null} onClose={() => setConfirmDeleteId(null)} className="max-w-sm w-full">
        <h3 className="mb-3 text-lg font-semibold text-gray-800 dark:text-white/90">Eliminar método</h3>
        <p className="mb-5 text-sm text-gray-500 dark:text-gray-400">
          Esta acción no se puede deshacer.
        </p>
        <div className="flex justify-end gap-3">
          <button
            onClick={() => setConfirmDeleteId(null)}
            className="rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-300"
          >
            Cancelar
          </button>
          <button
            onClick={handleDelete}
            disabled={saving}
            className="rounded-lg bg-error-500 px-4 py-2.5 text-sm font-medium text-white hover:bg-error-600 disabled:opacity-50"
          >
            {saving ? "Eliminando..." : "Eliminar"}
          </button>
        </div>
      </Modal>
    </>
  );
};
