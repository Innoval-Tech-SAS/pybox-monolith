import { useNavigate, useParams, useSearchParams } from "react-router";
import { Mail } from "lucide-react";
import { PageMeta } from "@/ui/pages/page-meta";
import { ModuleBase } from "@/ui/components/common/module-base";
import { Loader } from "@/ui/components/loader/loader";
import { Card, CardTitle } from "@/ui/components/card";
import { WizardForm } from "@/ui/components/wizard-form";
import { useTemplateVariables } from "@/templates/hooks/use-template-variables";
import { useTemplateEditorForm } from "@/templates/hooks/use-template-editor-form";
import { StepChannel } from "@/templates/components/template-form/step-channel";
import { StepInfo } from "@/templates/components/template-form/step-info";
import { StepDesign } from "@/templates/components/template-form/step-design";
import { StepWhatsAppInfo } from "@/templates/components/template-form/step-whatsapp-info";
import { StepWhatsAppDesign } from "@/templates/components/template-form/step-whatsapp-design";
import { StepWhatsAppPreview } from "@/templates/components/template-form/step-whatsapp-preview";
import { TemplatePreviewStep } from "@/templates/components/template-preview-step";
import { TEMPLATE_WIZARD_STEPS } from "@/templates/constants/template-wizard-options";
import { useOrgModule } from "@/companies/hooks/use-org-module";
import { useBreadcrumb } from "@/companies/hooks/use-breadcrumb";
import { usePortfolios } from "@/companies/hooks/use-portfolios";

export const TemplateEditorPage: React.FC = () => {
  const { id } = useParams<{ id?: string }>();
  const [searchParams] = useSearchParams();
  const portfolioId = searchParams.get("portfolio") ?? "";
  const { orgId, buildOrgPath } = useOrgModule();
  const { build } = useBreadcrumb();
  const navigate = useNavigate();

  const { portfolios } = usePortfolios(orgId);
  const portfolioName = portfolios.find((p) => p.id === portfolioId)?.name ?? "Portafolio";

  const backPath = buildOrgPath("/my-companies/templates", { portfolio: portfolioId });
  const breadcrumbItems = build({
    portfolio: { id: portfolioId, name: portfolioName },
    communications: true,
    trail: [{ label: "Plantillas", path: backPath, icon: Mail }],
  });
  const { variables, loading: loadingVariables } = useTemplateVariables(orgId);
  const {
    form,
    set,
    isEditing,
    loadingTemplate,
    saving,
    isEmail,
    isWhatsApp,
    whatsapp,
    isUnavailable,
    charLimit,
    isDesignValid,
    canAdvance,
    handleSubmit,
  } = useTemplateEditorForm(portfolioId, id, () => navigate(backPath), () => navigate(backPath), variables);

  const pageTitle = isEditing ? "Editar plantilla" : "Nueva plantilla";

  if (loadingTemplate) {
    return (
      <ModuleBase pageTitle={pageTitle} pageIcon={Mail} breadcrumbItems={breadcrumbItems}>
        <div className="py-24">
          <Loader loaderText="Cargando plantilla..." />
        </div>
      </ModuleBase>
    );
  }

  return (
    <>
      <PageMeta title={pageTitle} description="Editor de plantillas" />
      <ModuleBase
        pageTitle={pageTitle}
        pageIcon={Mail}
        breadcrumbItems={breadcrumbItems}
      >
        <WizardForm
          steps={TEMPLATE_WIZARD_STEPS}
          canAdvance={canAdvance}
          canSubmit={isDesignValid}
          onSubmit={handleSubmit}
          loading={saving}
          submitLabel={isEditing ? "Guardar cambios" : isWhatsApp ? "Crear y enviar a Meta" : "Crear plantilla"}
          loadingLabel={isEditing ? "Guardando…" : isWhatsApp ? "Enviando a Meta…" : "Creando…"}
        >
          {(step) => (
            <>
              {step === 0 && (
                <StepChannel channel={form.channel} disabled={isEditing} onChange={set("channel")} />
              )}

              {step === 1 && isWhatsApp && (
                <StepWhatsAppInfo
                  name={form.name}
                  whatsappForm={whatsapp.form}
                  onNameChange={set("name")}
                  onWhatsAppChange={whatsapp.set}
                />
              )}
              {step === 1 && !isWhatsApp && <StepInfo form={form} isEmail={isEmail} set={set} />}

              {step === 2 && isWhatsApp && (
                <StepWhatsAppDesign
                  form={whatsapp.form}
                  issues={whatsapp.issues}
                  variables={variables}
                  loadingVariables={loadingVariables}
                  onHeaderChange={whatsapp.set("headerText")}
                  onBodyChange={whatsapp.set("bodyText")}
                  onFooterChange={whatsapp.set("footerText")}
                />
              )}

              {step === 2 && !isWhatsApp && (
                <StepDesign
                  isEmail={isEmail}
                  isUnavailable={isUnavailable}
                  body={form.body}
                  design={form.design}
                  onBodyChange={set("body")}
                  onDesignChange={(html, design) => {
                    set("body")(html);
                    set("design")(design);
                  }}
                  charLimit={charLimit}
                  variables={variables}
                  loadingVariables={loadingVariables}
                />
              )}

              {step === 3 && isWhatsApp && (
                <StepWhatsAppPreview name={form.name} whatsappForm={whatsapp.form} variables={variables} />
              )}

              {step === 3 && !isWhatsApp && (
                <Card className="flex h-full flex-col">
                  <CardTitle>Vista previa</CardTitle>
                  <TemplatePreviewStep
                    channel={form.channel}
                    name={form.name}
                    subject={form.subject}
                    body={form.body}
                    variables={variables}
                  />
                </Card>
              )}
            </>
          )}
        </WizardForm>
      </ModuleBase>
    </>
  );
};
