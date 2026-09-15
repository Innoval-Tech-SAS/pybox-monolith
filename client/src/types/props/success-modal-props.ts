export interface SuccessModalProps {
  isOpen: boolean;
  title: string;
  description: React.ReactNode;
  actionLabel: string;
  onAction: () => void;
}
