import { useNavigate, useParams, useSearchParams } from "react-router";
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
import { TemplatePreviewStep } from "@/templates/components/template-preview-step";
import { TEMPLATE_WIZARD_STEPS } from "@/templates/constants/template-wizard-options";

export const TemplateEditorPage: React.FC = () => {
  const { id } = useParams<{ id?: string }>();
  const [searchParams] = useSearchParams();
  const orgId = searchParams.get("org") ?? "";
  const navigate = useNavigate();

  const backPath = `/my-companies/templates?org=${orgId}`;
  const { variables, loading: loadingVariables } = useTemplateVariables(orgId);
  const {
    form,
    set,
    isEditing,
    loadingTemplate,
    saving,
    isEmail,
    isUnavailable,
    charLimit,
    isDesignValid,
    canAdvance,
    handleSubmit,
  } = useTemplateEditorForm(orgId, id, () => navigate(backPath), () => navigate(backPath));

  const pageTitle = isEditing ? "Editar plantilla" : "Nueva plantilla";

  if (loadingTemplate) {
    return (
      <ModuleBase pageTitle={pageTitle} breadcrumbItems={[]}>
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
        breadcrumbItems={[
          { label: "Mis Empresas", path: "/my-companies" },
          { label: "Plantillas", path: backPath },
        ]}
      >
        <WizardForm
          steps={TEMPLATE_WIZARD_STEPS}
          canAdvance={canAdvance}
          canSubmit={isDesignValid}
          onSubmit={handleSubmit}
          loading={saving}
          submitLabel={isEditing ? "Guardar cambios" : "Crear plantilla"}
          loadingLabel={isEditing ? "Guardando…" : "Creando…"}
        >
          {(step) => (
            <>
              {step === 0 && (
                <StepChannel channel={form.channel} disabled={isEditing} onChange={set("channel")} />
              )}

              {step === 1 && <StepInfo form={form} isEmail={isEmail} set={set} />}

              {step === 2 && (
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

              {step === 3 && (
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
