import { LoaderProps } from "@/types/props/loader-props";

export const Loader: React.FC<LoaderProps> = ({
  loaderText = "Cargando...",
}) => {
  return (
    <div className="flex flex-col items-center justify-center w-full h-full">
      <div className="relative flex justify-center items-center">
        <div className="w-10 h-10 border-2 border-gray-200 rounded-full animate-spin border-t-gray-500 dark:border-white/20 dark:border-t-brand-500"></div>
      </div>
      <div className="mt-3 text-sm text-gray-500 font-light dark:text-gray-400">
        {loaderText}
      </div>
    </div>
  );
};
