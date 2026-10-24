import type { PaymentAttemptStatus } from "@/types/billing/billing-types";
import {
  ATTEMPT_STATUS_TO_RESULT,
  PAYMENT_RESULT_CONFIG,
  PAYMENT_RESULT_DEFAULT,
} from "../constants/payment-result-config";
import type { PaymentResultConfig, PaymentResultStatus } from "../types/payment-result-types";

export const resolvePaymentResultConfig = (status: string): PaymentResultConfig =>
  PAYMENT_RESULT_CONFIG[status as PaymentResultStatus] ?? PAYMENT_RESULT_DEFAULT;

export const attemptStatusToResult = (status: PaymentAttemptStatus | undefined): PaymentResultStatus =>
  status ? ATTEMPT_STATUS_TO_RESULT[status] : "PENDING";
