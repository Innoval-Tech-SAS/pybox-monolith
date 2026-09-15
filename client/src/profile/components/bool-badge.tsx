import { Badge } from "@/ui/components/badge";

export const BoolBadge = ({
  value,
  trueLabel = "Sí",
  falseLabel = "No",
}: {
  value?: boolean;
  trueLabel?: string;
  falseLabel?: string;
}) => (
  <Badge size="sm" color={value ? "success" : "light"} variant="light">
    {value ? trueLabel : falseLabel}
  </Badge>
);
