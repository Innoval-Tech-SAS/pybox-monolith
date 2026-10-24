export interface CardFieldsValue {
  number: string;
  cvc: string;
  expMonth: string;
  expYear: string;
  cardHolder: string;
  installments: number;
}

export interface WompiCardFieldsProps {
  value: CardFieldsValue;
  onChange: (value: CardFieldsValue) => void;
}
