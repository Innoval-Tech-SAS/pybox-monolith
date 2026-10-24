import { useCallback, useState } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import type {
  IvrNode,
  IvrEdge,
  IvrDefaults,
  IvrRedial,
  IvrOutcomeMap,
  IvrPacing,
} from "@/ivr/types/ivr-node-types";
import type { IvrFlowRecord } from "@/ivr/types/ivr-flow-record";
import type { AmdPreset, AmdVariables } from "@/ivr/constants/amd-presets";
import { serializeFlow } from "@/ivr/utils/ivr-utils";
import { compileFlow } from "@/ivr/utils/compile-flow";

export type SaveFlowParams = {
  /** Id del flujo en el backend (solo al editar). */
  backendId?: string | null;
  name: string;
  nodes: IvrNode[];
  edges: IvrEdge[];
  entryNodeId: string | null;
  defaults: IvrDefaults;
  redial: IvrRedial;
  amdPreset: AmdPreset;
  amd: AmdVariables;
  /** Etiquetas de resultado indexadas por id de nodo. */
  outcomes: IvrOutcomeMap;
  pacing: IvrPacing;
};

export type SaveFlowResult = {
  ok: boolean;
  flow: IvrFlowRecord | null;
  /** Errores de validación/compilación (bloquean el guardado). */
  errors: string[];
  /** Avisos que no impiden guardar (ver `CompileResult.warnings`). */
  warnings: string[];
};

/**
 * Persistencia real de flujos IVR contra `/ivr/flows`. Al guardar, compila el
 * grafo al `CampaignIvrConfig` de Helena (bloquea si hay errores) y envía tanto
 * el `config` compilado como el `graph` crudo (para reeditar).
 */
export const useSaveFlow = (portfolioId: string) => {
  const { apiClient } = useApiClient();
  const [saving, setSaving] = useState(false);

  const listFlows = useCallback(async (): Promise<IvrFlowRecord[]> => {
    if (!portfolioId) return [];
    try {
      return (await apiClient(`/ivr/flows/?portfolioId=${portfolioId}`, { method: "GET" })) ?? [];
    } catch {
      return [];
    }
  }, [apiClient, portfolioId]);

  const loadFlow = useCallback(
    async (id: string): Promise<IvrFlowRecord | null> => {
      if (!portfolioId) return null;
      try {
        return await apiClient(`/ivr/flows/${id}?portfolioId=${portfolioId}`, { method: "GET" });
      } catch {
        return null;
      }
    },
    [apiClient, portfolioId],
  );

  const saveFlow = useCallback(
    async (params: SaveFlowParams): Promise<SaveFlowResult> => {
      const { errors, warnings, config, redialConfig, outcomes } = compileFlow({
        nodes: params.nodes,
        edges: params.edges,
        entryNodeId: params.entryNodeId,
        defaults: params.defaults,
        redial: params.redial,
        outcomes: params.outcomes,
      });
      if (errors.length > 0 || !config) return { ok: false, flow: null, errors, warnings };

      const graph = serializeFlow({
        id: params.backendId ?? "",
        name: params.name,
        nodes: params.nodes,
        edges: params.edges,
        entryNodeId: params.entryNodeId,
        defaults: params.defaults,
        redial: params.redial,
        amdPreset: params.amdPreset,
        amd: params.amd,
        outcomes: params.outcomes,
      });

      const body = JSON.stringify({
        name: params.name,
        config,
        graph,
        redialConfig,
        variables: params.amd,
        outcomes,
        callsPerSecond: params.pacing.callsPerSecond,
        maxConcurrent: params.pacing.maxConcurrent,
        callerId: params.pacing.callerId.trim() || null,
        contactPolicyId: params.pacing.contactPolicyId.trim() || null,
      });

      setSaving(true);
      try {
        const flow: IvrFlowRecord = params.backendId
          ? await apiClient(`/ivr/flows/${params.backendId}?portfolioId=${portfolioId}`, {
              method: "PATCH",
              body,
            })
          : await apiClient(`/ivr/flows/?portfolioId=${portfolioId}`, { method: "POST", body });
        return { ok: !!flow, flow, errors: [], warnings };
      } catch {
        return {
          ok: false,
          flow: null,
          errors: ["No se pudo guardar el flujo."],
          warnings,
        };
      } finally {
        setSaving(false);
      }
    },
    [apiClient, portfolioId],
  );

  const removeFlow = useCallback(
    async (id: string): Promise<boolean> => {
      try {
        await apiClient(`/ivr/flows/${id}?portfolioId=${portfolioId}`, { method: "DELETE" });
        return true;
      } catch {
        return false;
      }
    },
    [apiClient, portfolioId],
  );

  return { saving, listFlows, loadFlow, saveFlow, removeFlow };
};
