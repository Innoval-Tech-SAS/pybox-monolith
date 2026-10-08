import { renderHook } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

const navigateMock = vi.fn();
vi.mock("react-router", () => ({
  useNavigate: () => navigateMock,
}));

const toastErrorMock = vi.fn();
vi.mock("@/context/toast-context", () => ({
  useToast: () => ({
    error: toastErrorMock,
    success: vi.fn(),
    info: vi.fn(),
    warning: vi.fn(),
    toasts: [],
    dismiss: vi.fn(),
  }),
}));

type MockResponseOptions = {
  ok?: boolean;
  headers?: Record<string, string>;
};

// Respuesta mínima compatible con lo que use-api-client lee: ok/status/headers.get/json.
const makeResponse = (status: number, body: unknown, options: MockResponseOptions = {}): Response => {
  const { ok = status >= 200 && status < 300, headers = {} } = options;
  return {
    ok,
    status,
    headers: { get: (key: string) => headers[key] ?? null },
    json: vi.fn().mockResolvedValue(body),
  } as unknown as Response;
};

describe("useApiClient", () => {
  beforeEach(() => {
    // _refreshPromise vive a nivel de módulo (mutex de refresh compartido entre
    // instancias del hook) -- vi.resetModules + import dinámico da un estado
    // limpio por test, igual que el patrón usado para bold-payment-button.
    vi.resetModules();
    navigateMock.mockClear();
    toastErrorMock.mockClear();
    sessionStorage.clear();
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("coalesces concurrent 401 'token expired' responses into a single /auth/refresh call", async () => {
    let refreshCalls = 0;
    const fetchMock = vi.fn((url: string) => {
      if (String(url).includes("/auth/refresh")) {
        refreshCalls += 1;
        return Promise.resolve(makeResponse(200, {}));
      }
      // Antes de que el refresh se dispare, cualquier request al endpoint recibe 401.
      // Después (retries), recibe 200. Esto es correcto sin importar el orden exacto
      // de interleaving entre las 3 llamadas concurrentes.
      if (refreshCalls === 0) {
        return Promise.resolve(makeResponse(401, { error: "El token expiró." }));
      }
      return Promise.resolve(makeResponse(200, { ok: true }));
    });
    vi.stubGlobal("fetch", fetchMock);

    const { useApiClient } = await import("@/hooks/use-api-client");
    const { result } = renderHook(() => useApiClient());

    await Promise.all([
      result.current.apiClient("/foo"),
      result.current.apiClient("/foo"),
      result.current.apiClient("/foo"),
    ]);

    const refreshFetchCalls = fetchMock.mock.calls.filter(([url]) => String(url).includes("/auth/refresh"));
    expect(refreshFetchCalls).toHaveLength(1);
  });

  it("clears the session and redirects to sign-in when refresh fails, without throwing", async () => {
    const fetchMock = vi.fn((url: string) => {
      if (String(url).includes("/auth/refresh")) {
        return Promise.resolve(makeResponse(401, {}, { ok: false }));
      }
      return Promise.resolve(makeResponse(401, { error: "El token expiró." }));
    });
    vi.stubGlobal("fetch", fetchMock);
    sessionStorage.setItem("mfaVerified", "true");
    sessionStorage.setItem("otherKey", "shouldAlsoBeCleared");

    const { useApiClient } = await import("@/hooks/use-api-client");
    const { result } = renderHook(() => useApiClient());

    const outcome = await result.current.apiClient("/foo");

    expect(outcome).toBeNull();
    // jsdom no permite espiar Storage.prototype.clear directamente (no es una
    // propiedad propia asignable) -- se verifica el efecto observable: la sesión
    // completa quedó vacía, no solo la clave de MFA.
    expect(sessionStorage.getItem("mfaVerified")).toBeNull();
    expect(sessionStorage.getItem("otherKey")).toBeNull();
    expect(navigateMock).toHaveBeenCalledWith("/admin/sign-in", { replace: true });
  });

  it("extracts a string 'error' field and forwards it to the toast", async () => {
    const fetchMock = vi.fn(() => Promise.resolve(makeResponse(400, { error: "Mensaje custom" })));
    vi.stubGlobal("fetch", fetchMock);

    const { useApiClient } = await import("@/hooks/use-api-client");
    const { result } = renderHook(() => useApiClient());

    await expect(result.current.apiClient("/foo")).rejects.toThrow("Mensaje custom");
    expect(toastErrorMock).toHaveBeenCalledWith("Error", "Mensaje custom");
  });

  it("clears mfaVerified and dispatches 'mfa-pending' on the exact 403 MFA message", async () => {
    const fetchMock = vi.fn(() =>
      Promise.resolve(makeResponse(403, { error: "Verificación de dos pasos pendiente." })),
    );
    vi.stubGlobal("fetch", fetchMock);
    sessionStorage.setItem("mfaVerified", "true");

    const mfaPendingSpy = vi.fn();
    window.addEventListener("mfa-pending", mfaPendingSpy);

    const { useApiClient } = await import("@/hooks/use-api-client");
    const { result } = renderHook(() => useApiClient());

    await expect(result.current.apiClient("/foo")).rejects.toThrow();

    expect(sessionStorage.getItem("mfaVerified")).toBeNull();
    expect(mfaPendingSpy).toHaveBeenCalledTimes(1);

    window.removeEventListener("mfa-pending", mfaPendingSpy);
  });

  it("does not dispatch 'mfa-pending' for other 403 messages", async () => {
    const fetchMock = vi.fn(() =>
      Promise.resolve(makeResponse(403, { error: "No tienes permisos para esta acción." })),
    );
    vi.stubGlobal("fetch", fetchMock);

    const mfaPendingSpy = vi.fn();
    window.addEventListener("mfa-pending", mfaPendingSpy);

    const { useApiClient } = await import("@/hooks/use-api-client");
    const { result } = renderHook(() => useApiClient());

    await expect(result.current.apiClient("/foo")).rejects.toThrow();

    expect(mfaPendingSpy).not.toHaveBeenCalled();

    window.removeEventListener("mfa-pending", mfaPendingSpy);
  });

  it("returns null for a 204 response without calling response.json()", async () => {
    const response = makeResponse(204, undefined);
    const fetchMock = vi.fn(() => Promise.resolve(response));
    vi.stubGlobal("fetch", fetchMock);

    const { useApiClient } = await import("@/hooks/use-api-client");
    const { result } = renderHook(() => useApiClient());

    const outcome = await result.current.apiClient("/foo");

    expect(outcome).toBeNull();
    expect(response.json).not.toHaveBeenCalled();
  });

  it("returns null when content-length is '0' without calling response.json()", async () => {
    const response = makeResponse(200, undefined, { headers: { "content-length": "0" } });
    const fetchMock = vi.fn(() => Promise.resolve(response));
    vi.stubGlobal("fetch", fetchMock);

    const { useApiClient } = await import("@/hooks/use-api-client");
    const { result } = renderHook(() => useApiClient());

    const outcome = await result.current.apiClient("/foo");

    expect(outcome).toBeNull();
    expect(response.json).not.toHaveBeenCalled();
  });

  it("does not set Content-Type when the body is FormData", async () => {
    const response = makeResponse(200, { ok: true });
    const fetchMock = vi.fn(() => Promise.resolve(response));
    vi.stubGlobal("fetch", fetchMock);

    const { useApiClient } = await import("@/hooks/use-api-client");
    const { result } = renderHook(() => useApiClient());

    const formData = new FormData();
    formData.append("file", "content");

    await result.current.apiClient("/upload", { method: "POST", body: formData });

    const [, init] = fetchMock.mock.calls[0];
    const headers = (init as RequestInit).headers as Record<string, string>;
    expect(headers["Content-Type"]).toBeUndefined();
  });
});
