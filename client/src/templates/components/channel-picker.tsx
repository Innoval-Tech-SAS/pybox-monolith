import { useChannels } from "@/campaigns/hooks/use-channels";
import { Loader } from "@/ui/components/loader/loader";
import { CHANNEL_ICON_BY_NAME, UNAVAILABLE_CHANNELS } from "@/templates/constants/template-wizard-options";
import { CHANNEL_PICKER_ICONS } from "@/templates/constants/channel-picker-icons";
import type { ChannelPickerProps } from "@/types/props/channel-picker-props";

export const ChannelPicker: React.FC<ChannelPickerProps> = ({ value, onChange, disabled = false }) => {
  const { channels, loading } = useChannels();

  if (loading) {
    return (
      <div className="py-12">
        <Loader loaderText="Cargando canales..." />
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
      {channels.map((channel) => {
        const isSelected = channel.name === value;
        const isComingSoon = UNAVAILABLE_CHANNELS.includes(channel.name);
        const isClickable = !disabled || isSelected;

        return (
          <button
            key={channel.id}
            type="button"
            disabled={!isClickable}
            onClick={() => onChange(channel.name)}
            className={`flex flex-col items-start gap-2 rounded-xl border p-4 text-left transition ${
              isSelected
                ? "border-brand-500 bg-brand-50 dark:border-brand-400 dark:bg-brand-500/10"
                : "border-gray-200 bg-white hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-900 dark:hover:bg-white/3"
            } ${!isClickable ? "cursor-not-allowed opacity-40" : ""}`}
          >
            <div className="flex w-full items-center justify-between">
              <span className={isSelected ? "text-brand-600 dark:text-brand-400" : "text-gray-500 dark:text-gray-400"}>
                {CHANNEL_PICKER_ICONS[CHANNEL_ICON_BY_NAME[channel.name]]}
              </span>
              {isComingSoon && (
                <span className="rounded-full bg-gray-100 px-2 py-0.5 text-[10px] font-medium uppercase tracking-wide text-gray-500 dark:bg-gray-800 dark:text-gray-400">
                  Próximamente
                </span>
              )}
            </div>
            <span className="text-sm font-semibold text-gray-800 dark:text-white/90">{channel.label}</span>
            <span className="text-xs text-gray-500 dark:text-gray-400">{channel.description}</span>
          </button>
        );
      })}
    </div>
  );
};
