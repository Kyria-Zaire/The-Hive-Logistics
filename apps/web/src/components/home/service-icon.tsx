import { homeContent } from "@/lib/content/home";

type ServiceIconName = (typeof homeContent.services.items)[number]["icon"];

export function ServiceIcon({ name }: { name: ServiceIconName }) {
  const commonProps = {
    width: 24,
    height: 24,
    viewBox: "0 0 24 24",
    fill: "none",
    stroke: "currentColor",
    strokeWidth: 1.5,
    strokeLinecap: "round" as const,
    strokeLinejoin: "round" as const,
    "aria-hidden": true,
  };

  switch (name) {
    case "route":
      return (
        <svg {...commonProps}>
          <path d="M4 19c2.5-7 5-11 8-11s5 4 8 11" />
          <circle cx="4" cy="19" r="1.5" />
          <circle cx="20" cy="19" r="1.5" />
        </svg>
      );
    case "fleet":
      return (
        <svg {...commonProps}>
          <rect x="3" y="5" width="18" height="14" rx="2" />
          <path d="M7 9h10M7 13h4M15 13h2" />
        </svg>
      );
    case "package":
      return (
        <svg {...commonProps}>
          <path d="m4 7 8-4 8 4v10l-8 4-8-4Z" />
          <path d="m4 7 8 4 8-4M12 11v10" />
        </svg>
      );
    case "sparkle":
      return (
        <svg {...commonProps}>
          <path d="m12 3 1.4 5.6L19 10l-5.6 1.4L12 17l-1.4-5.6L5 10l5.6-1.4Z" />
          <path d="m19 16 .5 2.5L22 19l-2.5.5L19 22l-.5-2.5L16 19l2.5-.5Z" />
        </svg>
      );
  }
}
