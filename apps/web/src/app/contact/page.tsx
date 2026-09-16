"use client";

import {
  type FormEvent,
  useCallback,
  useEffect,
  useRef,
  useState,
} from "react";
import { submitContactAction } from "@/app/actions/contact";
import { submitQuoteAction } from "@/app/actions/quote";
import type { ActionResult } from "@/app/actions/types";
import { SiteFooter } from "@/components/layout/site-footer";
import { SiteHeader } from "@/components/layout/site-header";
import type { ApiFieldError } from "@/lib/api/client";
import { SHOW_FOOTER_CONTACT_DETAILS, SHOW_FOOTER_SOCIAL_LINKS } from "@/lib/features";
import { TurnstileWidget } from "@/components/contact/turnstile-widget";

type FormStatus = "idle" | "loading" | "success" | "error";

type FormState = {
  status: FormStatus;
  result: ActionResult | null;
};

const initialFormState: FormState = { status: "idle", result: null };

function FieldError({ id, errors }: { id: string; errors: ApiFieldError[] }) {
  const error = errors.find((item) => item.field === id);
  return error ? (
    <p id={`${id}-error`} role="alert" className="mt-2 text-sm text-[var(--accent)]">
      {error.message}
    </p>
  ) : null;
}

function FormMessage({ state }: { state: FormState }) {
  if (!state.result || state.result.ok) {
    return null;
  }
  return (
    <p role="alert" className="text-sm text-[var(--accent)]">
      {state.result.message}
    </p>
  );
}

function TextInput({
  id,
  label,
  type = "text",
  required = false,
  errors,
}: {
  id: string;
  label: string;
  type?: "email" | "text" | "tel";
  required?: boolean;
  errors: ApiFieldError[];
}) {
  const hasError = errors.some((item) => item.field === id);
  return (
    <div>
      <label htmlFor={id} className="text-sm font-medium text-[var(--text-primary)]">
        {label}
        {required ? " *" : ""}
      </label>
      <input
        id={id}
        name={id}
        type={type}
        required={required}
        aria-invalid={hasError}
        aria-describedby={hasError ? `${id}-error` : undefined}
        className="mt-2 min-h-11 w-full border border-[var(--border)] bg-[var(--bg-elevated)] px-4 text-[var(--text-primary)] outline-none transition-colors focus:border-[var(--accent)]"
      />
      <FieldError id={id} errors={errors} />
    </div>
  );
}

function Honeypot() {
  return (
    <div className="sr-only" aria-hidden="true">
      <label htmlFor="contact-honeypot">Ne pas remplir</label>
      <input id="contact-honeypot" name="honeypot" tabIndex={-1} autoComplete="off" />
    </div>
  );
}

function ContactForm() {
  const [state, setState] = useState<FormState>(initialFormState);
  const [turnstileToken, setTurnstileToken] = useState("");
  const [resetSignal, setResetSignal] = useState(0);
  const formRef = useRef<HTMLFormElement>(null);
  const errors = state.result && !state.result.ok ? state.result.errors : [];

  const verifyToken = useCallback((token: string) => setTurnstileToken(token), []);

  useEffect(() => {
    formRef.current?.querySelector<HTMLElement>('[aria-invalid="true"]')?.focus();
  }, [state.result]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;
    if (!form.checkValidity() || !turnstileToken) {
      setState({
        status: "error",
        result: {
          ok: false,
          errors: turnstileToken ? [] : [{ field: "turnstile_token", message: "Validation anti-spam requise." }],
          message: "Vérifiez les champs requis avant de réessayer.",
        },
      });
      return;
    }
    setState({ status: "loading", result: null });
    const data = new FormData(form);
    data.set("turnstile_token", turnstileToken);
    const result = await submitContactAction(data);
    setState({ status: result.ok ? "success" : "error", result });
    if (result.ok) {
      form.reset();
      setTurnstileToken("");
      setResetSignal((value) => value + 1);
    }
  }

  return (
    <form
      ref={formRef}
      id="contact"
      noValidate
      onSubmit={handleSubmit}
      aria-busy={state.status === "loading"}
      className="space-y-5 border border-[var(--border)] bg-[var(--bg-secondary)] p-6 md:p-8"
    >
      <div>
        <p className="text-caption text-[var(--text-muted)]">CONTACT</p>
        <h2 className="text-heading mt-3 text-[var(--text-primary)]">Échangeons sur votre besoin</h2>
      </div>
      <div className="grid gap-5 md:grid-cols-2">
        <TextInput id="first_name" label="Prénom" required errors={errors} />
        <TextInput id="last_name" label="Nom" required errors={errors} />
      </div>
      <TextInput id="email" label="Email" type="email" required errors={errors} />
      <TextInput id="phone" label="Téléphone" type="tel" errors={errors} />
      <div>
        <label htmlFor="company" className="text-sm font-medium text-[var(--text-primary)]">Entreprise</label>
        <input id="company" name="company" className="mt-2 min-h-11 w-full border border-[var(--border)] bg-[var(--bg-elevated)] px-4 text-[var(--text-primary)] outline-none focus:border-[var(--accent)]" />
        <FieldError id="company" errors={errors} />
      </div>
      <div>
        <label htmlFor="subject" className="text-sm font-medium text-[var(--text-primary)]">Sujet *</label>
        <select id="subject" name="subject" required className="mt-2 min-h-11 w-full border border-[var(--border)] bg-[var(--bg-elevated)] px-4 text-[var(--text-primary)] outline-none focus:border-[var(--accent)]">
          <option value="">Sélectionner</option>
          <option value="information">Information</option>
          <option value="quote">Devis</option>
          <option value="partnership">Partenariat</option>
          <option value="other">Autre</option>
        </select>
        <FieldError id="subject" errors={errors} />
      </div>
      <div>
        <label htmlFor="message" className="text-sm font-medium text-[var(--text-primary)]">Message *</label>
        <textarea id="message" name="message" required minLength={10} rows={6} className="mt-2 w-full border border-[var(--border)] bg-[var(--bg-elevated)] px-4 py-3 text-[var(--text-primary)] outline-none focus:border-[var(--accent)]" />
        <FieldError id="message" errors={errors} />
      </div>
      <Honeypot />
      <TurnstileWidget resetSignal={resetSignal} onVerify={verifyToken} />
      <label className="flex items-start gap-3 text-sm text-[var(--text-secondary)]">
        <input type="checkbox" name="privacy_acknowledgement" value="true" required className="mt-1 accent-[var(--accent)]" />
        <span>Je prends connaissance de la politique de confidentialité. *</span>
      </label>
      <FormMessage state={state} />
      {state.status === "success" ? <p role="status" className="text-sm text-[var(--text-primary)]">Votre message a bien été transmis.</p> : null}
      <button type="submit" disabled={state.status === "loading" || !process.env.NEXT_PUBLIC_TURNSTILE_SITE_KEY} className="thl-btn-primary thl-focus-primary w-full sm:w-auto">
        {state.status === "loading" ? "Envoi…" : "Envoyer le message"}
      </button>
    </form>
  );
}

function QuoteForm() {
  const [state, setState] = useState<FormState>(initialFormState);
  const [turnstileToken, setTurnstileToken] = useState("");
  const [resetSignal, setResetSignal] = useState(0);
  const [timingKind, setTimingKind] = useState("period");
  const [vehicleCategory, setVehicleCategory] = useState("");
  const formRef = useRef<HTMLFormElement>(null);
  const errors = state.result && !state.result.ok ? state.result.errors : [];
  const verifyToken = useCallback((token: string) => setTurnstileToken(token), []);

  useEffect(() => {
    formRef.current?.querySelector<HTMLElement>('[aria-invalid="true"]')?.focus();
  }, [state.result]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;
    if (!form.checkValidity() || !turnstileToken) {
      setState({
        status: "error",
        result: {
          ok: false,
          errors: turnstileToken ? [] : [{ field: "turnstile_token", message: "Validation anti-spam requise." }],
          message: "Vérifiez les champs requis avant de réessayer.",
        },
      });
      return;
    }
    setState({ status: "loading", result: null });
    const data = new FormData(form);
    data.set("turnstile_token", turnstileToken);
    const result = await submitQuoteAction(data);
    setState({ status: result.ok ? "success" : "error", result });
    if (result.ok) {
      form.reset();
      setTurnstileToken("");
      setResetSignal((value) => value + 1);
      setTimingKind("period");
      setVehicleCategory("");
    }
  }

  return (
    <form ref={formRef} id="devis" noValidate onSubmit={handleSubmit} aria-busy={state.status === "loading"} className="space-y-5 border border-[var(--border)] bg-[var(--bg-secondary)] p-6 md:p-8">
      <div>
        <p className="text-caption text-[var(--text-muted)]">DEVIS</p>
        <h2 className="text-heading mt-3 text-[var(--text-primary)]">Préparer votre demande</h2>
      </div>
      <div className="grid gap-5 md:grid-cols-2">
        <TextInput id="first_name" label="Prénom" required errors={errors} />
        <TextInput id="last_name" label="Nom" required errors={errors} />
      </div>
      <TextInput id="email" label="Email" type="email" required errors={errors} />
      <TextInput id="phone" label="Téléphone" type="tel" required errors={errors} />
      <div>
        <label htmlFor="service" className="text-sm font-medium text-[var(--text-primary)]">Service *</label>
        <select id="service" name="service" required className="mt-2 min-h-11 w-full border border-[var(--border)] bg-[var(--bg-elevated)] px-4 text-[var(--text-primary)] outline-none focus:border-[var(--accent)]">
          <option value="">Sélectionner</option>
          <option value="convoyage_premium">Convoyage premium</option>
          <option value="fleet_coordination">Coordination de flotte</option>
          <option value="automotive_logistics">Logistique automobile</option>
          <option value="vehicle_preparation">Préparation automobile</option>
        </select>
        <FieldError id="service" errors={errors} />
      </div>
      <div className="grid gap-5 md:grid-cols-2">
        <TextInput id="departure_city" label="Ville de départ" required errors={errors} />
        <TextInput id="departure_postal_code" label="Code postal de départ" required errors={errors} />
        <TextInput id="arrival_city" label="Ville d'arrivée" required errors={errors} />
        <TextInput id="arrival_postal_code" label="Code postal d'arrivée" required errors={errors} />
      </div>
      <div>
        <label htmlFor="preferred_timing_kind" className="text-sm font-medium text-[var(--text-primary)]">Période souhaitée *</label>
        <select id="preferred_timing_kind" name="preferred_timing_kind" value={timingKind} onChange={(event) => setTimingKind(event.target.value)} required className="mt-2 min-h-11 w-full border border-[var(--border)] bg-[var(--bg-elevated)] px-4 text-[var(--text-primary)] outline-none focus:border-[var(--accent)]">
          <option value="period">Période</option>
          <option value="exact_date">Date exacte</option>
        </select>
        {timingKind === "exact_date" ? <input name="preferred_timing_exact_date" type="date" required className="mt-3 min-h-11 w-full border border-[var(--border)] bg-[var(--bg-elevated)] px-4 text-[var(--text-primary)] outline-none focus:border-[var(--accent)]" /> : <input name="preferred_timing_period_text" required minLength={3} placeholder="Ex. semaine du 15 octobre" className="mt-3 min-h-11 w-full border border-[var(--border)] bg-[var(--bg-elevated)] px-4 text-[var(--text-primary)] outline-none focus:border-[var(--accent)]" />}
      </div>
      <div>
        <label htmlFor="vehicle_category" className="text-sm font-medium text-[var(--text-primary)]">Catégorie du véhicule *</label>
        <select id="vehicle_category" name="vehicle_category" value={vehicleCategory} onChange={(event) => setVehicleCategory(event.target.value)} required className="mt-2 min-h-11 w-full border border-[var(--border)] bg-[var(--bg-elevated)] px-4 text-[var(--text-primary)] outline-none focus:border-[var(--accent)]">
          <option value="">Sélectionner</option>
          <option value="city_sedan">Berline citadine</option>
          <option value="suv_4x4">SUV / 4x4</option>
          <option value="premium_sport">Premium / sportive</option>
          <option value="light_commercial">Utilitaire léger</option>
          <option value="classic_collector">Classique / collection</option>
          <option value="other">Autre</option>
        </select>
        {vehicleCategory === "other" ? <input name="vehicle_category_other_detail" required minLength={2} placeholder="Préciser la catégorie" className="mt-3 min-h-11 w-full border border-[var(--border)] bg-[var(--bg-elevated)] px-4 text-[var(--text-primary)] outline-none focus:border-[var(--accent)]" /> : null}
      </div>
      <div className="grid gap-5 md:grid-cols-2">
        <TextInput id="vehicle_make" label="Marque" required errors={errors} />
        <TextInput id="vehicle_model" label="Modèle" required errors={errors} />
      </div>
      <div>
        <label htmlFor="vehicle_rolling" className="text-sm font-medium text-[var(--text-primary)]">Véhicule roulant *</label>
        <select id="vehicle_rolling" name="vehicle_rolling" required className="mt-2 min-h-11 w-full border border-[var(--border)] bg-[var(--bg-elevated)] px-4 text-[var(--text-primary)] outline-none focus:border-[var(--accent)]">
          <option value="">Sélectionner</option>
          <option value="true">Oui</option>
          <option value="false">Non</option>
        </select>
      </div>
      <TextInput id="company" label="Entreprise" errors={errors} />
      <div>
        <label htmlFor="special_constraints" className="text-sm font-medium text-[var(--text-primary)]">Contraintes particulières</label>
        <textarea id="special_constraints" name="special_constraints" rows={3} className="mt-2 w-full border border-[var(--border)] bg-[var(--bg-elevated)] px-4 py-3 text-[var(--text-primary)] outline-none focus:border-[var(--accent)]" />
      </div>
      <div>
        <label htmlFor="additional_message" className="text-sm font-medium text-[var(--text-primary)]">Message complémentaire</label>
        <textarea id="additional_message" name="additional_message" rows={4} className="mt-2 w-full border border-[var(--border)] bg-[var(--bg-elevated)] px-4 py-3 text-[var(--text-primary)] outline-none focus:border-[var(--accent)]" />
      </div>
      <div>
        <label htmlFor="contact_preference" className="text-sm font-medium text-[var(--text-primary)]">Préférence de contact</label>
        <select id="contact_preference" name="contact_preference" className="mt-2 min-h-11 w-full border border-[var(--border)] bg-[var(--bg-elevated)] px-4 text-[var(--text-primary)] outline-none focus:border-[var(--accent)]">
          <option value="">Sélectionner</option>
          <option value="email">Email</option>
          <option value="phone">Téléphone</option>
          <option value="no_preference">Pas de préférence</option>
        </select>
      </div>
      <div className="sr-only" aria-hidden="true"><label htmlFor="quote-honeypot">Ne pas remplir</label><input id="quote-honeypot" name="honeypot" tabIndex={-1} autoComplete="off" /></div>
      <TurnstileWidget resetSignal={resetSignal} onVerify={verifyToken} />
      <label className="flex items-start gap-3 text-sm text-[var(--text-secondary)]"><input type="checkbox" name="privacy_acknowledgement" value="true" required className="mt-1 accent-[var(--accent)]" /><span>Je prends connaissance de la politique de confidentialité. *</span></label>
      <FormMessage state={state} />
      {state.status === "success" ? <p role="status" className="text-sm text-[var(--text-primary)]">Votre demande a bien été transmise.</p> : null}
      <button type="submit" disabled={state.status === "loading" || !process.env.NEXT_PUBLIC_TURNSTILE_SITE_KEY} className="thl-btn-primary thl-focus-primary w-full sm:w-auto">{state.status === "loading" ? "Envoi…" : "Envoyer la demande"}</button>
    </form>
  );
}

export default function ContactPage() {
  return (
    <>
      <SiteHeader />
      <main id="contenu-principal" className="min-h-screen bg-[var(--bg-primary)] py-32 text-[var(--text-primary)]">
        <div className="thl-container">
          <header className="max-w-3xl">
            <p className="text-caption text-[var(--text-muted)]">THE HIVE LOGISTICS</p>
            <h1 className="text-display-m mt-4">Contact</h1>
            <p className="text-body-l mt-5 text-[var(--text-secondary)]">Un projet de convoyage ? Parlons-en.</p>
          </header>
          <div className="mt-16 grid gap-8 xl:grid-cols-2">
            <ContactForm />
            <QuoteForm />
          </div>
          <aside className="mt-8 grid gap-6 md:grid-cols-2">
            {!SHOW_FOOTER_CONTACT_DETAILS ? null : <div className="border-l-2 border-[var(--accent)] pl-4"><h2 className="text-heading">Coordonnées</h2><p className="text-body mt-3 text-[var(--text-secondary)]">Coordonnées disponibles prochainement.</p></div>}
            {!SHOW_FOOTER_SOCIAL_LINKS ? null : <div className="border-l-2 border-[var(--accent)] pl-4"><h2 className="text-heading">Réseaux sociaux</h2><p className="text-body mt-3 text-[var(--text-secondary)]">Réseaux sociaux disponibles prochainement.</p></div>}
          </aside>
        </div>
      </main>
      <SiteFooter />
    </>
  );
}