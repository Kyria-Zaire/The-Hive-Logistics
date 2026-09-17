import { useEffect, useRef } from "react";
import { act, render, waitFor } from "@testing-library/react";
import { TurnstileWidget } from "@/components/contact/turnstile-widget";

/**
 * Faithful stand-in for next/script (node_modules/next/dist/client/script.js):
 * - first instance for a src loads it, then gets onReady and onLoad;
 * - instances mounted while that src is loading only get onLoad (chained on the load promise);
 * - instances mounted after the src has loaded only get onReady (re-mount after navigation).
 */
const scriptRegistry = vi.hoisted(() => ({
  state: new Map<string, "loading" | "loaded">(),
  pendingOnLoad: new Map<string, Array<() => void>>(),
  finishLoading: (src: string) => {
    scriptRegistry.state.set(src, "loaded");
    for (const onLoad of scriptRegistry.pendingOnLoad.get(src) ?? []) onLoad();
    scriptRegistry.pendingOnLoad.delete(src);
  },
}));

vi.mock("next/script", () => ({
  default: function ScriptStub({
    src,
    onLoad,
    onReady,
  }: {
    src: string;
    onLoad?: () => void;
    onReady?: () => void;
  }) {
    const handlers = useRef({ onLoad, onReady });
    handlers.current = { onLoad, onReady };

    useEffect(() => {
      const state = scriptRegistry.state.get(src);
      if (state === "loaded") {
        handlers.current.onReady?.();
        return;
      }
      const queue = scriptRegistry.pendingOnLoad.get(src) ?? [];
      if (state === "loading") {
        queue.push(() => handlers.current.onLoad?.());
      } else {
        scriptRegistry.state.set(src, "loading");
        queue.push(() => {
          handlers.current.onReady?.();
          handlers.current.onLoad?.();
        });
      }
      scriptRegistry.pendingOnLoad.set(src, queue);
    }, [src]);

    return null;
  },
}));

const TURNSTILE_SRC = "https://challenges.cloudflare.com/turnstile/v0/api.js";

describe("TurnstileWidget", () => {
  let widgetCounter = 0;

  beforeEach(() => {
    scriptRegistry.state.clear();
    scriptRegistry.pendingOnLoad.clear();
    widgetCounter = 0;
    vi.stubEnv("NEXT_PUBLIC_TURNSTILE_SITE_KEY", "1x00000000000000000000AA");
    window.turnstile = {
      render: vi.fn(() => {
        widgetCounter += 1;
        return `widget-${widgetCounter}`;
      }),
      reset: vi.fn(),
      remove: vi.fn(),
    };
  });

  afterEach(() => {
    vi.unstubAllEnvs();
    delete window.turnstile;
  });

  it.each(["contact_message", "quote_request"])(
    "transmet l'action %s à turnstile.render (non-régression 403 ADR-004)",
    async (action) => {
      render(<TurnstileWidget action={action} resetSignal={0} onVerify={() => undefined} />);
      act(() => scriptRegistry.finishLoading(TURNSTILE_SRC));

      await waitFor(() => {
        expect(window.turnstile?.render).toHaveBeenCalledWith(
          expect.any(HTMLElement),
          expect.objectContaining({ action, sitekey: "1x00000000000000000000AA" }),
        );
      });
    },
  );

  it("rend les deux widgets d'une même page au premier chargement du script", async () => {
    render(
      <>
        <TurnstileWidget action="contact_message" resetSignal={0} onVerify={() => undefined} />
        <TurnstileWidget action="quote_request" resetSignal={0} onVerify={() => undefined} />
      </>,
    );
    act(() => scriptRegistry.finishLoading(TURNSTILE_SRC));

    await waitFor(() => expect(window.turnstile?.render).toHaveBeenCalledTimes(2));
  });

  it("rend à nouveau le widget après démontage puis remontage (navigation client) et le supprime au démontage", async () => {
    const first = render(
      <TurnstileWidget action="contact_message" resetSignal={0} onVerify={() => undefined} />,
    );
    act(() => scriptRegistry.finishLoading(TURNSTILE_SRC));
    await waitFor(() => expect(window.turnstile?.render).toHaveBeenCalledTimes(1));

    first.unmount();
    expect(window.turnstile?.remove).toHaveBeenCalledWith("widget-1");
    expect(window.turnstile?.reset).not.toHaveBeenCalled();

    render(<TurnstileWidget action="contact_message" resetSignal={0} onVerify={() => undefined} />);
    await waitFor(() => expect(window.turnstile?.render).toHaveBeenCalledTimes(2));
  });
});
