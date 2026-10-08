import { useParams, useSearchParams } from "react-router";
import { Send } from "lucide-react";
import { PageMeta } from "@/ui/pages/page-meta";
import { ModuleBase } from "@/ui/components/common/module-base";
import { Loader } from "@/ui/components/loader/loader";
import { WizardForm } from "@/ui/components/wizard-form";
import { useBreadcrumb } from "@/companies/hooks/use-breadcrumb";
import { useCampaignEditor } from "@/campaigns/hooks/use-campaign-editor";
import { CAMPAIGN_WIZARD_STEPS } from "../constants/campaign-wizard-options";
import { StepDetails } from "../components/campaign-form/step-details";
import { StepChannel } from "../components/campaign-form/step-channel";
import { StepMessage } from "../components/campaign-form/step-message";
import { StepIvrFlow } from "../components/campaign-form/step-ivr-flow";
import { StepSchedule } from "../components/campaign-form/step-schedule";

export const CampaignEditorPage: React.FC = () => {
  const { id } = useParams<{ id?: string }>();
  const [searchParams] = useSearchParams();
  const portfolioId = searchParams.get("portfolio") ?? "";
  const { build } = useBreadcrumb();

  const {
    isEditing,
    portfolioName,
    form,
    set,
    loadingCampaign,
    saving,
    segments,
    channels,
    compatibleTemplates,
    selectedTemplate,
    showsSubject,
    isCall,
    ivrFlows,
    loadingFlows,
    designerHref,
    variables,
    recurringPeriodicities,
    weekdays,
    canSubmit,
    canAdvance,
    handleSubmit,
    backPath,
  } = useCampaignEditor(id, portfolioId);

  const breadcrumbItems = build({
    portfolio: { id: portfolioId, name: portfolioName },
    communications: true,
    trail: [{ label: "Campañas", path: backPath, icon: Send }],
  });

  const pageTitle = isEditing ? "Editar campaña" : "Nueva campaña";

  if (loadingCampaign) {
    return (
      <ModuleBase pageTitle={pageTitle} pageIcon={Send} breadcrumbItems={breadcrumbItems}>
        <div className="py-24">
          <Loader loaderText="Cargando campaña..." />
        </div>
      </ModuleBase>
    );
  }

  return (
    <>
      <PageMeta title={pageTitle} description="Editor de campañas de SMS y correo" />
      <ModuleBase
        pageTitle={pageTitle}
        pageIcon={Send}
        breadcrumbItems={breadcrumbItems}
      >
        <WizardForm
          steps={CAMPAIGN_WIZARD_STEPS}
          orientation="vertical"
          canAdvance={canAdvance}
          canSubmit={canSubmit}
          onSubmit={handleSubmit}
          loading={saving}
          submitLabel={isEditing ? "Guardar cambios" : "Crear campaña"}
          loadingLabel={isEditing ? "Guardando…" : "Creando…"}
        >
          {(step) => (
            <>
              {step === 0 && <StepDetails form={form} set={set} />}

              {step === 1 && (
                <StepChannel channels={channels} value={form.channelId} onChange={set("channelId")} />
              )}

              {step === 2 &&
                (isCall ? (
                  <StepIvrFlow
                    form={form}
                    segments={segments}
                    flows={ivrFlows}
                    loadingFlows={loadingFlows}
                    designerHref={designerHref}
                    set={set}
                  />
                ) : (
                  <StepMessage
                    form={form}
                    segments={segments}
                    compatibleTemplates={compatibleTemplates}
                    selectedTemplate={selectedTemplate}
                    showsSubject={showsSubject}
                    variables={variables}
                    set={set}
                  />
                ))}

              {step === 3 && (
                <StepSchedule
                  form={form}
                  recurringPeriodicities={recurringPeriodicities}
                  weekdays={weekdays}
                  set={set}
                />
              )}
            </>
          )}
        </WizardForm>
      </ModuleBase>
    </>
  );
};
