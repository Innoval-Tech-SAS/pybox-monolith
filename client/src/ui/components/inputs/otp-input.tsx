import React, { useRef } from "react";
import { OtpInputProps } from "@/types/props/otp-input-props";

export const OtpInput: React.FC<OtpInputProps> = ({
  length = 6,
  value,
  onChange,
  disabled = false,
  error = false,
}) => {
  const inputsRef = useRef<HTMLInputElement[]>([]);

  const handleChange = (char: string, index: number) => {
    const updated = [...value];
    updated[index] = char.slice(-1);
    onChange(updated);
    if (char && index < length - 1) {
      inputsRef.current[index + 1]?.focus();
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>, index: number) => {
    if (e.key === "Backspace") {
      const updated = [...value];
      if (!value[index] && index > 0) {
        inputsRef.current[index - 1]?.focus();
      }
      updated[index] = "";
      onChange(updated);
    }
    if (e.key === "ArrowLeft" && index > 0) inputsRef.current[index - 1]?.focus();
    if (e.key === "ArrowRight" && index < length - 1) inputsRef.current[index + 1]?.focus();
  };

  const handlePaste = (e: React.ClipboardEvent<HTMLInputElement>) => {
    e.preventDefault();
    const chars = e.clipboardData.getData("text").replace(/\D/g, "").slice(0, length).split("");
    const updated = Array(length).fill("");
    chars.forEach((c, i) => { updated[i] = c; });
    onChange(updated);
    const lastIndex = Math.min(chars.length - 1, length - 1);
    inputsRef.current[lastIndex]?.focus();
  };

  const borderClass = error
    ? "border-error-500 focus:border-error-300 focus:ring-error-500/20"
    : "border-gray-300 focus:border-brand-300 focus:ring-brand-500/10 dark:border-gray-700 dark:focus:border-brand-800";

  return (
    <div role="group" aria-label="Código de verificación" className="flex gap-2 sm:gap-3">
      {Array.from({ length }).map((_, index) => (
        <input
          key={index}
          ref={(el) => { if (el) inputsRef.current[index] = el; }}
          type="text"
          inputMode="numeric"
          autoComplete={index === 0 ? "one-time-code" : "off"}
          maxLength={1}
          value={value[index] ?? ""}
          disabled={disabled}
          aria-label={`Dígito ${index + 1} de ${length}`}
          onChange={(e) => handleChange(e.target.value, index)}
          onKeyDown={(e) => handleKeyDown(e, index)}
          onPaste={handlePaste}
          className={`h-12 w-full rounded-lg border bg-transparent px-0 py-2 text-center text-xl font-semibold text-gray-800 shadow-theme-xs focus:outline-hidden focus:ring-3 dark:bg-gray-900 dark:text-white/90 ${borderClass} disabled:opacity-40`}
        />
      ))}
    </div>
  );
};
