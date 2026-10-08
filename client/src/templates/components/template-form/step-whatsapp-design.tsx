import { Card, CardTitle } from "@/ui/components/card";
import { WhatsAppTemplateDesigner } from "@/templates/components/whatsapp-template-designer";
import type { StepWhatsAppDesignProps } from "@/templates/types/step-whatsapp-design-props";

export const StepWhatsAppDesign: React.FC<StepWhatsAppDesignProps> = (props) => (
  <Card className="flex h-full flex-col p-4! lg:p-5!">
    <CardTitle>Contenido del mensaje</CardTitle>
    <WhatsAppTemplateDesigner {...props} />
  </Card>
);
