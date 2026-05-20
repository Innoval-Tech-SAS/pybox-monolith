import clsx from "clsx";
import { twMerge } from "tailwind-merge";
import { LabelProps } from "../../types/interfaces/props/label-props";

export const Label: FC<LabelProps> = ({ htmlFor, children, className }) => {
  return (
    <label
      htmlFor={htmlFor}
      className={clsx(
        twMerge(
          "mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-400",
          className,
        ),
      )}
    >
      {children}
    </label>
  );
};
