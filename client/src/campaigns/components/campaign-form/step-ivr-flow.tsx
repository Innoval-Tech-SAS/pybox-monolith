import { Link } from "react-router";
import { Phone, Plus, Pencil } from "lucide-react";
import { Card, CardTitle } from "@/ui/components/card";
import { Select } from "@/ui/components/inputs/select";
import { Switch } from "@/ui/components/switch";
import type { StepIvrFlowProps } from "@/campaigns/types/step-ivr-flow-props";

/**
 * Paso de destinatarios + flujo IVR para campañas del canal de llamadas (CALL).
 * Reemplaza al paso de mensaje/plantilla. El flujo se diseña en el Diseñador IVR
 * y aquí solo se selecciona uno guardado.
 */
export const StepIvrFlow: React.FC<StepIvrFlowProps> = ({
  form,
  segments,
  flows,
  loadingFlows,
  designerHref,
  set,
}) => (
  <div className="flex h-full flex-col gap-5">
    <Card>
      <CardTitle>Destinatarios y flujo de llamada</CardTitle>
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2">
        <div>
          <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-400">
            Segmento de destinatarios
          </label>
          <Select
            options={segments.map((s) => ({ value: String(s.id), label: s.name }))}
            value={form.segmentId}
            onChange={(v) => set("segmentId")(v)}
            placeholder="Selecciona un segmento"
          />
        </div>

        <div>
          <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-400">
            Flujo IVR *
          </label>
          <Select
            options={flows.map((f) => ({ value: f.id, label: f.name }))}
            value={form.ivrFlowId}
            onChange={(v) => set("ivrFlowId")(v)}
            placeholder={loadingFlows ? "Cargando flujos…" : "Selecciona un flujo"}
            disabled={loadingFlows || flows.length === 0}
          />
          {!loadingFlows && flows.length === 0 && (
            <p className="mt-1.5 text-xs text-gray-400 dark:text-gray-500">
              Aún no hay flujos IVR. Crea uno en el diseñador.
            </p>
          )}
        </div>

        <div className="sm:col-span-2">
          <Switch
            checked={form.fallback}
            onChange={set("fallback")}
            label="Usar canal de respaldo si falla el envío"
          />
        </div>
      </div>
    </Card>

    <Card className="flex min-h-0 flex-1 flex-col">
      <div className="flex flex-1 flex-col items-center justify-center gap-4 rounded-xl border border-dashed border-gray-200 p-8 text-center dark:border-gray-700">
        <Phone size={28} className="text-brand-500" />
        <p className="max-w-md text-sm text-gray-500 dark:text-gray-400">
          El flujo de llamada (audios, menús, transferencias y capturas) se diseña en el Diseñador
          IVR. Selecciona un flujo guardado o crea/edita uno.
        </p>
        <div className="flex items-center gap-2">
          <Link
            to={designerHref()}
            className="inline-flex items-center gap-1.5 rounded-lg bg-brand-500 px-3 py-2 text-xs font-medium text-white hover:bg-brand-600"
          >
            <Plus size={14} /> Nuevo flujo
          </Link>
          {form.ivrFlowId && (
            <Link
              to={designerHref(form.ivrFlowId)}
              className="inline-flex items-center gap-1.5 rounded-lg border border-brand-500 px-3 py-2 text-xs font-medium text-brand-600 hover:bg-brand-500 hover:text-white dark:text-brand-400"
            >
              <Pencil size={14} /> Editar flujo seleccionado
            </Link>
          )}
        </div>
      </div>
    </Card>
  </div>
);
