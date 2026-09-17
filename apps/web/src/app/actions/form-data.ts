import type { ApiFieldError } from "@/lib/api/client";

export type FormActionFailure = {
  ok: false;
  errors: ApiFieldError[];
  message: string;
};

export function readRequiredString(
  formData: FormData,
  field: string,
  errors: ApiFieldError[],
): string | undefined {
  const value = formData.get(field);
  if (typeof value !== "string" || value.length === 0) {
    errors.push({ field, message: "Ce champ est requis." });
    return undefined;
  }
  return value;
}

export function readOptionalString(
  formData: FormData,
  field: string,
  errors: ApiFieldError[],
): string | undefined {
  const value = formData.get(field);
  if (value === null) {
    return undefined;
  }
  if (typeof value !== "string") {
    errors.push({ field, message: "Format de champ invalide." });
    return undefined;
  }
  // An untouched optional input is submitted as "": omit it instead of sending an empty value the API rejects.
  if (value === "") {
    return undefined;
  }
  return value;
}

/**
 * API validation errors can carry a schema suffix (e.g. "phone.constrained-str").
 * Returns the root field name so the error attaches to the matching form control.
 */
export function mapApiErrorToField(field: string): string {
  const separatorIndex = field.indexOf(".");
  return separatorIndex === -1 ? field : field.slice(0, separatorIndex);
}

export function readBoolean(
  formData: FormData,
  field: string,
  errors: ApiFieldError[],
): boolean | undefined {
  const value = readRequiredString(formData, field, errors);
  if (value === undefined) {
    return undefined;
  }
  if (value === "true" || value === "on" || value === "1") {
    return true;
  }
  if (value === "false" || value === "0") {
    return false;
  }
  errors.push({ field, message: "Ce champ doit être booléen." });
  return undefined;
}

export function honeypotFailure(
  formData: FormData,
  errors: ApiFieldError[],
): FormActionFailure | undefined {
  const value = formData.get("honeypot");
  if (typeof value !== "string") {
    errors.push({ field: "honeypot", message: "Ce champ est requis." });
  } else if (value.length > 0) {
    errors.push({ field: "honeypot", message: "Requête refusée." });
  }
  return errors.length > 0
    ? { ok: false, errors, message: "La demande n'a pas pu être préparée." }
    : undefined;
}