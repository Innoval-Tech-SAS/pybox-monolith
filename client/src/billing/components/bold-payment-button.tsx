import { useBoldPaymentButton } from "../hooks/use-bold-payment-button";
import type { BoldPaymentButtonProps } from "../types/props/bold-payment-button-props";

export const BoldPaymentButton: React.FC<BoldPaymentButtonProps> = ({ data, style = "dark-L" }) => {
  const containerRef = useBoldPaymentButton(data, style);
  return <div ref={containerRef} />;
};
