import { Calendar } from "@/ui/components/calendar/calendar";
import { useMyCredits } from "@/credits/hooks/use-my-credits";

export const SelfUserHome: React.FC = () => {
  const { credits, loading, error, refetch } = useMyCredits();

  return (
    <div className="flex flex-col gap-6">
      <header className="rounded-lg border border-gray-200 bg-white p-5 shadow-theme-xs dark:border-gray-800 dark:bg-gray-900">
        <p className="mb-1 text-xs font-semibold uppercase tracking-widest text-brand-500 dark:text-brand-400">
          Home personal
        </p>
        <h1 className="text-title-sm font-semibold text-gray-800 dark:text-white/90">
          Calendario financiero
        </h1>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Visualiza la fecha de tu próximo pago por crédito y el histórico de pagos aplicados.
        </p>
      </header>

      <Calendar
        credits={credits}
        loading={loading}
        error={error}
        onRetry={refetch}
      />
    </div>
  );
};
