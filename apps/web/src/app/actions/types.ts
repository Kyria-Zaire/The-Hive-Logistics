import type { ApiFieldError, LeadSubmissionAccepted } from "@/lib/api/client";

export type ActionResult =
  | { ok: true; data: LeadSubmissionAccepted }
  | { ok: false; errors: ApiFieldError[]; message: string };