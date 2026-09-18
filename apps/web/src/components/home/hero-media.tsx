import { getImageProps } from "next/image";

const HERO_DESKTOP = {
  src: "/images/hero/hero-desktop.jpg",
  width: 7999,
  height: 4499,
} as const;

const HERO_MOBILE = {
  src: "/images/hero/hero-mobile.jpg",
  width: 2800,
  height: 3500,
} as const;

/** Art direction: one optimized srcSet per breakpoint, a single download per viewport. */
export function HeroMedia() {
  // priority only disables lazy loading here: fetchPriority is a separate prop in next/image.
  const common = {
    alt: "",
    sizes: "100vw",
    priority: true,
    fetchPriority: "high" as const,
  };
  const {
    props: { srcSet: desktopSrcSet },
  } = getImageProps({ ...common, ...HERO_DESKTOP });
  const {
    props: { srcSet: mobileSrcSet, ...imgProps },
  } = getImageProps({ ...common, ...HERO_MOBILE });

  return (
    <div
      className="absolute inset-0 overflow-hidden bg-[var(--bg-primary)]"
      aria-hidden="true"
    >
      <picture className="block size-full">
        <source media="(min-width: 768px)" srcSet={desktopSrcSet} />
        <source srcSet={mobileSrcSet} />
        <img {...imgProps} alt="" className="size-full object-cover" />
      </picture>
    </div>
  );
}
