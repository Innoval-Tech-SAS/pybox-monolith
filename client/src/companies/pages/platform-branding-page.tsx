import { Card, CardTitle } from "@/ui/components/card";
import { ModuleBase } from "@/ui/components/common/module-base";
import { LogoUploadCard } from "@/companies/components/logo-upload-card";
import { usePlatformBranding } from "@/companies/hooks/use-platform-branding";

export const PlatformBrandingPage: React.FC = () => {
  const { branding, saving, uploadLogo } = usePlatformBranding();

  return (
    <ModuleBase pageTitle="Marca de la plataforma">
      <Card>
        <CardTitle>Logo global</CardTitle>
        <p className="mb-4 text-sm text-gray-500 dark:text-gray-400">
          Se muestra a los usuarios que no pertenecen a ninguna organización (administradores y
          soporte global).
        </p>
        <LogoUploadCard
          logoUrl={branding?.logoUrl}
          saving={saving}
          onUpload={uploadLogo}
          label="Logo de la plataforma"
        />
      </Card>
    </ModuleBase>
  );
};
