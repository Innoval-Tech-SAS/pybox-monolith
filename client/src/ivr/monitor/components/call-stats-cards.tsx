import {
  CheckCircle2,
  PhoneCall,
  PhoneForwarded,
  PhoneMissed,
  PhoneOff,
  Hash,
  User,
  Voicemail,
} from "lucide-react";
import type { LucideIcon } from "lucide-react";
import type { IvrCampaignStats } from "../types/ivr-monitor-types";

interface StatCard {
  key: keyof IvrCampaignStats;
  label: string;
  icon: LucideIcon;
  tone: string;
  hint?: string;
}

const CARDS: StatCard[] = [
  { key: "totalCalls", label: "Llamadas", icon: PhoneCall, tone: "text-gray-500 dark:text-gray-400" },
  { key: "activeCalls", label: "En curso", icon: PhoneCall, tone: "text-brand-500" },
  {
    key: "humanDetections",
    label: "Personas",
    icon: User,
    tone: "text-success-500",
    hint: "Acumulado: incluye llamadas que ya terminaron",
  },
  {
    key: "machineDetections",
    label: "Contestadoras",
    icon: Voicemail,
    tone: "text-orange-500",
    hint: "Acumulado: incluye llamadas que ya terminaron",
  },
  {
    key: "menuSelections",
    label: "Con pulsación",
    icon: Hash,
    tone: "text-brand-500",
    hint: "Llamadas donde el cliente marcó al menos una tecla",
  },
  { key: "transfers", label: "Transferidas", icon: PhoneForwarded, tone: "text-purple-500" },
  { key: "completed", label: "Completadas", icon: CheckCircle2, tone: "text-success-600" },
  { key: "noAnswer", label: "Sin respuesta", icon: PhoneMissed, tone: "text-warning-500" },
  { key: "failed", label: "Fallidas", icon: PhoneOff, tone: "text-error-500" },
];

interface CallStatsCardsProps {
  stats: IvrCampaignStats;
}

export const CallStatsCards: React.FC<CallStatsCardsProps> = ({ stats }) => (
  <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-5 xl:grid-cols-9">
    {CARDS.map(({ key, label, icon: Icon, tone, hint }) => (
      <div
        key={key}
        title={hint}
        className="rounded-xl border border-gray-200 bg-white px-4 py-3 dark:border-white/5 dark:bg-white/3"
      >
        <div className="flex items-center gap-1.5">
          <Icon size={14} className={tone} />
          <span className="truncate text-xs text-gray-500 dark:text-gray-400">{label}</span>
        </div>
        <p className="mt-1 text-xl font-semibold text-gray-800 dark:text-white/90">
          {stats[key]}
        </p>
      </div>
    ))}
  </div>
);
