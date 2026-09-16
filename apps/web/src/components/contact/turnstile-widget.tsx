"use client";

import Script from "next/script";
import { useEffect, useRef, useState } from "react";

type TurnstileWidgetProps = {
  resetSignal: number;
  onVerify: (token: string) => void;
};

type TurnstileRenderOptions = {
  sitekey: string;
  callback: (token: string) => void;
  "expired-callback": () => void;
  "error-callback": () => void;
};

type TurnstileApi = {
  render: (container: HTMLElement, options: TurnstileRenderOptions) => string;
  reset: (widgetId?: string) => void;
};

declare global {
  interface Window {
    turnstile?: TurnstileApi;
  }
}

export function TurnstileWidget({ resetSignal, onVerify }: TurnstileWidgetProps) {
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
      callback: onVerify,
      "expired-callback": () => onVerify(""),
      "error-callback": () => onVerify(""),
    });

    return () => {
      if (widgetIdRef.current) {
        window.turnstile?.reset(widgetIdRef.current);
        widgetIdRef.current = undefined;
      }
    };
  }, [onVerify, resetSignal, scriptReady, siteKey]);

  if (!siteKey) {
    return (
      <p role="alert" className="text-sm text-[var(--accent)]">
        Turnstile DEV non configuré : le formulaire est désactivé.
      </p>
    );
  }

  return (
    <div>
      <Script
        src="https://challenges.cloudflare.com/turnstile/v0/api.js"
        strategy="afterInteractive"
        onLoad={() => setScriptReady(true)}
      />
      <div ref={containerRef} aria-label="Vérification anti-spam" />
    </div>
  );
}