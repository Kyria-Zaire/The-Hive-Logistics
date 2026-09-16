export type ServiceType =
  | "convoyage_premium"
  | "fleet_coordination"
  | "automotive_logistics"
  | "vehicle_preparation";

export type VehicleCategory =
  | "city_sedan"
  | "suv_4x4"
  | "premium_sport"
  | "light_commercial"
  | "classic_collector"
  | "other";

export type ContactSubject = "information" | "quote" | "partnership" | "other";

export type ContactPreference = "email" | "phone" | "no_preference";

export type PreferredTiming =
  | { kind: "exact_date"; exact_date: string }
  | { kind: "period"; period_text: string };

export type ContactMessagePayload = {
  turnstile_token: string;
  honeypot: string;
  privacy_acknowledgement: true;
  first_name: string;
  last_name: string;
  email: string;
  subject: ContactSubject;
  message: string;
  phone?: string;
  company?: string;
};

export type QuoteRequestPayload = {
  turnstile_token: string;
  honeypot: string;
  privacy_acknowledgement: true;
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
  service: ServiceType;
  departure_city: string;
  departure_postal_code: string;
  arrival_city: string;
  arrival_postal_code: string;
  preferred_timing: PreferredTiming;
  vehicle_category: VehicleCategory;
  vehicle_make: string;
  vehicle_model: string;
  vehicle_rolling: boolean;
  vehicle_category_other_detail?: string;
  company?: string;
  special_constraints?: string;
  additional_message?: string;
  contact_preference?: ContactPreference;
};

export type LeadSubmissionAccepted = {
  public_reference: string;
  status: "received";
  created_at: string;
};

export type ApiFieldError = {
  field: string;
  message: string;
};

export type Result<T> =
  | { ok: true; data: T }
  | { ok: false; errors: ApiFieldError[]; message: string };

type ProblemDetails = {
  title?: string;
  detail?: string;
  errors?: ApiFieldError[];
};

const REQUEST_TIMEOUT_MS = 10_000;

function apiUrl(path: string): string {
  const baseUrl = process.env.NEXT_PUBLIC_API_URL;
  if (!baseUrl) {
    throw new Error("NEXT_PUBLIC_API_URL is not configured");
  }
  return `${baseUrl.replace(/\/$/, "")}${path}`;
}

function isProblemDetails(value: unknown): value is ProblemDetails {
  return typeof value === "object" && value !== null;
}

async function readJson(response: Response): Promise<unknown> {
  try {
    return await response.json();
  } catch {
    return undefined;
  }
}

async function postLead<T>(path: string, payload: object): Promise<Result<T>> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);

  try {
    const response = await fetch(apiUrl(path), {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Idempotency-Key": crypto.randomUUID(),
      },
      body: JSON.stringify(payload),
      signal: controller.signal,
    });
    const body = await readJson(response);

    if (response.ok) {
      return { ok: true, data: body as T };
    }

    const problem = isProblemDetails(body) ? body : {};
    const message =
      typeof problem.detail === "string"
        ? problem.detail
        : typeof problem.title === "string"
          ? problem.title
          : response.status >= 500
            ? "Le service est temporairement indisponible."
            : "La demande n'a pas pu être envoyée.";

    return {
      ok: false,
      errors: Array.isArray(problem.errors) ? problem.errors : [],
      message,
    };
  } catch (error: unknown) {
    const message =
      error instanceof DOMException && error.name === "AbortError"
        ? "La demande a expiré. Réessayez dans quelques instants."
        : "Le service est momentanément inaccessible. Réessayez dans quelques instants.";
    return { ok: false, errors: [], message };
  } finally {
    clearTimeout(timeout);
  }
}

export function submitContactMessage(
  payload: ContactMessagePayload,
): Promise<Result<LeadSubmissionAccepted>> {
  return postLead<LeadSubmissionAccepted>("/api/v1/contact-messages", payload);
}

export function submitQuoteRequest(
  payload: QuoteRequestPayload,
): Promise<Result<LeadSubmissionAccepted>> {
  return postLead<LeadSubmissionAccepted>("/api/v1/quote-requests", payload);
}