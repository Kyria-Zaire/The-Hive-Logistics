"use client";

import { useCallback, useEffect, useId, useRef } from "react";
import { X } from "lucide-react";
import { homeContent } from "@/lib/content/home";
import { MainNavLinks } from "@/components/navigation/main-nav-links";

type MobileDrawerProps = {
  open: boolean;
  onClose: () => void;
  menuButtonRef: React.RefObject<HTMLButtonElement | null>;
};

const FOCUSABLE =
  'a[href], button:not([disabled]), textarea, input, select, [tabindex]:not([tabindex="-1"])';

export function MobileDrawer({ open, onClose, menuButtonRef }: MobileDrawerProps) {
  const panelRef = useRef<HTMLDivElement>(null);
  const closeRef = useRef<HTMLButtonElement>(null);
  const titleId = useId();

  useEffect(() => {
    if (!open) {
      return;
    }
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    closeRef.current?.focus();

    return () => {
      document.body.style.overflow = previousOverflow;
    };
  }, [open]);

  useEffect(() => {
    if (!open) {
      return;
    }
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        event.preventDefault();
        onClose();
        return;
      }
      if (event.key !== "Tab" || !panelRef.current) {
        return;
      }
      const focusables = Array.from(
        panelRef.current.querySelectorAll<HTMLElement>(FOCUSABLE),
      ).filter((el) => !el.hasAttribute("disabled") && el.offsetParent !== null);
      if (focusables.length === 0) {
        return;
      }
      const first = focusables[0];
      const last = focusables[focusables.length - 1];
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    };
    document.addEventListener("keydown", onKeyDown);
    return () => document.removeEventListener("keydown", onKeyDown);
  }, [open, onClose]);

  const handleClose = useCallback(() => {
    onClose();
    menuButtonRef.current?.focus();
  }, [onClose, menuButtonRef]);

  if (!open) {
    return null;
  }

  return (
    <div className="fixed inset-0 z-50 xl:hidden" role="presentation">
      <button
        type="button"
        className="absolute inset-0 bg-black/60 thl-focus-dark"
        aria-label={homeContent.nav.menuClose}
        onClick={handleClose}
      />
      <div
        ref={panelRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        className="absolute right-0 top-0 flex h-full w-[min(100%,20rem)] flex-col border-l border-thl-border bg-thl-bg-anthracite p-6 shadow-xl"
      >
        <div className="mb-6 flex items-center justify-between gap-4">
          <p id={titleId} className="text-sm font-medium text-thl-text-secondary">
            {homeContent.nav.primary}
          </p>
          <button
            ref={closeRef}
            type="button"
            className="inline-flex size-11 items-center justify-center thl-focus-dark"
            aria-label={homeContent.nav.menuClose}
            onClick={handleClose}
          >
            <X size={22} aria-hidden="true" />
          </button>
        </div>
        <nav aria-label={homeContent.nav.primary}>
          <MainNavLinks id="mobile-primary-nav" onNavigate={handleClose} />
        </nav>
      </div>
    </div>
  );
}
