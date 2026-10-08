import { beforeEach, describe, expect, it } from "vitest";
import { getSession, setSessionUser } from "@/auth/utils/auth-session-utils";

describe("auth-session-utils", () => {
  beforeEach(() => {
    sessionStorage.clear();
  });

  it("strips PII fields before persisting to sessionStorage", () => {
    setSessionUser({
      userId: "u1",
      fullName: "Ana Test",
      email: "ana@example.com",
      documentType: "CC",
      documentNumber: "123456789",
      phoneNumber: "+573001234567",
      nationality: "CO",
    });

    const raw = JSON.parse(sessionStorage.getItem("user")!);
    expect(raw.documentType).toBeUndefined();
    expect(raw.documentNumber).toBeUndefined();
    expect(raw.phoneNumber).toBeUndefined();
    expect(raw.nationality).toBeUndefined();
    // Lo no sensible sí debe persistir: es lo que hidrata la UI antes de que
    // SessionProvider vuelva a pedir /users/me.
    expect(raw.userId).toBe("u1");
    expect(raw.fullName).toBe("Ana Test");
    expect(raw.email).toBe("ana@example.com");
  });

  it("round-trips through getSession without the stripped fields", () => {
    setSessionUser({ email: "x@example.com", documentNumber: "999999999" });
    const session = getSession();
    expect(session?.email).toBe("x@example.com");
    expect(session?.documentNumber).toBeUndefined();
  });

  it("getSession returns null when nothing is stored", () => {
    expect(getSession()).toBeNull();
  });

  it("getSession returns null on malformed JSON instead of throwing", () => {
    sessionStorage.setItem("user", "{not json");
    expect(getSession()).toBeNull();
  });
});
