export interface PayuPayerFieldsValue {
  fullName: string;
  userLegalIdType: string;
  userLegalId: string;
  address: string;
  city: string;
}

export interface PayuPayerFieldsProps {
  value: PayuPayerFieldsValue;
  onChange: (value: PayuPayerFieldsValue) => void;
  idPrefix: string;
}
