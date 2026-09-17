import type { ApiFieldError } from "@/lib/api/client";
import {
  mapApiErrorToField,
  readOptionalString,
  readRequiredString,
} from "@/app/actions/form-data";

describe("readOptionalString", () => {
  it("retourne undefined quand le champ est absent", () => {
    const errors: ApiFieldError[] = [];
    expect(readOptionalString(new FormData(), "phone", errors)).toBeUndefined();
    expect(errors).toEqual([]);
  });

  it("retourne undefined quand le champ facultatif est vide (non-régression 422 phone)", () => {
    const formData = new FormData();
    formData.set("phone", "");
    const errors: ApiFieldError[] = [];
    expect(readOptionalString(formData, "phone", errors)).toBeUndefined();
    expect(errors).toEqual([]);
  });

  it("signale un format invalide quand la valeur n'est pas une chaîne", () => {
    const formData = new FormData();
    formData.set("company", new File(["x"], "x.txt"));
    const errors: ApiFieldError[] = [];
    expect(readOptionalString(formData, "company", errors)).toBeUndefined();
    expect(errors).toEqual([{ field: "company", message: "Format de champ invalide." }]);
  });

  it("retourne la valeur renseignée", () => {
    const formData = new FormData();
    formData.set("phone", "+33 6 12 34 56 78");
    const errors: ApiFieldError[] = [];
    expect(readOptionalString(formData, "phone", errors)).toBe("+33 6 12 34 56 78");
    expect(errors).toEqual([]);
  });
});

describe("readRequiredString", () => {
  it("continue de signaler un champ requis vide", () => {
    const formData = new FormData();
    formData.set("email", "");
    const errors: ApiFieldError[] = [];
    expect(readRequiredString(formData, "email", errors)).toBeUndefined();
    expect(errors).toEqual([{ field: "email", message: "Ce champ est requis." }]);
  });
});

describe("mapApiErrorToField", () => {
  it.each([
    ["phone.constrained-str", "phone"],
    ["phone.none", "phone"],
    ["email", "email"],
    ["subject.enum", "subject"],
    ["message", "message"],
  ])("rattache %s au champ %s", (apiField, expected) => {
    expect(mapApiErrorToField(apiField)).toBe(expected);
  });
});
