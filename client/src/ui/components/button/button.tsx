import { ButtonProps } from "@/types/props/button-props";
import { Spinner } from "@/ui/components/loader/spinner";
import {
  sizeClasses,
  variantClasses,
} from "@/ui/utils/button-utils";

export const Button: React.FC<ButtonProps> = ({
  children,
  size = "md",
  variant = "primary",
  startIcon,
  endIcon,
  onClick,
  className = "",
  disabled = false,
  loading = false,
  loadingText,
}) => {
  const isDisabled = disabled || loading;
  const spinnerTone = variant === "primary" ? "white" : "current";
  return (
    <button
      className={`inline-flex items-center justify-center gap-2 rounded-lg transition ${className} ${
        sizeClasses[size]
      } ${variantClasses[variant]} ${
        isDisabled ? "cursor-not-allowed opacity-50" : ""
      }`}
      onClick={onClick}
      disabled={isDisabled}
    >
      {loading ? (
        <Spinner size="xs" tone={spinnerTone} />
      ) : (
        startIcon && <span className="flex items-center">{startIcon}</span>
      )}
      {loading && loadingText ? loadingText : children}
      {!loading && endIcon && <span className="flex items-center">{endIcon}</span>}
    </button>
  );
};
