import { act, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { MfaGuard } from "@/auth/components/mfa-guard";

const requestOtpMock = vi.fn().mockResolvedValue(undefined);
const verifyOtpMock = vi.fn().mockResolvedValue(undefined);
const clearErrorMock = vi.fn();

vi.mock("@/hooks/use-verify-otp", () => ({
  useVerifyOtp: () => ({
    requestOtp: requestOtpMock,
    verifyOtp: verifyOtpMock,
    loading: false,
    error: null,
    clearError: clearErrorMock,
  }),
}));

const renderGuard = () =>
  render(
    <MfaGuard>
      <div>Contenido protegido</div>
    </MfaGuard>,
  );

describe("MfaGuard", () => {
  beforeEach(() => {
    sessionStorage.clear();
    requestOtpMock.mockClear();
    verifyOtpMock.mockClear();
    clearErrorMock.mockClear();
  });

  it("renders children directly when mfaVerified is already true in sessionStorage", () => {
    sessionStorage.setItem("mfaVerified", "true");
    renderGuard();

    expect(screen.getByText("Contenido protegido")).toBeInTheDocument();
    expect(screen.queryByText("Enviar código por correo")).not.toBeInTheDocument();
  });

  it("shows the channel selection screen, not the children, when mfaVerified is missing", () => {
    renderGuard();

    expect(screen.getByText("Enviar código por correo")).toBeInTheDocument();
    expect(screen.getByText("Enviar código por SMS")).toBeInTheDocument();
    expect(screen.queryByText("Contenido protegido")).not.toBeInTheDocument();
  });

  it("stores mfaVerified and renders children after a correct OTP verification", async () => {
    const user = userEvent.setup();
    renderGuard();

    await user.click(screen.getByText("Enviar código por correo"));
    expect(requestOtpMock).toHaveBeenCalledWith("EMAIL");

    for (let i = 1; i <= 6; i++) {
      const input = screen.getByLabelText(`Dígito ${i} de 6`);
      await user.type(input, String(i));
    }

    const verifyButton = screen.getByRole("button", { name: "Verificar" });
    expect(verifyButton).not.toBeDisabled();
    await user.click(verifyButton);

    expect(verifyOtpMock).toHaveBeenCalledWith("EMAIL", "123456");
    expect(sessionStorage.getItem("mfaVerified")).toBe("true");
    expect(screen.getByText("Contenido protegido")).toBeInTheDocument();
  });

  it("keeps the Verificar button disabled with fewer than 6 digits entered", async () => {
    const user = userEvent.setup();
    renderGuard();

    await user.click(screen.getByText("Enviar código por correo"));

    for (let i = 1; i <= 3; i++) {
      const input = screen.getByLabelText(`Dígito ${i} de 6`);
      await user.type(input, String(i));
    }

    expect(screen.getByRole("button", { name: "Verificar" })).toBeDisabled();
  });

  it("re-shows the OTP screen when a 'mfa-pending' event fires, even after mfaVerified was true", () => {
    // Cubre el fix: el flag de sesión del servidor pudo expirar aunque
    // sessionStorage.mfaVerified siguiera en "true" -- use-api-client dispara este
    // evento ante un 403 con el mensaje exacto de MFA pendiente, y el guard debe
    // volver a pedir el OTP en vez de dejar pasar al usuario. `children` sigue
    // montado (ver mfa-guard.tsx: layoutUnlockedOnce) para no perder el estado de
    // navbar/sidebar/chat -- el modal de OTP solo se superpone encima.
    sessionStorage.setItem("mfaVerified", "true");
    renderGuard();
    expect(screen.getByText("Contenido protegido")).toBeInTheDocument();

    act(() => {
      window.dispatchEvent(new Event("mfa-pending"));
    });

    expect(screen.getByText("Contenido protegido")).toBeInTheDocument();
    expect(screen.getByText("Enviar código por correo")).toBeInTheDocument();
  });
});
