"use server";

import {
  submitQuoteRequest,
  type ApiFieldError,
  type ContactPreference,
  type QuoteRequestPayload,
  type ServiceType,
  type VehicleCategory,
} from "@/lib/api/client";
import {
  honeypotFailure,
  readBoolean,
  readOptionalString,
  readRequiredString,
} from "./form-data";
import type { ActionResult } from "./types";

export async function submitQuoteAction(
  formData: FormData,
): Promise<ActionResult> {
  const errors: ApiFieldError[] = [];
  const honeypotError = honeypotFailure(formData, errors);
  if (honeypotError) {
    return honeypotError;
  }

  const turnstileToken = readRequiredString(formData, "turnstile_token", errors);
  const privacyAcknowledgement = readRequiredString(
    formData,
    "privacy_acknowledgement",
    errors,
  );
  const firstName = readRequiredString(formData, "first_name", errors);
  const lastName = readRequiredString(formData, "last_name", errors);
  const email = readRequiredString(formData, "email", errors);
  const phone = readRequiredString(formData, "phone", errors);
  const service = readRequiredString(formData, "service", errors);
  const departureCity = readRequiredString(formData, "departure_city", errors);
  const departurePostalCode = readRequiredString(
    formData,
    "departure_postal_code",
    errors,
  );
  const arrivalCity = readRequiredString(formData, "arrival_city", errors);
  const arrivalPostalCode = readRequiredString(
    formData,
    "arrival_postal_code",
    errors,
  );
  const timingKind = readRequiredString(formData, "preferred_timing_kind", errors);
  const vehicleCategory = readRequiredString(formData, "vehicle_category", errors);
  const vehicleMake = readRequiredString(formData, "vehicle_make", errors);
  const vehicleModel = readRequiredString(formData, "vehicle_model", errors);
  const vehicleRolling = readBoolean(formData, "vehicle_rolling", errors);
  const company = readOptionalString(formData, "company", errors);
  const specialConstraints = readOptionalString(
    formData,
    "special_constraints",
    errors,
  );
  const additionalMessage = readOptionalString(
    formData,
    "additional_message",
    errors,
  );
  const contactPreference = readOptionalString(
    formData,
    "contact_preference",
    errors,
  );

  const timingValue =
    timingKind === "exact_date"
      ? readRequiredString(formData, "preferred_timing_exact_date", errors)
      : timingKind === "period"
        ? readRequiredString(formData, "preferred_timing_period_text", errors)
        : undefined;
  if (timingKind !== "exact_date" && timingKind !== "period") {
    errors.push({
      field: "preferred_timing_kind",
      message: "Type de période invalide.",
    });
  }

  const otherDetail = readOptionalString(
    formData,
    "vehicle_category_other_detail",
    errors,
  );

  if (
    errors.length > 0 ||
    turnstileToken === undefined ||
    privacyAcknowledgement === undefined ||
    firstName === undefined ||
    lastName === undefined ||
    email === undefined ||
    phone === undefined ||
    service === undefined ||
    departureCity === undefined ||
    departurePostalCode === undefined ||
    arrivalCity === undefined ||
    arrivalPostalCode === undefined ||
    timingKind === undefined ||
    timingValue === undefined ||
    vehicleCategory === undefined ||
    vehicleMake === undefined ||
    vehicleModel === undefined ||
    vehicleRolling === undefined
  ) {
    return {
      ok: false,
      errors,
      message: "Vérifiez les champs requis avant de réessayer.",
    };
  }

  const preferredTiming =
    timingKind === "exact_date"
      ? { kind: "exact_date" as const, exact_date: timingValue }
      : { kind: "period" as const, period_text: timingValue };
  const payload: QuoteRequestPayload = {
    turnstile_token: turnstileToken,
    honeypot: "",
    privacy_acknowledgement: true,
    first_name: firstName,
    last_name: lastName,
    email,
    phone,
    service: service as ServiceType,
    departure_city: departureCity,
    departure_postal_code: departurePostalCode,
    arrival_city: arrivalCity,
    arrival_postal_code: arrivalPostalCode,
    preferred_timing: preferredTiming,
    vehicle_category: vehicleCategory as VehicleCategory,
    vehicle_make: vehicleMake,
    vehicle_model: vehicleModel,
    vehicle_rolling: vehicleRolling,
    ...(otherDetail === undefined ? {} : { vehicle_category_other_detail: otherDetail }),
    ...(company === undefined ? {} : { company }),
    ...(specialConstraints === undefined ? {} : { special_constraints: specialConstraints }),
    ...(additionalMessage === undefined ? {} : { additional_message: additionalMessage }),
    ...(contactPreference === undefined
      ? {}
      : { contact_preference: contactPreference as ContactPreference }),
  };

  return submitQuoteRequest(payload);
}