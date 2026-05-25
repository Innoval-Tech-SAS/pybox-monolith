import { Calendar } from "@/ui/components/calendar/calendar";
import { useMyCredits } from "@/credits/hooks/use-my-credits";
import { ModuleBase } from "@/ui/components/common/module-base";

export const SelfUserHome: React.FC = () => {
  const { credits, loading, error, refetch } = useMyCredits();

  return (
    <ModuleBase pageTitle="Calendario financiero">
      <Calendar
        credits={credits}
        loading={loading}
        error={error}
        onRetry={refetch}
      />
    </ModuleBase>
  );
};
