import { useRef, useState } from "react";
import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MobileDrawer } from "@/components/navigation/mobile-drawer";
import { homeContent } from "@/lib/content/home";

function DrawerHarness() {
  const [open, setOpen] = useState(false);
  const menuButtonRef = useRef<HTMLButtonElement>(null);

  return (
    <>
      <button
        ref={menuButtonRef}
        type="button"
        aria-expanded={open}
        aria-controls="mobile-primary-nav"
        aria-label={homeContent.nav.menuOpen}
        onClick={() => setOpen(true)}
      >
        {homeContent.nav.menuOpen}
      </button>
      <MobileDrawer
        open={open}
        onClose={() => setOpen(false)}
        menuButtonRef={menuButtonRef}
      />
    </>
  );
}

describe("MobileDrawer", () => {
  it("ouvre le menu, piège le focus, restitue le focus et le scroll au Escape", async () => {
    const user = userEvent.setup();
    render(<DrawerHarness />);

    const menuButton = screen.getByRole("button", { name: homeContent.nav.menuOpen });
    const initialOverflow = document.body.style.overflow;

    await user.click(menuButton);

    const dialog = screen.getByRole("dialog");
    expect(dialog).toBeInTheDocument();
    expect(document.body.style.overflow).toBe("hidden");

    const panelClose = within(dialog).getByRole("button", {
      name: homeContent.nav.menuClose,
    });
    await waitFor(() => {
      expect(panelClose).toHaveFocus();
    });

    await user.keyboard("{Escape}");

    await waitFor(() => {
      expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
    });
    expect(menuButton).toHaveFocus();
    expect(document.body.style.overflow).toBe(initialOverflow);
  });

  it("restitue le focus au bouton Menu après fermeture par clic overlay", async () => {
    const user = userEvent.setup();
    render(<DrawerHarness />);

    const menuButton = screen.getByRole("button", { name: homeContent.nav.menuOpen });
    await user.click(menuButton);

    const closeTargets = screen.getAllByRole("button", {
      name: homeContent.nav.menuClose,
    });
    await user.click(closeTargets[0]!);

    await waitFor(() => {
      expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
    });
    expect(menuButton).toHaveFocus();
  });
});
