export interface GoogleButtonProps {
  text: string;
  onToken: (token: string) => void;
  disabled?: boolean;
}
