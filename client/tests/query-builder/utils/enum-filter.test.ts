import { describe, expect, it } from "vitest";
import { getFilterOpsForField, isEnumField } from "@/query-builder/utils/enum-filter";
import type { FieldInfo } from "@/query-builder/types/query-builder-types";

const enumField: FieldInfo = { name: "tipo_deudor", type: "USER-DEFINED", enumValues: ["TITULAR", "CO_DEUDOR"] };
const textField: FieldInfo = { name: "nombre_completo", type: "text", enumValues: null };

describe("enum-filter", () => {
  describe("isEnumField", () => {
    it("is true only for a field with enum values", () => {
      expect(isEnumField(enumField)).toBe(true);
      expect(isEnumField(textField)).toBe(false);
      expect(isEnumField(undefined)).toBe(false);
    });

    it("is false for a user-defined type that has no enum labels", () => {
      expect(isEnumField({ name: "geom", type: "USER-DEFINED", enumValues: [] })).toBe(false);
    });
  });

  describe("getFilterOpsForField", () => {
    it("drops like/ilike for an enum column, since Postgres rejects them", () => {
      const ops = getFilterOpsForField(enumField).map((o) => o.value);
      expect(ops).not.toContain("like");
      expect(ops).not.toContain("ilike");
      expect(ops).toEqual(expect.arrayContaining(["=", "!=", "in", "not_in", "is_null", "is_not_null"]));
    });

    it("keeps every operator for a non-enum column", () => {
      const ops = getFilterOpsForField(textField).map((o) => o.value);
      expect(ops).toContain("like");
      expect(ops).toContain("ilike");
    });

    it("keeps every operator while the field is not yet resolved", () => {
      expect(getFilterOpsForField(undefined).map((o) => o.value)).toContain("like");
    });
  });
});
