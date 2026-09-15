import { act, renderHook, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { useFileAvailability } from "@/support/hooks/use-file-availability";

type MockResponseOptions = {
  ok?: boolean;
  status?: number;
  contentType?: string;
};

const makeResponse = ({ ok = true, status = 200, contentType = "application/pdf" }: MockResponseOptions = {}) =>
  ({
    ok,
    status,
    headers: { get: (key: string) => (key.toLowerCase() === "content-type" ? contentType : null) },
  }) as unknown as Response;

describe("useFileAvailability", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn());
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("is unavailable without hitting the network when there is no url", () => {
    const { result } = renderHook(() => useFileAvailability(""));
    expect(result.current.fileStatus).toBe("unavailable");
    expect(fetch).not.toHaveBeenCalled();
  });

  it("resolves to available for a HEAD 200 with a non-JSON content-type", async () => {
    vi.mocked(fetch).mockResolvedValue(makeResponse());
    const { result } = renderHook(() => useFileAvailability("https://files/doc.pdf"));

    expect(result.current.fileStatus).toBe("checking");
    await waitFor(() => expect(result.current.fileStatus).toBe("available"));
    expect(fetch).toHaveBeenCalledWith(
      "https://files/doc.pdf",
      expect.objectContaining({ method: "HEAD" }),
    );
  });

  it("resolves to unavailable when the HEAD response is JSON (an error page disguised as 200)", async () => {
    vi.mocked(fetch).mockResolvedValue(makeResponse({ contentType: "application/json" }));
    const { result } = renderHook(() => useFileAvailability("https://files/doc.pdf"));

    await waitFor(() => expect(result.current.fileStatus).toBe("unavailable"));
  });

  it("falls back to a ranged GET when HEAD is not supported (405), and uses its result", async () => {
    vi.mocked(fetch)
      .mockResolvedValueOnce(makeResponse({ ok: false, status: 405 }))
      .mockResolvedValueOnce(makeResponse({ contentType: "application/pdf" }));

    const { result } = renderHook(() => useFileAvailability("https://files/doc.pdf"));

    await waitFor(() => expect(result.current.fileStatus).toBe("available"));
    expect(fetch).toHaveBeenCalledTimes(2);
    const [, getOptions] = vi.mocked(fetch).mock.calls[1];
    expect((getOptions as RequestInit).headers).toMatchObject({ Range: "bytes=0-0" });
  });

  it("treats a network error as available (optimistic: let the iframe try)", async () => {
    vi.mocked(fetch).mockRejectedValue(new TypeError("Failed to fetch"));
    const { result } = renderHook(() => useFileAvailability("https://files/doc.pdf"));

    await waitFor(() => expect(result.current.fileStatus).toBe("available"));
  });

  it("retry() re-runs the check and can flip the status", async () => {
    vi.mocked(fetch).mockResolvedValue(makeResponse({ ok: false, status: 404 }));
    const { result } = renderHook(() => useFileAvailability("https://files/doc.pdf"));
    await waitFor(() => expect(result.current.fileStatus).toBe("unavailable"));

    vi.mocked(fetch).mockResolvedValue(makeResponse());
    act(() => result.current.retry());

    expect(result.current.fileStatus).toBe("checking");
    await waitFor(() => expect(result.current.fileStatus).toBe("available"));
  });
});
