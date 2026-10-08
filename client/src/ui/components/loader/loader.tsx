import { LoaderProps } from "@/types/props/loader-props";
import { Spinner } from "@/ui/components/loader/spinner";

const variantClasses: Record<NonNullable<LoaderProps["variant"]>, string> = {
  inline: "",
  section: "min-h-60",
  page: "min-h-[60vh]",
};

export const Loader: React.FC<LoaderProps> = ({
  loaderText = "Cargando...",
  size = "md",
  variant = "inline",
  className = "",
}) => {
  const sm = size === "sm";
  return (
    <div
      className={`flex flex-col items-center justify-center w-full ${variantClasses[variant]} ${className}`}
    >
      <Spinner size={size} />
      <div
        className={`${sm ? "mt-1.5 text-xs" : "mt-3 text-sm"} text-gray-500 font-light dark:text-gray-400`}
      >
        {loaderText}
      </div>
    </div>
  );
};
