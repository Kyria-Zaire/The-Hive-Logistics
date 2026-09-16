"use server";

import {
  submitContactMessage,
  type ApiFieldError,
  type ContactMessagePayload,
  type ContactSubject,
} from "@/lib/api/client";
import {
  honeypotFailure,
  readOptionalString,
  readRequiredString,
} from "./form-data";
import type { ActionResult } from "./types";

export async function submitContactAction(
  formData: FormData,
): Promise<ActionResult> {
  const errors: ApiFieldError[] = [];
  const honeypotError = honeypotFailure(formData, errors);
  if (honeypotError) {
    return honeypotError;
  }

  const firstName = readRequiredString(formData, "first_name", errors);
  const lastName = readRequiredString(formData, "last_name", errors);
  const email = readRequiredString(formData, "email", errors);
  const subject = readRequiredString(formData, "subject", errors);
  const message = readRequiredString(formData, "message", errors);
  const turnstileToken = readRequiredString(formData, "turnstile_token", errors);
  const privacyAcknowledgement = readRequiredString(
    formData,
    "privacy_acknowledgement",
    errors,
  );
  const phone = readOptionalString(formData, "phone", errors);
  const company = readOptionalString(formData, "company", errors);

  if (
    errors.length > 0 ||
    firstName === undefined ||
    lastName === undefined ||
    email === undefined ||
    subject === undefined ||
    message === undefined ||
    turnstileToken === undefined ||
    privacyAcknowledgement === undefined
  ) {
    return {
      ok: false,
      errors,
      message: "Vérifiez les champs requis avant de réessayer.",
    };
  }

  const payload: ContactMessagePayload = {
    turnstile_token: turnstileToken,
    honeypot: "",
    privacy_acknowledgement: true,
    first_name: firstName,
    last_name: lastName,
    email,
    subject: subject as ContactSubject,
    message,
    ...(phone === undefined ? {} : { phone }),
    ...(company === undefined ? {} : { company }),
  };

  return submitContactMessage(payload);
}