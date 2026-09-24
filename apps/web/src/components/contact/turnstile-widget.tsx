"use client";

import Script from "next/script";
import { useEffect, useRef, useState } from "react";

type TurnstileWidgetProps = {
  /** Siteverify action checked by the API (ADR-004): "contact_message" | "quote_request". */
  action: string;
  resetSignal: number;
  onVerify: (token: string) => void;
  /** Id of the element describing a Turnstile validation error, when one is displayed. */
  describedBy?: string;
};

type TurnstileRenderOptions = {
  sitekey: string;
  action: string;
  callback: (token: string) => void;
  "expired-callback": () => void;
  "error-callback": () => void;
};

type TurnstileApi = {
  render: (container: HTMLElement, options: TurnstileRenderOptions) => string;
  reset: (widgetId?: string) => void;
  remove: (widgetId: string) => void;
};

declare global {
  interface Window {
    turnstile?: TurnstileApi;
  }
}

export function TurnstileWidget({ action, resetSignal, onVerify, describedBy }: TurnstileWidgetProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const widgetIdRef = useRef<string | undefined>(undefined);
  const [scriptReady, setScriptReady] = useState(false);
  const siteKey = process.env.NEXT_PUBLIC_TURNSTILE_SITE_KEY;

  useEffect(() => {
    if (!siteKey || !scriptReady || !window.turnstile || !containerRef.current) {
      return;
    }

    containerRef.current.replaceChildren();
    widgetIdRef.current = window.turnstile.render(containerRef.current, {
      sitekey: siteKey,
      action,
      callback: onVerify,
      "expired-callback": () => onVerify(""),
      "error-callback": () => onVerify(""),
    });

    return () => {
      if (widgetIdRef.current) {
        // remove (not reset): the widget must be destroyed when its container leaves the DOM.
        window.turnstile?.remove(widgetIdRef.current);
        widgetIdRef.current = undefined;
      }
    };
  }, [action, onVerify, resetSignal, scriptReady, siteKey]);

  if (!siteKey) {
    return (
      <p role="alert" className="text-sm text-[var(--accent)]">
        Turnstile DEV non configuré : le formulaire est désactivé.
      </p>
    );
  }

  // next/script: onReady covers re-mounts after a client-side navigation (script already loaded);
  // onLoad covers a second <Script> with the same src mounted while the first load is in flight,
  // which receives onLoad only. Both are needed for the two widgets of /contact.
  const markScriptReady = () => setScriptReady(true);

  return (
    <div>
      <Script
        src="https://challenges.cloudflare.com/turnstile/v0/api.js"
        strategy="afterInteractive"
        onLoad={markScriptReady}
        onReady={markScriptReady}
      />
      {/* The widget Cloudflare renders in here is a fixed 300px wide. On a 320px screen the
          card only offers 248px, and the page gained a horizontal scrollbar. It is scaled
          down rather than clipped: a captcha with its right edge cut off is one nobody can
          finish. See globals.css — .thl-turnstile. */}
      <div
        ref={containerRef}
        className="thl-turnstile"
        role="group"
        aria-label="Vérification anti-spam"
        aria-describedby={describedBy}
      />
    </div>
  );
}