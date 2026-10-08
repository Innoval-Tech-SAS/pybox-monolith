import { useState } from "react";
import { useNavigate } from "react-router";
import { Building2, FileText, User } from "lucide-react";
import { ModuleBase } from "@/ui/components/common/module-base";
import { StepSidebar } from "@/ui/components/wizard/step-sidebar";
import { useCountries } from "@/hooks/use-countries";
import {
  ORG_FISCAL_NAMES,
  ORG_MERCANTILE_NAMES,
} from "@/onboarding/constants/organization-documents";
import { StepCompanyInfo } from "../components/create-org/step-company-info";
import { StepDocuments } from "../components/create-org/step-documents";
import { StepRepresentative } from "../components/create-org/step-representative";
import { useRegisterOrg } from "../hooks/use-register-org";
import type { CreateOrgStepDef } from "@/companies/types/create-org-step-def";

export const CreateOrgPage: React.FC = () => {
  const navigate = useNavigate();
  const [step, setStep] = useState(1);

  const form = useRegisterOrg();
  const {
    name,
    sector,
    country,
    fiscalFile, fiscalError,
    mercantileFile, mercantileError,
    repFile, repFileError,
    repMode, selectedUser,
    repFirstname, repLastname, repEmail, repDocType, repDocNumber,
  } = form;

  const countriesData = useCountries();
  const { countries } = countriesData;
  const selectedCountry = countries.find((c) => c.code === country);
  const repDocTypes = selectedCountry?.documentTypes ?? [];
  const fiscalLabel = (country && ORG_FISCAL_NAMES[country]) ?? "Documento fiscal";
  const mercantileLabel = (country && ORG_MERCANTILE_NAMES[country]) ?? "Documento mercantil";

  const stepDefs: CreateOrgStepDef[] = [
    { label: "Empresa", description: "Información general", icon: <Building2 size={14} /> },
    { label: "Documentos", description: "Archivos requeridos", icon: <FileText size={14} /> },
    { label: "Representante", description: "Persona legal", icon: <User size={14} /> },
  ];

  const canGoStep2 = !!name.trim() && !!sector && !!country;
  const canGoStep3 =
    !!fiscalFile && !fiscalError && !!mercantileFile && !mercantileError;
  const repModeValid =
    repMode === "self" ||
    (repMode === "select" && !!selectedUser) ||
    (repMode === "create" &&
      !!repFirstname.trim() &&
      !!repLastname.trim() &&
      !!repEmail.trim() &&
      !!repDocType &&
      !!repDocNumber.trim());
  const canSubmit = !!repFile && !repFileError && repModeValid;

  const currentContent =
    step === 1 ? (
      <StepCompanyInfo
        form={form}
        countriesData={countriesData}
        fiscalLabel={fiscalLabel}
        canGoNext={canGoStep2}
        onNext={() => setStep(2)}
        onCancel={() => navigate("/my-companies")}
      />
    ) : step === 2 ? (
      <StepDocuments
        form={form}
        fiscalLabel={fiscalLabel}
        mercantileLabel={mercantileLabel}
        canGoNext={canGoStep3}
        onNext={() => setStep(3)}
        onBack={() => setStep(1)}
      />
    ) : (
      <StepRepresentative
        form={form}
        repDocTypes={repDocTypes}
        canSubmit={canSubmit}
        onBack={() => setStep(2)}
      />
    );

  return (
    <ModuleBase
      pageTitle="Crear empresa"
      pageIcon={Building2}
      breadcrumbItems={[]}
      showBack
    >
      <div className="flex gap-10">
        <aside className="hidden w-52 shrink-0 pt-1 lg:block">
          <StepSidebar steps={stepDefs} current={step} />
        </aside>
        <div className="hidden w-px self-stretch bg-gray-100 dark:bg-white/5 lg:block" />
        <div className="min-w-0 flex-1">{currentContent}</div>
      </div>
    </ModuleBase>
  );
};
